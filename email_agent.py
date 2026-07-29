import os
import sys
import io
import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk
from datetime import datetime
from dotenv import load_dotenv
import ollama
import pyttsx3
import threading
import re
import urllib.parse # <-- Added to safely format mailto links

# ==========================================
# MEMORY SYSTEM SETUP
# ==========================================
DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\AI_Agent_Memory"
DRAFT_MEMORY_FILE = os.path.join(DESKTOP_PATH, "sending_email_memory.json")
SWEEP_MEMORY_FILE = os.path.join(DESKTOP_PATH, "sweep_agent_memory_bank.json")

def initialize_memory():
    if not os.path.exists(DESKTOP_PATH):
        os.makedirs(DESKTOP_PATH)
        print(f"DEBUG: Created folder at {DESKTOP_PATH}")
    
    for file_path in [DRAFT_MEMORY_FILE, SWEEP_MEMORY_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)
            print(f"DEBUG: Created file at {file_path}")

initialize_memory()

def save_memory(task, outcome, is_success, user_prompt="", generated_body=""):
    target_file = SWEEP_MEMORY_FILE if "Sweep" in task else DRAFT_MEMORY_FILE
    
    try:
        with open(target_file, 'r+') as f:
            memory = json.load(f)
            memory.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "task": task,
                "userprompt": user_prompt,
                "generated_body": generated_body,
                "outcome": outcome,
                "success": is_success
            })
            f.seek(0)
            json.dump(memory, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"Failed to save memory: {e}")

def get_memory_context(task_keyword):
    """
    RAG Integration: Reads the memory JSON files and extracts the 5 most recent 
    corrective lessons to inject into the AI's prompt before it runs.
    """
    target_file = SWEEP_MEMORY_FILE if "Sweep" in task_keyword else DRAFT_MEMORY_FILE
    try:
        if not os.path.exists(target_file):
            return ""
        with open(target_file, 'r') as f:
            memory = json.load(f)

        corrections = []
        for entry in memory:
            if f"{task_keyword} Corrective Learning" in entry.get("task", ""):
                corrections.append(entry.get("outcome", ""))

        if not corrections:
            return ""

        recent_corrections = corrections[-5:]
        
        context_string = "\nCRITICAL PREVIOUS USER FEEDBACK TO APPLY:\n"
        for text in recent_corrections:
            clean_text = text.replace("Correction: ", "")
            context_string += f"- {clean_text}\n"
        
        return context_string + "\n"
    except Exception as e:
        print(f"DEBUG: Failed to load memory context: {e}")
        return ""

# ==========================================
# TEXT-TO-SPEECH HELPER (Non-Blocking)
# ==========================================
def read_aloud(text):
    def speak():
        try:
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 25) 
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    threading.Thread(target=speak, daemon=True).start()

# ==========================================
# INSTRUCTION LOADER
# ==========================================
def get_agent_instructions():
    return """
    Email Agent System Manual:
    - MANDATORY FORMAT: You MUST begin your response with these exact headers:
      TO: [recipient email]
      SUBJECT: [email subject]
      BODY: [email content]
    - If you do not have the recipient email, use: TO: [RECIPIENT_MISSING]
    - Role: Personal Email Assistant for Daniel Blades.
    - Tone: Technical, direct, and professional. 
    """

# ==========================================
# SETUP & CREDENTIALS
# ==========================================
load_dotenv()
yahoo_email = os.getenv("YAHOO_EMAIL")
yahoo_app_password = os.getenv("YAHOO_APP_PASSWORD")
ai_api_key = os.getenv("AI_API_KEY")

# ==========================================
# GUI FUNCTIONS
# ==========================================
def review_draft_gui(to_address, subject, body, user_prompt="", raw_ai_reply=""):
    root = tk.Tk()
    root.title("Review Email Draft")
    result = {"approved": False, "to": to_address, "subject": subject, "body": body}
    
    tk.Label(root, text="To:", font=("Arial", 10, "bold")).pack(pady=(5,0))
    to_entry = tk.Entry(root, width=50)
    to_entry.insert(0, to_address)
    to_entry.pack(padx=20)
    
    tk.Label(root, text="Subject:", font=("Arial", 10, "bold")).pack(pady=(5,0))
    sub_entry = tk.Entry(root, width=50)
    sub_entry.insert(0, subject)
    sub_entry.pack(padx=20)
    
    tk.Label(root, text="Body:").pack(pady=(5,0))
    body_text = scrolledtext.ScrolledText(root, width=50, height=12)
    body_text.insert(tk.INSERT, body)
    body_text.pack(padx=20, pady=5)
    
    def approve():
        result["approved"] = True
        result["to"] = to_entry.get()
        result["subject"] = sub_entry.get()
        result["body"] = body_text.get("1.0", tk.END).strip()
        root.destroy()
        
    def corrective_feedback():
        feedback = simpledialog.askstring("Corrective Learning", "Why was this draft incorrect? (Feedback will be saved to memory):", parent=root)
        if feedback:
            save_memory("Draft Corrective Learning", f"Correction: {feedback}", False, user_prompt, raw_ai_reply)
            print("Feedback saved to draft memory bank.")
            messagebox.showinfo("Memory Saved", "Feedback saved to memory! You can now manually edit the draft and send, or discard it.", parent=root)
    
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    
    tk.Button(
        btn_frame, text="✅ Send Email", command=approve,
        bg="#10B981", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        btn_frame, text="🧠 Corrective Learning", command=corrective_feedback,
        bg="#F59E0B", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        btn_frame, text="❌ Discard", command=root.destroy,
        bg="#EF4444", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=tk.LEFT, padx=5)
    
    root.mainloop()
    return result if result["approved"] else None

def review_sweep_gui(email_list, junk_indices, ai_reply=""):
    root = tk.Tk()
    root.title("Inbox Sweep Review")
    root.geometry("650x450")
    root.update()
    
    tk.Label(root, text="AI Scan Results", font=("Helvetica", 12, "bold")).pack(pady=10)
    tk.Label(root, text="Checked items are flagged as JUNK/SPAM.", fg="red").pack()
    
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both", padx=10, pady=10)
    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        if event.num == 4: canvas.yview_scroll(-1, "units")
        elif event.num == 5: canvas.yview_scroll(1, "units")
        else: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    check_vars = {}
    for idx, mail_item in enumerate(email_list):
        is_junk = 1 if (idx + 1) in junk_indices else 0
        var = tk.IntVar(value=is_junk)
        check_vars[idx + 1] = var
        display_text = f"[{idx+1}] {mail_item['sender']} | {mail_item['subject']}"
        cb = tk.Checkbutton(scrollable_frame, text=display_text, variable=var, font=("Helvetica", 10), anchor="w")
        cb.pack(fill="x", padx=5, pady=2)
        
    result = {"approved": False, "final_junk_indices": []}
    
    def approve_sweep():                                                 
        result["approved"] = True
        result["final_junk_indices"] = [i for i, var in check_vars.items() if var.get() == 1]
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        root.destroy()                                                   
        
    def corrective_feedback():
        feedback = simpledialog.askstring("Corrective Learning", "Why was this scan incorrect? (e.g. 'Missed newsletter'):", parent=root)
        if feedback:
            context = json.dumps([{"sender": e["sender"], "subject": e["subject"]} for e in email_list])[:500]
            save_memory("Sweep Corrective Learning", f"Correction: {feedback}", False, context, ai_reply)
            print("Feedback saved to sweep memory bank.")
            messagebox.showinfo("Memory Saved", "Feedback saved to memory! Please check the correct boxes and click 'Approve & Archive'.", parent=root)
        
    def cancel_sweep():
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        root.destroy()
        
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    
    tk.Button(
        btn_frame, text="✅ Approve & Archive", command=approve_sweep, 
        bg="#10B981", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        btn_frame, text="🧠 Corrective Learning", command=corrective_feedback, 
        bg="#F59E0B", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        btn_frame, text="❌ Cancel/Keep All", command=cancel_sweep, 
        bg="#EF4444", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5
    ).pack(side=tk.LEFT, padx=5)
    
    root.mainloop()
    return result["final_junk_indices"] if result["approved"] else None

def ask_batch_size():
    root = tk.Tk()
    root.withdraw()
    count = simpledialog.askinteger("Email Sweeper", "How many recent emails to scan?", initialvalue=10, minvalue=1, maxvalue=100, parent=root)
    root.destroy()
    return count if count is not None else 10

# ==========================================
# AUTO-SWEEP LOOP
# ==========================================
def auto_sweep_loop():
    print("Starting continuous auto-sweep...")
    try:
        while True:
            mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
            mail.login(yahoo_email, yahoo_app_password)
            mail.select("INBOX")
            _, messages = mail.uid('SEARCH', None, "UNSEEN")
            if not messages[0]:
                print("No more unread emails. Stopping.")
                mail.logout()
                save_memory("Auto-Sweep", "No more unread emails found.", True, "Auto-Sweep Triggered", "")
                break
            
            email_ids = messages[0].split()[:30]
            emails_metadata = []
            for e_id in email_ids:
                _, msg_data = mail.uid('FETCH', e_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                def safe_decode(header_value):
                    try:
                        parts = decode_header(header_value)
                        decoded_parts = []
                        for part, encoding in parts:
                            if isinstance(part, bytes):
                                encoding = encoding if encoding and encoding.lower() != 'unknown-8bit' else 'utf-8'
                                decoded_parts.append(part.decode(encoding, errors='replace'))
                            else:
                                decoded_parts.append(str(part))
                        return "".join(decoded_parts)
                    except Exception:
                        return "Unparseable Header"

                sender = safe_decode(msg.get("From", "Unknown"))
                subject = safe_decode(msg.get("Subject", "No Subject"))
                
                # --- NEW LOGIC: Intercept Approval/Denial Responses ---
                subject_upper = subject.upper()
                if "APPROVE:" in subject_upper:
                    save_memory("Approval Tracking", f"Recipient APPROVED: {subject}", True, "Track Approval", sender)
                    print(f"Logged APPROVAL from {sender}")
                elif "DENY:" in subject_upper:
                    save_memory("Approval Tracking", f"Recipient DENIED: {subject}", False, "Track Approval", sender)
                    print(f"Logged DENIAL from {sender}")
                
                emails_metadata.append({"uid": e_id.decode(), "sender": sender, "subject": subject})
            
            uid_string = ",".join([m['uid'] for m in emails_metadata])
            print(f"Trashing {len(emails_metadata)} unread emails...")
            mail.uid('COPY', uid_string, 'Trash')
            mail.uid('STORE', uid_string, '+FLAGS (\\Deleted)')
            mail.expunge()
            mail.logout()
            
            sweep_context = json.dumps([{"sender": m["sender"], "subject": m["subject"]} for m in emails_metadata])
            save_memory("Auto-Sweep", f"Trashed {len(emails_metadata)} emails.", True, sweep_context, f"Trashed UIDs: {uid_string}")
            time.sleep(2)
    except Exception as e:
        save_memory("Auto-Sweep", f"Error: {e}", False, "Auto-Sweep Failure", "")
        print(f"Error during auto-sweep: {e}")

# ==========================================
# DRAFTING LOGIC
# ==========================================
def draft_and_send_email(user_prompt, is_auto=False):
    memory_rules = get_memory_context("Draft")
    ai_instructions = f"{get_agent_instructions()}\n{memory_rules}\nUser Request: '{user_prompt}'"
    
    try:
        response = ollama.chat(model='huihui_ai/qwen2.5-abliterate:7b-instruct', messages=[{'role': 'user', 'content': ai_instructions}])
        ai_reply = response['message']['content'].strip()
    except Exception as e:
        save_memory("Draft Email", f"Error: {e}", False, user_prompt, "")
        return

    to_match = re.search(r"TO:\s*(.*)", ai_reply, re.IGNORECASE)
    sub_match = re.search(r"SUBJECT:\s*(.*)", ai_reply, re.IGNORECASE)
    body_match = re.search(r"BODY:\s*(.*)", ai_reply, re.IGNORECASE | re.DOTALL)
    
    to_address = to_match.group(1).strip() if (to_match and to_match.group(1).strip()) else "bladesdaniel@yahoo.com" 
    subject = sub_match.group(1).strip() if (sub_match and sub_match.group(1).strip()) else "Follow-up on Project"
    body = body_match.group(1).strip() if (body_match and body_match.group(1).strip()) else ai_reply

    if not is_auto:
        final_email_data = review_draft_gui(to_address, subject, body, user_prompt, ai_reply)
        if final_email_data: 
            send_via_to = final_email_data["to"]
            send_via_subject = final_email_data["subject"]
            send_via_body = final_email_data["body"]
            send_via_smtp(send_via_to, send_via_subject, send_via_body)
            save_memory("Draft Email", "Approved and Sent", True, user_prompt, send_via_body)
    else: 
        send_via_smtp(to_address, subject, body)
        save_memory("Draft Email", "Auto-Sent", True, user_prompt, ai_reply)

def send_via_smtp(to_address, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = yahoo_email
        msg['To'] = to_address
        msg['Subject'] = subject
        
        formatted_body = body.replace('\n', '<br>')
        
        # --- NEW LOGIC: URL Encoded mailto: links ---
        safe_subject = urllib.parse.quote(subject)
        approve_link = f"mailto:{yahoo_email}?subject=APPROVE:%20{safe_subject}&body=I%20approve%20this."
        deny_link = f"mailto:{yahoo_email}?subject=DENY:%20{safe_subject}&body=I%20deny%20this."
        
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f9fafb; padding: 40px 20px; text-align: center;">
            <div style="background-color: #ffffff; max-width: 600px; margin: 0 auto; border-radius: 12px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); padding: 32px; text-align: left; color: #1f2937; line-height: 1.6;">
                <div style="font-size: 16px; margin-bottom: 30px;">
                    {formatted_body}
                </div>
                <div style="text-align: center; margin-top: 30px; padding-top: 24px; border-top: 1px solid #f3f4f6;">
                    <a href="{approve_link}" style="display: inline-block; padding: 12px 28px; margin: 8px; border-radius: 6px; text-decoration: none; font-weight: bold; color: #ffffff; background-color: #10b981; font-size: 16px; border: 1px solid #059669;">✅ Approve</a>
                    <a href="{deny_link}" style="display: inline-block; padding: 12px 28px; margin: 8px; border-radius: 6px; text-decoration: none; font-weight: bold; color: #ffffff; background-color: #ef4444; font-size: 16px; border: 1px solid #dc2626;">❌ Deny</a>
                </div>
                <div style="margin-top: 20px; font-size: 12px; color: #9ca3af; text-align: center;">
                    Please click an option above to log your response. A new email draft will open. Just hit send!
                </div>
            </div>
        </div>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as server:
            server.login(yahoo_email, yahoo_app_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e: print(f"Failed to send email: {e}")

def sweep_inbox(is_auto=False):
    if is_auto:
        auto_sweep_loop()
        return

    batch_size = ask_batch_size()
    try:
        # --- PHASE 1: Fetch and Disconnect ---
        mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
        mail.login(yahoo_email, yahoo_app_password)
        mail.select("INBOX")
        _, messages = mail.uid('SEARCH', None, "UNSEEN")
        if not messages[0]:
            print("No unseen emails to sweep.")
            mail.logout()
            return
        
        email_ids = messages[0].split()[-batch_size:]
        emails_metadata = []

        for e_id in email_ids:
            _, msg_data = mail.uid('FETCH', e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = "".join(
                        p[0].decode(p[1] or "utf-8", "ignore") if isinstance(p[0], bytes) else str(p[0]) 
                        for p in decode_header(msg.get("Subject", "No Subject"))
                    )
                    sender = "".join(
                        p[0].decode(p[1] or "utf-8", "ignore") if isinstance(p[0], bytes) else str(p[0]) 
                        for p in decode_header(msg.get("From", "Unknown"))
                    )
                    body_content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body_content = part.get_payload(decode=True).decode(errors="ignore")[:300]
                                break
                    else: body_content = msg.get_payload(decode=True).decode(errors="ignore")[:300]
                    emails_metadata.append({"uid": e_id.decode(), "sender": sender, "subject": subject, "body": body_content})
        
        # Disconnect so Yahoo doesn't time out while the GUI is open
        mail.logout()

        # --- PHASE 2: AI Processing & GUI ---
        compiled_text = "".join([f"[{idx}] From: {item['sender']}\nSubject: {item['subject']}\nBody: {item['body']}\n---\n" for idx, item in enumerate(emails_metadata, 1)])
        
        memory_rules = get_memory_context("Sweep")
        ai_combined_instructions = (
            "Analyze the following emails. For each email, classify it as 'JUNK' or 'URGENT'.\n"
            "Return JSON output: {\"junk\": [indices], \"urgent\": [indices]}\n\n"
            f"{memory_rules}"
            f"Emails:\n{compiled_text}"
        )

        response = ollama.chat(model='huihui_ai/qwen2.5-abliterate:7b-instruct', messages=[{'role': 'user', 'content': ai_combined_instructions}])
        ai_reply = response['message']['content'].strip()
        
        try:
            clean_reply = ai_reply[ai_reply.find('{'):ai_reply.rfind('}')+1]
            data = json.loads(clean_reply)
            junk_indices, urgent_indices = data.get("junk", []), data.get("urgent", [])
        except: junk_indices, urgent_indices = [], []

        final_junk_indices = review_sweep_gui(emails_metadata, junk_indices, ai_reply)
        
        # --- PHASE 3: Reconnect and Delete ---
        if final_junk_indices:
            # Re-establish the connection to execute the deletion
            mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com")
            mail.login(yahoo_email, yahoo_app_password)
            mail.select("INBOX")
            
            uid_string = ",".join([emails_metadata[i-1]['uid'] for i in final_junk_indices])
            mail.uid('COPY', uid_string, 'Trash')
            mail.uid('STORE', uid_string, '+FLAGS (\\Deleted)')
            mail.expunge()
            
            sweep_context = json.dumps([{"sender": e["sender"], "subject": e["subject"]} for e in emails_metadata])
            save_memory("Manual Sweep", f"Trashed {len(final_junk_indices)} emails.", True, sweep_context, ai_reply)
            mail.logout()
            
    except Exception as e: 
        save_memory("Manual Sweep", f"Error: {e}", False, "Sweep Attempt", "")
        print(f"Error: {e}")

def arg_parse_check(): # Placeholder for structural integrity
    pass

if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:])
    input_lower = user_input.lower().strip()
    
    is_auto = "--auto" in input_lower or input_lower in ["auto sweep", "sweep auto"]
    is_sweep_cmd = "--sweep" in input_lower or input_lower in ["sweep", "auto sweep", "sweep auto"]

    clean_input = user_input.replace("--auto", "").replace("--sweep", "").strip()

    if is_sweep_cmd:
        sweep_inbox(is_auto=is_auto)
    elif clean_input and not is_sweep_cmd: 
        draft_and_send_email(clean_input, is_auto=is_auto)
    else: 
        print("Usage: python script.py 'your message' OR python script.py sweep")

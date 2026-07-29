import os
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import subprocess
from google import genai
import speech_recognition as sr
import time
import json
import pyttsx3  # Make sure to run: pip install pyttsx3

# ==========================================
# 1. THE WIRING HARNESS (IMPORTS)
# ==========================================
from link_to_agent import generate_code, audit_code, get_ceo_routing  # Cleaned up old get_ceo_routing import
from ai_model_router import get_model_for_task  # Moved to top wiring harness for consistency
from software_engineer import software_engineer_agent
from red_team_hacker import red_team_hacker
from graphic_designer import graphic_designer_agent
from cybersecurity_auditor import cybersecurity_auditor
from security_auditor import get_live_system_health, security_auditor
from developer_sec_ops import run_dev_sec_ops_pipeline 
from flask import Flask, request
import logging

# ==========================================
# 2. GLOBAL STATE & UI LOGGER
# ==========================================
app_state = {'selected_agent': None, 'selected_name': None, 'chat_history': None, 'root': None, 'auto_sweep_process': None}

def log_to_chat(sender, message, color="#00ff00"):
    """Safely pushes text from background threads into the Tkinter GUI."""
    root = app_state.get('root')
    chat = app_state.get('chat_history')
    
    if not root or not chat:
        print(f"[{sender}] {message}") 
        return

    def append():
        chat.config(state=tk.NORMAL)
        chat.insert(tk.END, f"[{sender}]\n", "sender_tag")
        chat.insert(tk.END, f"{message}\n\n", "message_tag")
        chat.tag_config("sender_tag", foreground="#00aaff", font=("Courier", 9, "bold"))
        chat.tag_config("message_tag", foreground=color)
        chat.see(tk.END)
        chat.config(state=tk.DISABLED)

    root.after(0, append)

# ==========================================
# 2.5. WEBHOOK LISTENER (FLASK SERVER)
# ==========================================
webhook_app = Flask(__name__)
# Suppress normal Flask terminal output to keep your console clean
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@webhook_app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Grab the raw text sent by your PowerShell script
    payload = request.get_data(as_text=True)
    
    # Send an alert to the Tkinter UI
    log_to_chat("System", "Incoming Network Log Detected!", "#ffaa00")
    log_to_chat("NetCheck Payload", payload, "#00ff00")
    
    return "Log received by 8-Agent System", 200

def start_webhook_server():
    webhook_app.run(host="127.0.0.1", port=5000, use_reloader=False)

# ==========================================
# 3. UNIVERSAL APPROVAL GUI (WITH TTS)
# ==========================================
def universal_approval_gui(agent_name, proposed_action_summary, patch_code=""):
    """
    Pops up a dark-mode review window showing which agent is acting and what they want to do.
    Includes Text-to-Speech and Smart JSON parsing.
    Returns True if the user clicks 'Approve', False if they click 'Deny'.
    """
    try:
        data = json.loads(proposed_action_summary)
        details = data.get("situation_details", "No details provided.")
        why_fix = data.get("why_fix_is_needed", "No risk analysis provided.")
        changes = data.get("proposed_changes", "No change summary provided.")
        
        display_text = f"=== SITUATION DETAILS ===\n{details}\n\n"
        display_text += f"=== WHY THIS MUST BE FIXED (THE RISK) ===\n{why_fix}\n\n"
        display_text += f"=== PROPOSED CHANGES ===\n{changes}\n\n"
        
        speech_text = f"Alert from {agent_name}. Situation Details: {details}. Why this must be fixed: {why_fix}. Proposed changes: {changes}."
    except (json.JSONDecodeError, TypeError):
        display_text = f"=== PROPOSED ACTION ===\n{proposed_action_summary}\n\n"
        speech_text = f"Approval required for {agent_name}. Proposed action: {proposed_action_summary}"

    if patch_code:
        display_text += "="*60 + "\nDEVELOPER PATCH SCRIPT PREVIEW:\n\n" + patch_code

    # Create the pop-up window
    popup = tk.Toplevel(app_state['root'])
    popup.title(f"⚠️ CEO SECURITY ALERT: {agent_name} Review Required")
    popup.geometry("850x750")
    popup.configure(bg="#1e1e1e")
    popup.attributes("-topmost", True)
    
    user_approved = tk.BooleanVar(value=False)
    
    # Text-to-Speech Function
    def read_aloud():
        def speak():
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 25) 
            engine.say(speech_text)
            engine.runAndWait()
        threading.Thread(target=speak, daemon=True).start()

    def approve():
        user_approved.set(True)
        popup.destroy()
        
    def deny():
        user_approved.set(False)
        popup.destroy()
    
    # UI Elements for the Popup
    title_label = tk.Label(popup, text=f"{agent_name.upper()} REQUESTING APPROVAL", font=("Helvetica", 16, "bold"), fg="#ff4d4d", bg="#1e1e1e")
    title_label.pack(pady=15)
    
    text_area = scrolledtext.ScrolledText(popup, wrap=tk.WORD, width=95, height=30, bg="#2d2d2d", fg="#ffffff", font=("Consolas", 10))
    text_area.insert(tk.INSERT, display_text)
    text_area.config(state=tk.DISABLED) 
    text_area.pack(pady=10, padx=20)
    
    btn_frame = tk.Frame(popup, bg="#1e1e1e")
    btn_frame.pack(pady=15)
    
    tk.Button(btn_frame, text="APPROVE & DEPLOY", width=20, bg="#28a745", fg="black", 
              font=("Helvetica", 12, "bold"), command=approve).grid(row=0, column=0, padx=20)

    tk.Button(btn_frame, text="🔊 READ ALOUD", width=20, bg="#007bff", fg="white", 
              font=("Helvetica", 12, "bold"), command=read_aloud).grid(row=0, column=1, padx=20)

    tk.Button(btn_frame, text="DENY / ABORT", width=20, bg="#dc3545", fg="black", 
              font=("Helvetica", 12, "bold"), command=deny).grid(row=0, column=2, padx=20)
    
    # Auto-read aloud when window opens
    read_aloud()
    
    # Halt the code until a button is clicked
    popup.wait_window()
    return user_approved.get()

# ==========================================
# 4. AGENT TRIGGER FUNCTIONS
# ==========================================
def trigger_email_agent(user_command):
    try:
        # Safeguard: If the command is to start the auto loop, use Popen to prevent the dashboard from freezing
        if "auto" in user_command.lower() or "loop" in user_command.lower():
            if app_state.get('auto_sweep_process') is not None and app_state['auto_sweep_process'].poll() is None:
                return "Auto Sweeper is already running in the background."
            process = subprocess.Popen([sys.executable, "email_agent.py", user_command])
            app_state['auto_sweep_process'] = process
            return "Email Agent Auto-Loop launched in the background."
        else:
            result = subprocess.run([sys.executable, "email_agent.py", user_command], capture_output=True, text=True)
            return result.stdout
    except Exception as e:
        return f"Error: {e}"

def trigger_cyber(user_command):
    try:
        return cybersecurity_auditor(user_command)
    except Exception as e:
        return f"Error: {e}"

def trigger_sec_auditor(user_command):
    try:
        live_data = get_live_system_health()
        combined_prompt = f"{live_data}\n\nUser Directive: {user_command}"
        return security_auditor(combined_prompt)
    except Exception as e:
        return f"Error: {e}"

def trigger_graphic(user_command):
    try:
        graphic_designer_agent(user_command)
        return "Graphic design process completed. Check your output folder."
    except Exception as e:
        return f"Error: {e}"

def trigger_cyber_model_route(user_command, chosen_model):
    """Fallback router function logic can expand here if other tools accept model selection parameters."""
    try:
        return cybersecurity_auditor(user_command)
    except Exception as e:
         return f"Error: {e}"

def trigger_red_team(user_command):
    try:
        return red_team_hacker(user_command)
    except Exception as e:
        return f"Error: {e}"

# APPROVED CHANGE: trigger_soft_eng now dynamically accepts and passes the chosen model string
def trigger_soft_eng(user_command, model="qwen2.5:latest"):
    try:
        return software_engineer_agent(user_command, model=model)
    except Exception as e:
        return f"Error: {e}"

# ==========================================
# 5. THE DASHBOARD ENGINE (CLICK LOGIC)
# ==========================================
def set_active(agent_ui, status_text):
    frame, avatar, name, status = agent_ui
    frame.config(bg="#4a0000", highlightbackground="#ff3333", highlightcolor="#ff3333", highlightthickness=2)
    avatar.config(bg="#4a0000")
    name.config(bg="#4a0000", fg="#ff3333")
    status.config(bg="#4a0000", text=status_text, fg="white")

def set_selected(agent_ui, status_text="Listening..."):
    frame, avatar, name, status = agent_ui
    frame.config(bg="#333333", highlightbackground="#ffffff", highlightcolor="#ffffff", highlightthickness=2)
    avatar.config(bg="#333333")
    name.config(bg="#333333", fg="white")
    status.config(bg="#333333", text=status_text, fg="#00ff00")

def set_idle(agent_ui, status_text="Idle"):
    frame, avatar, name, status = agent_ui
    frame.config(bg="#2b2b2b", highlightbackground="#444444", highlightcolor="#444444", highlightthickness=1)
    avatar.config(bg="#2b2b2b")
    name.config(bg="#2b2b2b", fg="white")
    status.config(bg="#2b2b2b", text=status_text, fg="#888888")

def execute_agent_task(ui_elements, target_key, target_name, command_text):
    target_ui = ui_elements[target_key]
    
    # APPROVED CHANGE: Intercept request and ask the centralized model router to pick its engine
    chosen_model = get_model_for_task(command_text)
    log_to_chat("CEO Router System", f"Selected running target model: {chosen_model}", "#00aaff")
    
    if target_key == 'dev_mgr':
        # ---> INTERCEPT: CEO APPROVAL REQUIRED <---
        is_approved = universal_approval_gui(
            agent_name="Dev Manager", 
            proposed_action_summary=f"The user has requested the following task:\n\n'{command_text}'\n\nDo you authorize the Developer and Auditor to spin up a continuous feedback loop and consume API resources to complete this task?"
        )
        
        if not is_approved:
            log_to_chat("SYSTEM", "❌ ACTION ABORTED BY CEO.", "red")
            set_selected(ui_elements['dev_mgr'], "Listening...")
            return

        # If approved, proceed with the pipeline
        set_active(ui_elements['dev_mgr'], "Delegating...")
        try:
            set_active(ui_elements['soft_eng'], "Looping...")
            set_active(ui_elements['sec_auditor'], "Looping...")
            
            final_approved_code = run_dev_sec_ops_pipeline(command_text)
            
            log_to_chat("Dev Manager", f"Pipeline Complete. Final Code:\n\n{final_approved_code}")
            
            set_idle(ui_elements['soft_eng']) 
            set_idle(ui_elements['sec_auditor']) 
        except Exception as e:
            log_to_chat("Dev Manager Error", str(e), "red")
            set_idle(ui_elements['soft_eng'])
            set_idle(ui_elements['sec_auditor'])

        set_selected(ui_elements['dev_mgr'], "Listening...")
        
    else:
        set_active(target_ui, "Processing...")
        output = ""
        
        if target_key == 'email':
            output = trigger_email_agent(command_text)
        elif target_key == 'cyber':
            output = trigger_cyber(command_text)
        elif target_key == 'sec_auditor':
            output = trigger_sec_auditor(command_text)
        elif target_key == 'graphic':
            output = trigger_graphic(command_text)
        elif target_key == 'red_team':
            output = trigger_red_team(command_text)
        elif target_key == 'soft_eng':
            # APPROVED CHANGE: Direct routing instruction safely appended down to execution phase
            output = trigger_soft_eng(command_text, model=chosen_model)
            
        if output:
            log_to_chat(target_name, output)
            
        set_selected(target_ui, "Listening...")

# ==========================================
# 6. THE VISUAL INTERFACE (UI)
# ==========================================
def create_dashboard():
    root = tk.Tk()
    app_state['root'] = root 
    root.title("8-Agent System")
    root.configure(bg="#1e1e1e")
    root.attributes("-topmost", True) 
    root.attributes("-alpha", 0.95)
    
    # Adjusted to roughly half size and positioned in top-right corner
    window_width = 460 
    window_height = 600 
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate right-hand corner position (with 20px padding from the edges)
    x_pos = screen_width - window_width - 20
    y_pos = 20
    
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
    
    header = tk.Label(root, text="THREAT & RESPONSE PIPELINE", font=("Courier", 10, "bold"), bg="#1e1e1e", fg="#00ff00")
    header.pack(pady=(10, 5))
    
    top_row = tk.Frame(root, bg="#1e1e1e")
    top_row.pack()
    bottom_row = tk.Frame(root, bg="#1e1e1e")
    bottom_row.pack()
    
    ui_elements = {}

    def select_agent(event, key, name):
        for k, ui in ui_elements.items():
            set_idle(ui)
        app_state['selected_agent'] = key
        app_state['selected_name'] = name
        set_selected(ui_elements[key])
        target_label.config(text=f"Talking to: [{name}]", fg="#00aaff")

    def build_agent_panel(parent, avatar_text, name_text, key):
        frame = tk.Frame(parent, bg="#2b2b2b", width=95, height=110, highlightbackground="#444444", highlightthickness=1)
        frame.pack_propagate(False) 
        frame.pack(side="left", padx=5, pady=5)
        
        avatar = tk.Label(frame, text=avatar_text, font=("Segoe UI Emoji", 26), bg="#2b2b2b")
        avatar.pack(pady=(10, 2))
        
        name = tk.Label(frame, text=name_text, font=("Courier", 7, "bold"), bg="#2b2b2b", fg="white", wraplength=90)
        name.pack()
        
        status = tk.Label(frame, text="Idle", font=("Courier", 7), bg="#2b2b2b", fg="#888888")
        status.pack(pady=(2, 0))
        
        widgets_to_bind = [frame, avatar, name, status]
        for widget in widgets_to_bind:
            widget.bind("<Button-1>", lambda e, k=key, n=name_text: select_agent(e, k, n))
            widget.config(cursor="hand2")
            
        return (frame, avatar, name, status)

    ui_elements['ceo'] = build_agent_panel(top_row, "👑", "CEO Router", 'ceo')
    ui_elements['dev_mgr'] = build_agent_panel(top_row, "👔", "Dev Manager", 'dev_mgr')
    ui_elements['email'] = build_agent_panel(top_row, "📧", "Email Agent", 'email')
    ui_elements['cyber'] = build_agent_panel(top_row, "🛡️", "Cybersecurity", 'cyber')
    
    ui_elements['sec_auditor'] = build_agent_panel(bottom_row, "📋", "Sec Auditor", 'sec_auditor')
    ui_elements['graphic'] = build_agent_panel(bottom_row, "🎨", "Graphic Design", 'graphic')
    ui_elements['red_team'] = build_agent_panel(bottom_row, "🥷", "Red Team", 'red_team')
    ui_elements['soft_eng'] = build_agent_panel(bottom_row, "💻", "Software Eng", 'soft_eng')
    
    history_frame = tk.Frame(root, bg="#1e1e1e")
    history_frame.pack(pady=10, fill="both", expand=True, padx=15)

    chat_history = scrolledtext.ScrolledText(history_frame, bg="#0d0d0d", fg="#00ff00", font=("Courier", 9), wrap=tk.WORD, height=10)
    chat_history.pack(fill="both", expand=True)
    chat_history.config(state=tk.DISABLED)
    app_state['chat_history'] = chat_history
    
    log_to_chat("SYSTEM", "8-Agent Pipeline Online. All channels open.", "#888888")
    
    comms_frame = tk.Frame(root, bg="#1e1e1e")
    comms_frame.pack(pady=(5, 5))
    
    target_label = tk.Label(comms_frame, text="Select an agent to begin...", font=("Courier", 9, "bold"), bg="#1e1e1e", fg="#00aaff")
    target_label.pack(side="top", pady=(0, 5))
    
    input_subframe = tk.Frame(comms_frame, bg="#1e1e1e")
    input_subframe.pack(side="top")

    # Adjusted width to 22 so it doesn't clip off the screen on the narrower window
    command_entry = tk.Text(input_subframe, width=22, height=3, bg="#2b2b2b", fg="white", font=("Courier", 9), insertbackground="white", wrap=tk.WORD)
    command_entry.pack(side="left", padx=(5, 5), pady=2)
    
    scrollbar = tk.Scrollbar(input_subframe, command=command_entry.yview)
    scrollbar.pack(side="left", fill="y", pady=2)
    command_entry.config(yscrollcommand=scrollbar.set)
    
    def on_mic_click():
        def listen_thread():
            mic_btn.config(text="🔴 LISTENING", bg="#ff3333", fg="white")
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                    command_entry.delete(1.0, tk.END)
                    command_entry.insert(1.0, "Speak now...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    text = recognizer.recognize_google(audio)
                    command_entry.delete(1.0, tk.END)
                    command_entry.insert(1.0, text)
                except sr.UnknownValueError:
                    command_entry.delete(1.0, tk.END)
                    command_entry.insert(1.0, "[Could not understand]")
                except sr.RequestError:
                    command_entry.delete(1.0, tk.END)
                    command_entry.insert(1.0, "[API Error]")
                except Exception as e:
                    command_entry.delete(1.0, tk.END)
                    command_entry.insert(1.0, f"[Mic Error]")
                
                mic_btn.config(text="🎤 MIC", bg="#444444", fg="white")

        threading.Thread(target=listen_thread, daemon=True).start()

    mic_btn = tk.Button(input_subframe, text="🎤 MIC", font=("Courier", 8, "bold"), bg="#444444", fg="white", command=on_mic_click)
    mic_btn.pack(side="left", padx=5)

    def on_send_command():
        cmd_text = command_entry.get(1.0, tk.END).strip()
        target_key = app_state['selected_agent']
        target_name = app_state['selected_name']
        
        if cmd_text and target_key:
            log_to_chat("CEO (You)", cmd_text, "white")
            
            if target_key == 'ceo':
                def run_router():
                    set_active(ui_elements['ceo'], "Thinking...")
                    try:
                        # APPROVED CHANGE: Intercept using synchronized router function instead of old link function
                        new_target_key = get_ceo_routing(cmd_text)
                        
                        if new_target_key in ui_elements and new_target_key != 'ceo':
                            new_target_name = ui_elements[new_target_key][2].cget("text")
                            app_state['selected_agent'] = new_target_key
                            app_state['selected_name'] = new_target_name
                            
                            log_to_chat("CEO Router", f"Routing task to: [{new_target_name}]", "#ffaa00")
                            
                            set_idle(ui_elements['ceo'])
                            set_selected(ui_elements[new_target_key])
                            target_label.config(text=f"Talking to: [{new_target_name}]", fg="#00aaff")
                            
                            execute_agent_task(ui_elements, new_target_key, new_target_name, cmd_text)
                        else:
                            log_to_chat("CEO Router Error", f"Could not route to unknown category '{new_target_key}'", "red")
                            target_label.config(text="CEO Error: Could not route task", fg="red")
                            set_selected(ui_elements['ceo'], "Listening...")
                    except Exception as e:
                        log_to_chat("CEO Router Error", str(e), "red")
                        set_selected(ui_elements['ceo'], "Listening...")
                        
                threading.Thread(target=run_router, daemon=True).start()
                
            else:
                threading.Thread(target=execute_agent_task, args=(ui_elements, target_key, target_name, cmd_text), daemon=True).start()
            
            command_entry.delete(1.0, tk.END)

    send_btn = tk.Button(input_subframe, text="▶ SEND", font=("Courier", 8, "bold"), bg="#00ff00", fg="black", command=on_send_command)
    send_btn.pack(side="left", padx=5)

    def on_test_click():
        def run_offline_test():
            for k, ui in ui_elements.items():
                set_idle(ui)
            app_state['selected_agent'] = 'dev_mgr'
            app_state['selected_name'] = 'Dev Manager'
            set_selected(ui_elements['dev_mgr'])
            target_label.config(text=f"Talking to: [Dev Manager]")
            
            log_to_chat("SYSTEM", "Initiating offline mock pipeline...", "#ffaa00")
            
            set_active(ui_elements['dev_mgr'], "Delegating...")
            time.sleep(1.5) 
            
            set_active(ui_elements['soft_eng'], "Coding...")
            log_to_chat("Software Engineer", "print('All systems nominal. Local test successful.')")
            time.sleep(1.5) 
            set_idle(ui_elements['soft_eng']) 
            
            set_active(ui_elements['sec_auditor'], "Auditing...")
            log_to_chat("Sec Auditor", "AUDIT PASSED: APPROVED. Zero internet required.")
            time.sleep(1.5) 
            set_idle(ui_elements['sec_auditor']) 

            set_selected(ui_elements['dev_mgr'], "Listening...")

        threading.Thread(target=run_offline_test, daemon=True).start()

    test_btn = tk.Button(input_subframe, text="⚙️ TEST", font=("Courier", 8, "bold"), bg="#ffaa00", fg="black", command=on_test_click)
    test_btn.pack(side="left", padx=5)

    # ==========================================
    # AUTO SWEEP CONTROL SWITCHES
    # ==========================================
    sweep_control_frame = tk.Frame(comms_frame, bg="#1e1e1e")
    sweep_control_frame.pack(side="top", pady=5)

    def set_sweep_state(is_running):
        if is_running:
            # Highlight START, dim STOP
            start_sweep_btn.config(bg="#00ff00", fg="black", relief=tk.SUNKEN)
            stop_sweep_btn.config(bg="#440000", fg="#888888", relief=tk.RAISED)
        else:
            # Highlight STOP, dim START
            start_sweep_btn.config(bg="#004400", fg="#888888", relief=tk.RAISED)
            stop_sweep_btn.config(bg="#ff3333", fg="white", relief=tk.SUNKEN)

    def on_start_sweep():
        if app_state.get('auto_sweep_process') is not None and app_state['auto_sweep_process'].poll() is None:
            log_to_chat("SYSTEM", "Auto Sweeper is already running.", "#ffaa00")
            return
            
        log_to_chat("SYSTEM", "Starting Email Auto Sweep (Every 30 Mins)...", "#28a745")
        try:
            process = subprocess.Popen([sys.executable, "email_agent.py", "auto"])
            app_state['auto_sweep_process'] = process
            set_sweep_state(True)
        except Exception as e:
            log_to_chat("SYSTEM Error", f"Failed to start Auto Sweeper: {e}", "red")

    def on_stop_sweep():
        process = app_state.get('auto_sweep_process')
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                app_state['auto_sweep_process'] = None
                log_to_chat("SYSTEM", "🛑 Email Auto Sweep halted.", "#ff4d4d")
            except Exception as e:
                log_to_chat("SYSTEM Error", f"Failed to stop Auto Sweeper: {e}", "red")
        else:
            log_to_chat("SYSTEM", "No Auto Sweeper is currently running.", "#888888")
        set_sweep_state(False)

    start_sweep_btn = tk.Button(sweep_control_frame, text="▶ START: Email Auto Sweep Every 30 Mins", font=("Courier", 8, "bold"), command=on_start_sweep)
    start_sweep_btn.pack(side="left", padx=5)

    stop_sweep_btn = tk.Button(sweep_control_frame, text="🛑 STOP: Email Auto Sweep", font=("Courier", 8, "bold"), command=on_stop_sweep)
    stop_sweep_btn.pack(side="left", padx=5)
    
    # Initialize the visual state to "Stopped" when dashboard boots up
    set_sweep_state(False)
    # ==========================================

    dial_frame = tk.Frame(root, bg="#1e1e1e")
    dial_frame.pack(side="bottom", pady=5)
    
    def update_transparency(val):
        root.attributes("-alpha", float(val))

    alpha_dial = tk.Scale(dial_frame, from_=0.2, to=1.0, resolution=0.05, orient="horizontal", bg="#1e1e1e", fg="#888888", troughcolor="#2b2b2b", highlightthickness=0, command=update_transparency, font=("Courier", 7), showvalue=0, length=100)
    alpha_dial.set(0.95)
    alpha_dial.pack(side="bottom")
    tk.Label(dial_frame, text="Opacity", bg="#1e1e1e", fg="#888888", font=("Courier", 7)).pack(side="bottom")

    # Start the webhook listener in a background thread
    threading.Thread(target=start_webhook_server, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    create_dashboard()

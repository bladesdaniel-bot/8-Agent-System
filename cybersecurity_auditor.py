import os
import json
import tkinter as tk
from tkinter import scrolledtext
import requests
from datetime import datetime

# ==========================================
# 1. LOCAL OLLAMA CONFIG
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"

# ==========================================
# 2. MEMORY SYSTEM SETUP
# ==========================================
DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\AI_Agent_Memory"
MEMORY_FILE = os.path.join(DESKTOP_PATH, "cybersecurity_memory_bank.json")

def initialize_memory():
    """Manually create the folder and file if they don't exist."""
    if not os.path.exists(DESKTOP_PATH):
        os.makedirs(DESKTOP_PATH)
        print(f"DEBUG: Created folder at {DESKTOP_PATH}")
    
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w') as f:
            json.dump([], f)
        print(f"DEBUG: Created file at {MEMORY_FILE}")

def load_past_memory():
    """Reads past memory bank logs so the agent can learn from previous mistakes."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                memory = json.load(f)
                if not memory:
                    return "No past memory recorded yet."
                # Summarize the last few entries to keep context sharp
                recent_logs = memory[-5:] 
                return json.dumps(recent_logs, indent=2)
        except Exception:
            return "Could not parse past memory."
    return "No past memory file found."

# Initialize immediately
initialize_memory()

def save_memory(task, outcome, is_success):
    with open(MEMORY_FILE, 'r+') as f:
        memory = json.load(f)
        memory.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": task,
            "outcome": outcome,
            "success": is_success
        })
        f.seek(0)
        json.dump(memory, f, indent=4)
        f.truncate()

# --- 1. THE AI AGENTS ---

def cybersecurity_auditor(ip_log):
    print("Running Cybersecurity Auditor...")
    assigned_model = os.environ.get("CEO_SELECTED_MODEL", "qwen2.5")
    
    instructions = "You are an elite Cybersecurity Auditor. Your job is to detect active hacking attempts, unauthorized access, and suspicious traffic. Be ruthless. Output your findings in clean JSON format with keys: 'threat_level', 'identified_threats' (list), and 'immediate_actions' (list)."
    prompt = f"{instructions}\n\nAnalyze this IP log for threats: {ip_log}"
    
    payload = {
        "model": assigned_model,
        "prompt": prompt,
        "stream": False,
        "format": "json" 
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get("response", "{}").strip()
    except Exception as e:
        return json.dumps({"error": f"Failed to connect: {e}"})

def general_security_auditor(system_report):
    print("Running General Security Auditor...")
    assigned_model = os.environ.get("CEO_SELECTED_MODEL", "qwen2.5")
    
    instructions = "You are a strict IT Compliance Auditor. Focus on backups, outdated software, and general policy violations. Output your findings in clean JSON format with keys: 'compliance_score', 'policy_violations' (list), and 'required_updates' (list)."
    prompt = f"{instructions}\n\nReview this system report for compliance and safety: {system_report}"
    
    payload = {
        "model": assigned_model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get("response", "{}").strip()
    except Exception as e:
        return json.dumps({"error": f"Failed to connect: {e}"})

def developer_agent(cyber_report, general_report):
    print("Deploying Developer Agent to write patches...")
    assigned_model = os.environ.get("CEO_SELECTED_MODEL", "qwen2.5")
    
    instructions = "You are a Senior Software Engineer. You receive JSON threat and compliance reports. Write secure, efficient, and well-commented Python code to patch the vulnerabilities and fix the policy violations. Output ONLY the Python code without markdown backticks."
    prompt = f"{instructions}\n\nCyber Threats: {cyber_report}\n\nCompliance Issues: {general_report}\n\nWrite a complete, safe Python script to resolve these specific issues."
    
    payload = {
        "model": assigned_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        raw_code = response.json().get("response", "")
        return raw_code.replace("```python\n", "").replace("```python", "").replace("```", "").strip()
    except Exception as e:
        return f"# Failed to generate patch locally: {e}"

def ceo_agent(cyber_report, general_report, patch_code):
    print("CEO Agent is drafting the executive summary for human review...")
    assigned_model = os.environ.get("CEO_SELECTED_MODEL", "qwen2.5")
    
    instructions = "You are the Chief Information Security Officer (CEO Agent). Review the audit reports and the developer's proposed code. Explain to the human overseer exactly what is going on. Output strictly in JSON format with three keys: 'situation_details' (what is happening), 'why_fix_is_needed' (the risk of doing nothing), and 'proposed_changes' (how the patch works). Keep descriptions punchy, professional, and clear."
    prompt = f"{instructions}\n\nCyber Threats: {cyber_report}\nCompliance Issues: {general_report}\nProposed Patch Code: {patch_code}"
    
    payload = {
        "model": assigned_model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get("response", "{}").strip()
    except Exception as e:
        return json.dumps({
            "situation_details": "Error connecting to local LLM.", 
            "why_fix_is_needed": str(e), 
            "proposed_changes": "None."
        })

# --- 2. THE GUI POP-UP WINDOW ---

def human_approval_window(ceo_summary_json, patch_code):
    try:
        data = json.loads(ceo_summary_json)
        details = data.get("situation_details", "No details provided.")
        why_fix = data.get("why_fix_is_needed", "No risk analysis provided.")
        changes = data.get("proposed_changes", "No change summary provided.")
    except (json.JSONDecodeError, TypeError):
        details = "Error: Could not parse CEO report."
        why_fix = "Unknown."
        changes = "Unknown."

    user_decision = {"approved": False}

    root = tk.Tk()
    root.title("⚠️ CEO SECURITY ALERT: Human Approval Required")
    root.geometry("850x700")
    root.configure(bg="#1e1e1e")

    def approve_action():
        user_decision["approved"] = True
        root.destroy()

    def deny_action():
        user_decision["approved"] = False
        root.destroy()

    title_label = tk.Label(root, text="SYSTEM THREAT DETECTED - REVIEW REQUIRED", font=("Helvetica", 16, "bold"), fg="#ff4d4d", bg="#1e1e1e")
    title_label.pack(pady=15)

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=95, height=30, bg="#2d2d2d", fg="#ffffff", font=("Consolas", 10))
    text_area.pack(pady=10, padx=20)
    
    safe_patch_code = patch_code if patch_code is not None else "No code generated by the AI."

    display_text = "=== SITUATION DETAILS ===\n" + details + "\n\n"
    display_text += "=== WHY THIS MUST BE FIXED (THE RISK) ===\n" + why_fix + "\n\n"
    display_text += "=== PROPOSED CHANGES ===\n" + changes + "\n\n"
    display_text += "="*60 + "\n"
    display_text += "DEVELOPER PATCH SCRIPT PREVIEW:\n\n" + safe_patch_code

    text_area.insert(tk.INSERT, display_text)
    text_area.config(state=tk.DISABLED)

    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=15)

    approve_btn = tk.Button(btn_frame, text="APPROVE & DEPLOY", width=20, bg="#28a745", fg="black", font=("Helvetica", 12, "bold"), command=approve_action)
    approve_btn.pack(side=tk.LEFT, padx=30)

    deny_btn = tk.Button(btn_frame, text="DENY & DISCARD", width=20, bg="#dc3545", fg="black", font=("Helvetica", 12, "bold"), command=deny_action)
    deny_btn.pack(side=tk.RIGHT, padx=30)

    root.mainloop()

    return user_decision["approved"]

# --- 3. EXECUTION PIPELINE ---

def read_log_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    initialize_memory()
    log_file_name = "system_logs.txt"
    health_report_name = "system_health.txt"

    print("--- INITIALIZING AGENT PIPELINE ---\n")

    real_log_data = read_log_file(log_file_name) or "Simulated Log: 192.168.1.50 failed SSH login 45 times in 2 minutes."
    real_health_data = read_log_file(health_report_name) or "Simulated Health: Daily backups skipped. Apache server running v2.4.40."

    # 1. Run the Auditors
    cyber_results = cybersecurity_auditor(real_log_data)
    general_results = general_security_auditor(real_health_data)

    # 2. Deploy the Developer to fix the found issues
    dev_patch_code = developer_agent(cyber_results, general_results)

    # 3. Deploy the CEO Agent to summarize the situation
    ceo_summary = ceo_agent(cyber_results, general_results, dev_patch_code)

    # 4. Trigger the GUI for Human Approval
    print("\n[!] Triggering CEO Approval Window...")
    is_approved = human_approval_window(ceo_summary, dev_patch_code)

    # 5. Handle the Human's Decision
    if is_approved:
        patch_filename = "auto_patch.py"
        with open(patch_filename, "w") as f:
            f.write(dev_patch_code)
        print(f"\n[SUCCESS] Fix approved! Patch script saved locally as '{patch_filename}'.")
        save_memory("Cybersecurity Audit & Patch", "Fix deployed successfully", True)
    else:
        print("\n[ABORTED] CEO / Human denied the patch. No changes were made to the system.")
        save_memory("Cybersecurity Audit & Patch", "Fix denied by human", False)

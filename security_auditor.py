import os
import sys
import platform
import psutil
import subprocess
import json
from dotenv import load_dotenv
import ollama
from datetime import datetime

# Load Credentials
load_dotenv()

# ==========================================
# MEMORY SYSTEM SETUP
# ==========================================
DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\AI_Agent_Memory"
MEMORY_FILE = os.path.join(DESKTOP_PATH, "security_auditor_memory_bank.json")

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

# ==========================================
# DIAGNOSTICS & AUDIT LOGIC
# ==========================================
def get_live_system_health():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk_path = 'C:\\' if platform.system() == "Windows" else '/'
    disk = psutil.disk_usage(disk_path)
    return f"CPU: {cpu_usage}%, RAM: {memory.percent}%, Disk: {disk.percent}%"

def run_diagnostic():
    script_path = r"C:\Users\Daniel\Scripts\NetworkTools\netcheck.ps1"
    if os.path.exists(script_path):
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], 
                                capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    return "Network script not found."

def get_instructions():
    try:
        with open("security_auditor_instructions.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Perform standard system health, network audit, and email malware/phishing scan."

def update_gui_status(status, message):
    with open("status.json", "w") as f:
        json.dump({"status": status, "message": message}, f)

def security_auditor(email_payload_path=None):
    hw_data = get_live_system_health()
    net_data = run_diagnostic()
    instructions = get_instructions()
    
    # Load email data if provided
    email_data = "No emails to scan."
    if email_payload_path and os.path.exists(email_payload_path):
        with open(email_payload_path, "r", encoding="utf-8") as f:
            email_data = f.read()
    
    # --- MEMORY INJECTION ---
    past_lessons = load_past_memory()
    
    # Analyze data with AI using local Ollama model
    prompt = (
        f"Instructions: {instructions}\n\n"
        f"--- PAST MEMORY & LESSONS LEARNED ---\n{past_lessons}\n\n"
        f"System Hardware: {hw_data}\n"
        f"Network Status: {net_data}\n"
        f"Email Data to Audit: {email_data}\n\n"
        "Analyze the system health and the provided emails for malware, phishing attempts, or suspicious links."
    )

    try:
        response = ollama.chat(
            model="hf.co/jiunsong/supergemma4-26b-uncensored-gguf-v2:latest",
            messages=[{'role': 'user', 'content': prompt}]
        )
        analysis = response['message']['content']
        
        # Determine Status
        is_critical = "CRITICAL" in analysis or "MALWARE" in analysis or "PHISHING" in analysis or "BLOCKED" in net_data
        
        if is_critical:
            update_gui_status("critical", "Security or Network Alert Detected")
            save_memory("System Security Audit", analysis, False)
        else:
            update_gui_status("healthy", "System and Email Security Nominal")
            save_memory("System Security Audit", analysis, True)
            
        return analysis
    except Exception as e:
        error_msg = f"Failed to connect: {e}"
        save_memory("System Security Audit", error_msg, False)
        return error_msg

if __name__ == "__main__":
    # Check if a payload file was passed via command line
    payload_arg = sys.argv[1] if len(sys.argv) > 1 else None
    print(security_auditor(payload_arg))

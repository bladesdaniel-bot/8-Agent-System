import os
import time
import requests
import json
from datetime import datetime

# ==========================================
# 1. LOCAL OLLAMA CONFIG
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"

# ==========================================
# 2. MEMORY SYSTEM SETUP
# ==========================================
DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\AI_Agent_Memory"
MEMORY_FILE = os.path.join(DESKTOP_PATH, "developer_sec_ops_memory_bank.json")

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
# 3. AGENT INSTRUCTIONS (SYSTEM PROMPTS)
# ==========================================
dev_instructions = """
You are an expert Senior Python Developer. 
Your job is to write clean, efficient, and well-commented Python code based on the user's request or an auditor's feedback. 
Output ONLY the raw code. Do not include any conversational text, greetings, or explanations.
"""

auditor_instructions = """
You are a strict, uncompromising Cybersecurity Auditor and QA Tester. 
Your job is to review the provided Python code. 
1. Identify any security vulnerabilities (like exposed API keys or injection flaws).
2. Point out any syntax bugs or inefficiencies.
3. If the code is flawless, simply reply ONLY with exactly: 'AUDIT PASSED: APPROVED.'
4. If it has issues, provide a bulleted list of the exact problems found. Do not rewrite the code for them.
"""

# ==========================================
# 4. CORE FUNCTION (PIPELINE)
# ==========================================
def run_dev_sec_ops_pipeline(task):
    """
    Takes a coding task, runs it through the Developer and Auditor loop locally,
    and returns the final approved Python code.
    """
    max_revisions = 3
    revision_count = 0
    audit_passed = False
    
    # --- MEMORY INJECTION ---
    past_lessons = load_past_memory()
    current_prompt = f"--- PAST MEMORY & LESSONS LEARNED ---\n{past_lessons}\n\n--- CURRENT TASK ---\n{task}"
    
    final_code = ""

    assigned_model = os.environ.get("CEO_SELECTED_MODEL", "qwen2.5")

    while revision_count < max_revisions and not audit_passed:
        print(f"\n👨‍💻 DEVELOPER AGENT (Iteration {revision_count + 1}): Writing code on model [{assigned_model}]...")
        
        # 1. Developer Drafts Code
        dev_payload = {
            "model": assigned_model,
            "prompt": f"{dev_instructions}\n\n{current_prompt}",
            "stream": False,
            "options": {"temperature": 0.2}
        }
        
        try:
            dev_response = requests.post(OLLAMA_URL, json=dev_payload)
            draft_code = dev_response.json().get("response", "")
        except Exception as e:
            print(f"Developer Agent Error: {e}")
            draft_code = f"# Error generating code: {e}"
            
        draft_code = draft_code.replace("```python\n", "").replace("```python", "").replace("```", "").strip()

        # 2. Auditor Reviews Code
        print(f"\n🕵️‍♂️ AUDITOR AGENT: Inspecting code for vulnerabilities and bugs...")
        auditor_payload = {
            "model": assigned_model,
            "prompt": f"{auditor_instructions}\n\nCode to Review:\n{draft_code}",
            "stream": False
        }
        
        try:
            auditor_response = requests.post(OLLAMA_URL, json=auditor_payload)
            audit_report = auditor_response.json().get("response", "").strip()
        except Exception as e:
            print(f"Auditor Agent Error: {e}")
            audit_report = f"Error performing audit: {e}"

        # 3. Check for Approval
        if "AUDIT PASSED: APPROVED" in audit_report.upper():
            audit_passed = True
            final_code = draft_code
            print("\n✅ SUCCESS: Code passed all security and QA checks!")
            save_memory(task, "Audit passed successfully", True)
        else:
            print(f"\n⚠️ ISSUES FOUND: Sending back to the Developer...")
            current_prompt = f"Original Task: {task}\n\nHere is your previous draft:\n{draft_code}\n\nThe Auditor found these issues. Fix them:\n{audit_report}"
            revision_count += 1
            time.sleep(1)

    if not audit_passed:
        print("\n❌ FAILED: Maximum revisions reached.")
        final_code = draft_code
        save_memory(task, "Maximum revisions reached without approval", False)

    return final_code

# ==========================================
# 5. EXECUTION BLOCK
# ==========================================
if __name__ == "__main__":
    initialize_memory()
    print("======================================")
    print("DEV-SEC-OPS TEAM INITIALIZED (LOCAL MODE)")
    print("======================================\n")

    user_task = input("What do you want the Developer to build? (e.g., 'A script to scrape weather data'): ")
    completed_code = run_dev_sec_ops_pipeline(user_task)

    print("\n======================================")
    print("FINAL DELIVERABLE")
    print("======================================\n")
    print(completed_code)

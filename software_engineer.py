import os
import requests
import subprocess
from datetime import datetime
import json
import re

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
CONDA_PATH = r"C:\Users\blade\anaconda3\Scripts\conda.exe"
PYTHON_EXE = r"C:\Users\blade\anaconda3\python.exe" 
MAX_RETRIES = 3

# --- Memory System Setup ---
DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\AI_Agent_Memory"
MEMORY_FILE = os.path.join(DESKTOP_PATH, "software_engineer_memory_bank.json")
DELIVERABLES_PATH = r"C:\Users\blade\OneDrive\Desktop\Completed_Coding_Projects"

def initialize_memory():
    """Manually create the folder and file if they don't exist."""
    if not os.path.exists(DESKTOP_PATH):
        os.makedirs(DESKTOP_PATH)
        print(f"DEBUG: Created folder at {DESKTOP_PATH}")
        
    if not os.path.exists(DELIVERABLES_PATH):
        os.makedirs(DELIVERABLES_PATH)
        print(f"DEBUG: Created deliverables folder at {DELIVERABLES_PATH}")
    
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w') as f:
            json.dump([], f)
        print(f"DEBUG: Created file at {MEMORY_FILE}")

def load_past_memory(current_prompt, limit=5):
    """Reads past memory and returns entries most similar to the current prompt."""
    if not os.path.exists(MEMORY_FILE):
        return "No past memory file found."
        
    try:
        with open(MEMORY_FILE, 'r') as f:
            memory = json.load(f)
            if not memory:
                return "No past memory recorded yet."
            
            # Helper to extract meaningful keywords
            def get_keywords(text):
                words = set(re.findall(r'\b\w+\b', text.lower()))
                stop_words = {"write", "a", "to", "the", "in", "for", "and", "is", "script", "python", "create", "make"}
                return words - stop_words
            
            prompt_keywords = get_keywords(current_prompt)
            
            # Score each memory entry based on keyword overlap
            for entry in memory:
                entry_keywords = get_keywords(entry.get("task", ""))
                entry["relevance"] = len(prompt_keywords.intersection(entry_keywords))
            
            # Sort by relevance (highest first), then fallback to most recent timestamp
            memory.sort(key=lambda x: (x.get("relevance", 0), x.get("timestamp", "")), reverse=True)
            
            relevant_logs = memory[:limit]
            
            # Remove the temporary score before feeding to the LLM
            for log in relevant_logs:
                log.pop("relevance", None)
                
            return json.dumps(relevant_logs, indent=2)
            
    except Exception:
        return "Could not parse past memory."
    
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

# --- Logging & Tools ---
def log_new_file(filename):
    manifest_path = os.path.join(DELIVERABLES_PATH, "master_manifest.txt")
    with open(manifest_path, "a") as f:      
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Created: {filename}\n")

def log_agency_action(agent_name, action, details):
    audit_path = os.path.join(DELIVERABLES_PATH, "agency_audit_trail.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(audit_path, "a") as f:      
        f.write(f"[{timestamp}] Agent: {agent_name} | Action: {action} | Details: {details}\n")

def read_file_content(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read()
    return None

def execute_and_verify(code, filename="generated_task.py"):
    with open(filename, "w") as f:
        f.write(code)
    log_new_file(filename)
    try:
        result = subprocess.run([PYTHON_EXE, "-m", "py_compile", filename], capture_output=True, text=True)
        return (True, "Code passed syntax check.") if result.returncode == 0 else (False, result.stderr)
    except Exception as e:
        return False, str(e)

def run_background_script(filename):
    script_path = os.path.abspath(filename)
    command = [PYTHON_EXE, script_path]
    try:
        # Blocking run to capture stdout and stderr, shell=True removed for list command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            log_agency_action("Software Engineer", "Execute", f"Ran {filename} successfully")
            return f"Execution Success:\n{result.stdout}"
        else:
            log_agency_action("Software Engineer", "Execute Error", f"{filename} returned code {result.returncode}")
            return f"Execution Failed:\n{result.stderr}"
    except Exception as e:
        return f"Execution Exception: {str(e)}"

def check_and_install_dependencies():
    print(f"[Software Engineer] Verifying dependencies...")
    install_cmd = [PYTHON_EXE, "-m", "pip", "install", "pygame"]
    try:
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        return "[Success] Pygame dependency check passed." if result.returncode == 0 else f"[Error] Install failed: {result.stderr}"
    except Exception as e:
        return f"[Error] Installation failed: {str(e)}"

def compile_to_executable(filename):
    print(f"[Software Engineer] Compiling {filename} to a standalone executable...")
    
    # Ensure PyInstaller is available
    subprocess.run([PYTHON_EXE, "-m", "pip", "install", "pyinstaller"], capture_output=True)
    
    try:
        # Run PyInstaller: --onefile makes it standalone, --noconsole hides the command prompt window
        # --distpath routes the final .exe straight to your deliverables folder
        result = subprocess.run(
            [PYTHON_EXE, "-m", "PyInstaller", "--onefile", "--noconsole", 
             "--distpath", DELIVERABLES_PATH, filename],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            exe_name = os.path.basename(filename).replace('.py', '.exe')
            log_agency_action("Software Engineer", "Compile", f"Successfully compiled {exe_name}")
            return True, os.path.join(DELIVERABLES_PATH, exe_name)
        else:
            log_agency_action("Software Engineer", "Compile Error", "Failed to compile executable")
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)

# --- Consolidated Software Engineer Agent ---
def software_engineer_agent(task_prompt, model="qwen2.5:latest", filename=None, attempt=1):
    # Dynamic naming and path routing
    if filename is None:
        # Check if the user specified a name in the prompt
        name_match = re.search(r'named\s+([a-zA-Z0-9_ -]+\.py)', task_prompt, re.IGNORECASE)
        if name_match:
            filename = os.path.join(DELIVERABLES_PATH, name_match.group(1).strip())
        else:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(DELIVERABLES_PATH, f"task_{timestamp_str}.py")
    elif not os.path.isabs(filename):
        filename = os.path.join(DELIVERABLES_PATH, filename)

    if attempt == 1:
        print(f"[Software Engineer] {check_and_install_dependencies()}")

    if attempt > MAX_RETRIES:
        save_memory(task_prompt, "Reached max retries", False)
        return "[Error] Maximum retry attempts reached."

    if attempt == 1 and os.path.exists(filename) and "patch" not in task_prompt.lower():
        print(f"[Warning] Overwriting existing file: {filename}")

    print(f"\n[Software Engineer] Evaluating task (Attempt {attempt}) using model: {model}...")
    
    assigned_model = model
    engineer_persona = "You are an elite Lead Software Engineer. Write clean, production-grade code. Output ONLY code."
    
    # --- MEMORY INJECTION ---
    past_lessons = load_past_memory(task_prompt)
    
    full_prompt = f"{engineer_persona}\n\n--- PAST MEMORY & LESSONS LEARNED ---\n{past_lessons}\n\nTask Prompt:\n{task_prompt}"
    payload = {"model": assigned_model, "prompt": full_prompt, "stream": False, "options": {"temperature": 0.2}}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        raw_response = response.json().get("response", "")
        
        # Regex extraction: looks for content between triple backticks, handles optional 'python' tag
        match = re.search(r"```(?:python)?\s*(.*?)\s*```", raw_response, re.DOTALL | re.IGNORECASE)
        clean_code = match.group(1).strip() if match else raw_response.strip()
        
        success, feedback = execute_and_verify(clean_code, filename)
        
        if success:
            print("[Software Engineer] Code saved and verified. Executing...")
            run_background_script(filename)
            save_memory(task_prompt, "Code executed successfully", True)
            
            # The Explicit Handoff
            handoff_alert = f"\n[!] DELIVERABLE READY: Python script saved at:\n -> {filename}\n"
            
            # NEW: The Auto-Compile Trigger
            if "executable" in task_prompt.lower() or ".exe" in task_prompt.lower():
                comp_success, comp_path = compile_to_executable(filename)
                if comp_success:
                    handoff_alert += f"[!] EXECUTABLE READY: Standalone tool compiled to:\n -> {comp_path}\n"
                else:
                    handoff_alert += f"[X] COMPILATION FAILED. Check PyInstaller logs.\n"
                    
            print(handoff_alert)
            return handoff_alert + clean_code
        else:
            print(f"[Software Engineer] Syntax error: {feedback}. Auto-fixing...")
            fix_prompt = f"The following code failed with: {feedback}\n\nCode:\n{clean_code}\n\nFix it."
            return software_engineer_agent(fix_prompt, model=model, filename=filename, attempt=attempt + 1)
            
    except Exception as e:
        save_memory(task_prompt, str(e), False)
        return f"[Software Engineer Error] {e}"

if __name__ == "__main__":
    initialize_memory()
    print("System Check: Folders and Memory File verified.")
    
    user_task = input("\n[!] Enter the coding task for the Software Engineer: ")
    custom_name = input("[?] Enter a custom filename (or press Enter for auto-timestamp): ").strip()
    
    # If you typed a name, ensure it has .py and pass it to the agent
    if custom_name:
        if not custom_name.endswith('.py'):
            custom_name += '.py'
        software_engineer_agent(user_task, filename=custom_name)
    else:
        # If you just pressed Enter, it uses the default timestamp naming
        software_engineer_agent(user_task)

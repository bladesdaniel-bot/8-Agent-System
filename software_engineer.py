import os
import requests
import subprocess
from datetime import datetime
import json
import re
import ast
import threading
import time
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import shutil

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
PYTHON_EXE = "python"
MAX_RETRIES = 5

# --- Memory System Setup ---
DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\8 Agent Project\AI_Agent_Memory"
MEMORY_FILE = os.path.join(DESKTOP_PATH, "software_engineer_memory_bank.json")
DELIVERABLES_PATH = r"C:\Users\blade\OneDrive\Desktop\Completed_Coding_Projects"

def initialize_memory():
    """Manually create the folders and file if they don't exist."""
    if not os.path.exists(DESKTOP_PATH):
        os.makedirs(DESKTOP_PATH)
        
    if not os.path.exists(DELIVERABLES_PATH):
        os.makedirs(DELIVERABLES_PATH)
    
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_past_memory(current_prompt, limit=5):
    """Reads past memory and returns entries most similar to the current prompt."""
    if not os.path.exists(MEMORY_FILE):
        return "No past memory file found."
        
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
            if not memory:
                return "No past memory recorded yet."
            
            def get_keywords(text):
                words = set(re.findall(r'\b\w+\b', text.lower()))
                stop_words = {"write", "a", "to", "the", "in", "for", "and", "is", "script", "python", "create", "make", "cpp", "javascript", "typescript"}
                return words - stop_words
            
            prompt_keywords = get_keywords(current_prompt)
            
            for entry in memory:
                entry_keywords = get_keywords(entry.get("task", ""))
                entry["relevance"] = len(prompt_keywords.intersection(entry_keywords))
            
            memory.sort(key=lambda x: (x.get("relevance", 0), x.get("timestamp", "")), reverse=True)
            relevant_logs = memory[:limit]
            
            for log in relevant_logs:
                log.pop("relevance", None)
                
            return json.dumps(relevant_logs, indent=2)
            
    except Exception:
        return "Could not parse past memory."

initialize_memory()

def save_memory(task, outcome, is_success):
    with open(MEMORY_FILE, 'r+', encoding='utf-8') as f:
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
    with open(manifest_path, "a", encoding='utf-8') as f:      
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Created: {filename}\n")

def log_agency_action(agent_name, action, details):
    audit_path = os.path.join(DELIVERABLES_PATH, "agency_audit_trail.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(audit_path, "a", encoding='utf-8') as f:      
        f.write(f"[{timestamp}] Agent: {agent_name} | Action: {action} | Details: {details}\n")

# --- Multi-Language Dispatcher: Syntax Verification ---
def execute_and_verify(code, filename):
    with open(filename, "w", encoding='utf-8') as f:
        f.write(code)
    log_new_file(filename)
    
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == '.py':
            result = subprocess.run([PYTHON_EXE, "-m", "py_compile", filename], capture_output=True, text=True)
            return (True, "Python code passed syntax check.") if result.returncode == 0 else (False, result.stderr)
            
        elif ext == '.ps1':
            ps_command = f"[System.Management.Automation.Language.Parser]::ParseFile('{filename}', [ref]$null, [ref]$null)"
            result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
            return (True, "PowerShell script parsed successfully.") if result.returncode == 0 else (False, result.stderr)
            
        elif ext == '.js':
            result = subprocess.run(["node", "-c", filename], capture_output=True, text=True)
            return (True, "JavaScript syntax check passed.") if result.returncode == 0 else (False, result.stderr)
            
        elif ext == '.ts':
            result = subprocess.run(["tsc", "--noEmit", filename], capture_output=True, text=True)
            return (True, "TypeScript syntax check passed.") if result.returncode == 0 else (False, result.stderr)
            
        elif ext == '.ipynb':
            try:
                import json
                with open(filename, 'r', encoding='utf-8') as nb_file:
                    json.load(nb_file)
                return (True, "Jupyter Notebook structure is valid JSON.")
            except Exception as e:
                return (False, f"Invalid Jupyter Notebook JSON structure: {str(e)}")
            
        else:
            return True, "Generic file syntax check bypassed."
            
    except Exception as e:
        return False, str(e)

# --- Multi-Language Screen Recording Preview ---
def record_screen_preview(output_video_path, duration=15):
    try:
        import mss
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 20.0
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            capture_box = {'top': monitor['top'] + 100, 'left': monitor['left'] + 100, 'width': 800, 'height': 600}
            
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (800, 600))
            
            start_time = time.time()
            while time.time() - start_time < duration:
                img = np.array(sct.grab(capture_box))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(frame)
                time.sleep(1 / fps)
            out.release()
    except Exception as e:
        print(f"[Preview Warning] Could not record screen preview: {e}")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 20.0
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (640, 480))
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank_frame, "Preview Unavailable", (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        for _ in range(int(duration * fps)):
            out.write(blank_frame)
        out.release()

        # --- Auto-Dependency Manager ---
def auto_install_dependencies(code, filename, staging_path):
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.py':
        imports = set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names: imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module: imports.add(node.module.split('.')[0])
        except Exception:
            pass
        
        if imports:
            print(f"[Dependency Manager] Auto-installing packages via Conda/Pip: {', '.join(imports)}")
            for mod in imports:
                # Try Anaconda first
                conda_result = subprocess.run(["conda", "install", "-y", mod], capture_output=True)
                if conda_result.returncode != 0:
                    # Fallback to pip if Conda doesn't have the package in its default channels
                    subprocess.run([PYTHON_EXE, "-m", "pip", "install", mod], capture_output=True)
                
    elif ext in ['.js', '.ts']:
        imports = set()
        imports.update(re.findall(r"(?:require\(['\"])(.*?)(?:['\"]\))", code))
        imports.update(re.findall(r"(?:from\s+['\"])(.*?)(?:['\"])", code))
        
        valid_mods = [m for m in imports if not m.startswith('.')]
        if valid_mods:
            print(f"[Dependency Manager] Auto-installing NPM packages: {', '.join(valid_mods)}")
            if not os.path.exists(os.path.join(staging_path, 'package.json')):
                subprocess.run(["npm", "init", "-y"], cwd=staging_path, capture_output=True)
            for mod in valid_mods:
                subprocess.run(["npm", "install", mod], cwd=staging_path, capture_output=True)


# --- Multi-Language Compilation Dispatcher ---
def compile_to_executable(filename, output_dir):
    ext = os.path.splitext(filename)[1].lower()
    print(f"[Software Engineer] Compiling {filename} to a standalone executable...")
    
    if ext == '.ipynb':
        print(f"[Compiler] Bypassing executable compilation for Jupyter Notebook.")
        # Returns True to keep the workflow moving, and passes back the raw notebook path
        return True, filename
        
    elif ext == '.py':
        subprocess.run([PYTHON_EXE, "-m", "pip", "install", "pyinstaller"], capture_output=True)
        try:
            result = subprocess.run(
                [PYTHON_EXE, "-m", "PyInstaller", "--onefile", "--noconsole", 
                 "--distpath", output_dir, filename],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                exe_name = os.path.basename(filename).replace('.py', '.exe')
                log_agency_action("Software Engineer", "Compile", f"Successfully compiled {exe_name}")
                return True, os.path.join(output_dir, exe_name)
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
            
    elif ext == '.ps1':
        try:
            subprocess.run(["powershell", "-Command", "Install-Module -Name ps2exe -Force -Scope CurrentUser"], capture_output=True)
            exe_name = os.path.basename(filename).replace('.ps1', '.exe')
            out_exe = os.path.join(output_dir, exe_name)
            ps_compile_cmd = f"Invoke-PS2Exe -InputFile '{filename}' -OutputFile '{out_exe}' -NoConsole"
            result = subprocess.run(["powershell", "-Command", ps_compile_cmd], capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(out_exe):
                return True, out_exe
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
            
    elif ext in ['.cpp', '.cc']:
        exe_name = os.path.basename(filename).replace(ext, '.exe')
        out_exe = os.path.join(output_dir, exe_name)
        try:
            result = subprocess.run(["g++", filename, "-o", out_exe, "-O3"], capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(out_exe):
                log_agency_action("Software Engineer", "Compile", f"Successfully compiled C++ to {exe_name}")
                return True, out_exe
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
            
    elif ext in ['.js', '.ts']:
        try:
            if ext == '.ts':
                subprocess.run(["tsc", filename], capture_output=True)
                filename = filename.replace('.ts', '.js')
            
            subprocess.run(["npm", "install", "-g", "pkg"], capture_output=True)
            exe_name = os.path.basename(filename).replace('.js', '.exe')
            out_exe = os.path.join(output_dir, exe_name)
            
            result = subprocess.run(["pkg", filename, "--target", "node18-win-x64", "--output", out_exe], capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(out_exe):
                return True, out_exe
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
            
    return False, "Unsupported extension for compilation."

# --- Security Static Analysis Auditor ---
def security_audit(code, filename):
    print("[Security Auditor] Running static analysis scan...")
    risks = []
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.py':
        dangerous_patterns = [
            (r'\bdeval\s*\(', "Use of built-in eval() detected."),
            (r'\bexec\s*\(', "Use of built-in exec() detected."),
            (r'shell\s*=\s*True', "Subprocess with shell=True detected."),
            (r'pickle\.load', "Unsafe deserialization using pickle detected.")
        ]
        for pattern, msg in dangerous_patterns:
            if re.search(pattern, code): risks.append(msg)
    elif ext == '.ps1':
        if 'Invoke-Expression' in code or 'iex ' in code:
            risks.append("Use of Invoke-Expression (iex) detected.")
    elif ext in ['.cpp', '.cc']:
        if 'system(' in code or 'popen(' in code:
            risks.append("Unsafe system call or popen detected in C++.")
            
    if risks:
        risk_summary = "; ".join(risks)
        log_agency_action("Security Auditor", "Warning", f"Found risks: {risk_summary}")
        return False, f"Security vulnerabilities detected: {risk_summary}"
    
    log_agency_action("Security Auditor", "Pass", "Static security analysis passed.")
    return True, "No high-risk security patterns detected."

# --- Automatic Documentation Generator ---
def generate_code_documentation(filename, code):
    print("[Documentation Generator] Generating specification README...")
    try:
        base_name = os.path.basename(filename)
        doc_filename = filename.replace(os.path.splitext(filename)[1], '_README.md')
        
        doc_content = f"# Documentation for {base_name}\n\n"
        doc_content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        doc_content += "## Overview\nAuto-generated specification sheet and execution manifest.\n\n"
        doc_content += "## Source Code Preview\n```\n" + code[:500] + "\n...\n```\n"
        
        with open(doc_filename, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        log_new_file(os.path.basename(doc_filename))
    except Exception as e:
        print(f"[Documentation Generator Error] {e}")

# --- GUI Approval Dialog with File Name Display ---
def request_user_approval(video_path, exe_path, py_path, readme_path):
    approval_result = {"approved": False, "reason": ""}
    file_name = os.path.basename(py_path)
    
    root = tk.Tk()
    root.title(f"Software Engineer - Approval Gate ({file_name})")
    root.geometry("640x600")
    root.configure(bg="#1e1e1e")
    
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    header_label = tk.Label(root, text=f"[!] REVIEWING FILE: {file_name}", fg="#00ffcc", bg="#1e1e1e", font=("Consolas", 11, "bold"))
    header_label.pack(pady=10)
    
    video_label = tk.Label(root, bg="black")
    video_label.pack(pady=5)
    
    def play_video():
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame = cv2.resize(frame, (480, 270))
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2_image)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Safely hand the image update off to the main Tkinter thread
            def update_image(tk_img=imgtk):
                try:
                    video_label.imgtk = tk_img
                    video_label.configure(image=tk_img)
                except Exception:
                    pass
            
            try:
                root.after(0, update_image)
            except Exception:
                break
            
            time.sleep(0.03)
        cap.release()

    threading.Thread(target=play_video, daemon=True).start()
    
    info_text = tk.Label(root, text=f"Deliverable built at:\n{exe_path}\n\nReview the 15-second running clip above. Approve or Deny.", fg="white", bg="#1e1e1e", font=("Consolas", 9), justify="center")
    info_text.pack(pady=10)
    
    def on_approve():
        approval_result["approved"] = True
        root.destroy()
        
    def on_deny():
        reason = simpledialog.askstring("Denial Feedback", f"Why are you denying '{file_name}'?\n(Provide feedback for AI memory training):", parent=root)
        approval_result["approved"] = False
        approval_result["reason"] = reason if reason else "No specific reason provided."
        root.destroy()
        
    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=15)
    
    approve_btn = tk.Button(btn_frame, text=" APPROVAL ", bg="#28a745", fg="white", font=("Consolas", 11, "bold"), width=15, command=on_approve)
    approve_btn.pack(side=tk.LEFT, padx=10)
    
    deny_btn = tk.Button(btn_frame, text=" DENIAL ", bg="#dc3545", fg="white", font=("Consolas", 11, "bold"), width=15, command=on_deny)
    deny_btn.pack(side=tk.RIGHT, padx=10)
    
    root.mainloop()
    return approval_result

# --- Human Override GUI ---
def request_human_intervention_gui(filename, existing_code, error_msg):
    result_code = [None]
    
    root = tk.Tk()
    root.title(f"Human Override Required - {os.path.basename(filename)}")
    root.geometry("800x700")
    root.configure(bg="#1e1e1e")
    
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    lbl_info = tk.Label(root, text="[!] AI FAILED 5 TIMES. MANUAL FIX REQUIRED.", fg="#ff4444", bg="#1e1e1e", font=("Consolas", 14, "bold"))
    lbl_info.pack(pady=10)
    
    lbl_err = tk.Label(root, text=f"Last Error/Feedback:\n{error_msg}", fg="#ffcc00", bg="#1e1e1e", font=("Consolas", 10), justify="left", wraplength=760)
    lbl_err.pack(pady=5)
    
    scroll_y = tk.Scrollbar(root)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_area = tk.Text(root, bg="#2d2d2d", fg="white", font=("Consolas", 11), yscrollcommand=scroll_y.set, undo=True)
    text_area.pack(expand=True, fill='both', padx=10, pady=5)
    scroll_y.config(command=text_area.yview)
    
    if existing_code:
        text_area.insert("1.0", existing_code)
        
    def on_submit():
        result_code[0] = text_area.get("1.0", tk.END).strip()
        root.destroy()
        
    def on_cancel():
        root.destroy()
        
    btn_frame = tk.Frame(root, bg="#1e1e1e")
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text=" SUBMIT FIX & RETEST ", bg="#28a745", fg="white", font=("Consolas", 11, "bold"), command=on_submit).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text=" CANCEL OVERRIDE ", bg="#dc3545", fg="white", font=("Consolas", 11, "bold"), command=on_cancel).pack(side=tk.RIGHT, padx=10)
    
    root.mainloop()
    return result_code[0]

# --- Consolidated Software Engineer Agent ---
def software_engineer_agent(task_prompt, model="qwen2.5:latest", filename=None, attempt=1, existing_code=None, staging_path=None):
    
    if staging_path is None:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_slug = re.sub(r'[^a-zA-Z0-9]', '_', task_prompt[:15]).strip('_')
        staging_path = os.path.join(DELIVERABLES_PATH, f"Project_{timestamp_str}_{safe_slug}")
        if not os.path.exists(staging_path):
            os.makedirs(staging_path)

    prompt_lower = task_prompt.lower()
    if "cpp" in prompt_lower or "c++" in prompt_lower or ".cpp" in prompt_lower:
        default_ext = ".cpp"
    elif "typescript" in prompt_lower or ".ts" in prompt_lower:
        default_ext = ".ts"
    elif "javascript" in prompt_lower or ".js" in prompt_lower:
        default_ext = ".js"
    elif "powershell" in prompt_lower or ".ps1" in prompt_lower:
        default_ext = ".ps1"
    elif "jupyter" in prompt_lower or "notebook" in prompt_lower or ".ipynb" in prompt_lower:
        default_ext = ".ipynb"
    else:
        default_ext = ".py"

    if filename is None:
        name_match = re.search(r'named\s+([a-zA-Z0-9_ -]+\.(?:py|ps1|js|ts|cpp))', task_prompt, re.IGNORECASE)
        if name_match:
            filename = os.path.join(staging_path, name_match.group(1).strip())
        else:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(staging_path, f"task_{timestamp_str}{default_ext}")
    else:
        if not os.path.splitext(filename)[1]:
            filename = filename + default_ext
            
        if not os.path.isabs(filename):
            filename = os.path.join(staging_path, filename)
                # Hard-fail removed. Hands over to human if attempt > MAX_RETRIES
    ext = os.path.splitext(filename)[1].lower()
    
    if existing_code:
        engineer_persona = (
            f"You are an elite Lead Software Engineer. Provide a targeted line-number patch or "
            f"precise code correction in {ext}. Do not rewrite the whole file. Output ONLY the line numbers and code to replace."
        )
    else:
        engineer_persona = (
            f"You are an elite Lead Software Engineer. Write clean, production-grade {ext} code. "
            f"UNIVERSAL RULE: You must build a persistent start-up counter using a local 'startup_config.json' file. "
            f"If the application boot count is 2 or fewer, you must launch an automated background thread (using PyAutoGUI or similar) "
            f"to visually demonstrate the app's functionality (moving the mouse, clicking buttons, triggering mock alerts) starting 2 seconds after boot. "
            f"If the boot count is 3 or higher, completely bypass this automation so the app opens normally. Output ONLY code."
        )

    
    past_lessons = load_past_memory(task_prompt)
    
    if existing_code:
        full_prompt = f"{engineer_persona}\n\nExisting Code:\n{existing_code}\n\nError/Feedback:\n{task_prompt}"
    else:
        full_prompt = f"{engineer_persona}\n\n--- PAST MEMORY & LESSONS LEARNED ---\n{past_lessons}\n\nTask Prompt:\n{task_prompt}"
        
    payload = {"model": model, "prompt": full_prompt, "stream": False, "options": {"temperature": 0.2}}
    try:
        if attempt <= MAX_RETRIES:
            print(f"\n[Software Engineer] Evaluating task (Attempt {attempt}) using model: {model}...")
            response = requests.post(OLLAMA_URL, json=payload)
            raw_response = response.json().get("response", "")
            
            match = re.search(r"```(?:python|powershell|javascript|js|typescript|ts|cpp)?\s*(.*?)\s*```", raw_response, re.DOTALL | re.IGNORECASE)
            clean_code = match.group(1).strip() if match else raw_response.strip()
            
            # --- Pause for Manual Patch Integration ---
            if existing_code:
                print(f"\n[AI Suggested Patch for Attempt {attempt}]:\n{clean_code}\n")
                input(f"[!] Pausing workflow.\n[!] Please manually apply the exact line-number fix above to:\n -> {filename}\n[!] Press Enter once you have saved the file to continue...")
                
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        clean_code = f.read()
                except Exception as e:
                    return f"[Error] Could not read updated file: {e}"
            # ------------------------------------------
        else:
            print(f"\n[!] AI failed {MAX_RETRIES} times. Engaging Human Override (Attempt {attempt})...")
            clean_code = request_human_intervention_gui(filename, existing_code, task_prompt)
            
            if not clean_code:
                save_memory(task_prompt, "Human override canceled", False)
                return "[!] Human override canceled. Exiting."

        success, feedback = execute_and_verify(clean_code, filename)

        
        if success:
            sec_passed, sec_msg = security_audit(clean_code, filename)
            if not sec_passed:
                print(f"[Security Auditor] {sec_msg}. Requesting security fix...")
                return software_engineer_agent(
                    task_prompt=f"Fix security issue: {sec_msg}", 
                    model=model, 
                    filename=filename, 
                    attempt=attempt + 1, 
                    existing_code=clean_code,
                    staging_path=staging_path
                )
            
            generate_code_documentation(filename, clean_code)
            
            # Intercept and install dependencies before compiling
            auto_install_dependencies(clean_code, filename, staging_path)
            
            comp_success, stage_exe_path = compile_to_executable(filename, staging_path)

            if not comp_success:
                return f"[X] COMPILATION FAILED:\n{stage_exe_path}"

            video_preview_path = filename.replace(ext, '_preview.avi')
            print(f"[Software Engineer] Executing {ext} application and recording 15-second video preview...")
            
            # Helper to run execution
            def run_background_script():
                if ext in ['.cpp', '.cc'] and os.path.exists(stage_exe_path):
                    command = [stage_exe_path]
                elif ext == '.py':
                    command = [PYTHON_EXE, os.path.abspath(filename)]
                elif ext == '.ps1':
                    command = ["powershell", "-ExecutionPolicy", "Bypass", "-File", os.path.abspath(filename)]
                elif ext == '.js':
                    command = ["node", os.path.abspath(filename)]
                elif ext == '.ts':
                    js_file = os.path.abspath(filename).replace('.ts', '.js')
                    command = ["node", js_file]
                elif ext == '.ipynb':
                    # Launches the Anaconda Jupyter Notebook server automatically
                    command = ["jupyter", "notebook", os.path.abspath(filename)]
                else:
                    command = [os.path.abspath(filename)]
                    
                try:
                    process = subprocess.Popen(command)
                    
                    def monitor_storage():
                        max_size_bytes = 250 * 1024 * 1024 # 250 MB hard limit
                        while process.poll() is None:
                            total_size = 0
                            for dirpath, _, filenames in os.walk(staging_path):
                                for f in filenames:
                                    fp = os.path.join(dirpath, f)
                                    if not os.path.islink(fp) and os.path.exists(fp):
                                        total_size += os.path.getsize(fp)
                            if total_size > max_size_bytes:
                                print("\n[!] WARNING: Runaway file generation detected! Nuking process to protect hard drive.")
                                subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
                                break
                            time.sleep(1)
                            
                    threading.Thread(target=monitor_storage, daemon=True).start()
                    
                    time.sleep(1)
                    record_screen_preview(video_preview_path, duration=15)
                    
                    if process.poll() is None:
                        # Force-kill the parent process AND any children it spawned
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
                except Exception as e:
                    print(f"[Preview Warning] {e}")



            run_background_script()

            readme_path = filename.replace(ext, '_README.md')
            approval_result = request_user_approval(video_preview_path, stage_exe_path, filename, readme_path)

            if os.path.exists(video_preview_path): 
                os.remove(video_preview_path)

            if approval_result["approved"]:
                save_memory(task_prompt, "Code executed and approved", True)
                handoff_alert = f"\n[!] DELIVERABLE APPROVED & SAVED IN:\n -> {staging_path}\n"
                print(handoff_alert)
                return handoff_alert + clean_code
            else:
                denial_reason = approval_result["reason"]
                print(f"[!] DENIAL RECEIVED. Reason: {denial_reason}")
                print("[!] Wiping entire project folder due to denial...")
                
                if os.path.exists(staging_path):
                    try: shutil.rmtree(staging_path)
                    except Exception: pass
                
                save_memory(task_prompt, f"Denied by user. Reason: {denial_reason}", False)
                return f"[!] Run rejected and folder wiped clean. Recorded denial reason to memory: '{denial_reason}'"
        else:
            print(f"[Software Engineer] Syntax error: {feedback}. Requesting targeted patch...")
            return software_engineer_agent(
                task_prompt=feedback, 
                model=model, 
                filename=filename, 
                attempt=attempt + 1, 
                existing_code=clean_code,
                staging_path=staging_path
            )
            
    except Exception as e:
        save_memory(task_prompt, str(e), False)
        return f"[Software Engineer Error] {e}"

if __name__ == "__main__":
    initialize_memory()
    print("System Check: Folders and Memory File verified.")
    
    user_task = input("\n[!] Enter the coding task for the Software Engineer: ")
    
    # Tkinter Pop-up for the filename
    root = tk.Tk()
    root.withdraw()  # Hides the empty background window
    custom_name = simpledialog.askstring("File Name", "Enter the exact name for this app (e.g., ChatBot):")
    root.destroy()
    
    # Clean up spaces for the compiler or handle if you hit Cancel
    if not custom_name:
        custom_name = ""
    else:
        custom_name = custom_name.strip().replace(" ", "_")
    
    if custom_name:
        software_engineer_agent(user_task, filename=custom_name)
    else:
        software_engineer_agent(user_task)

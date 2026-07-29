import os

import sys

import json

import tkinter as tk

from tkinter import scrolledtext

from pathlib import Path

from dotenv import load_dotenv

from google import genai

from google.genai import types # Added for strict JSON typing



# ==========================================

# 1. CREDENTIALS (SECURE LOAD)

# ==========================================

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=gemini_api_key)



# ==========================================

# 2. THE RED TEAM AGENT

# ==========================================

def red_team_hacker(user_command):

    """The AI Red Team Agent extracts a path, scans it, and offers a two-step GUI to fix and auto-save."""

    

    print("\n[Red Team] Waking up. Analyzing command for target path...")

    

    # --- STEP 1: EXTRACTION BRAIN (UPGRADED TO STRICT JSON) ---

    extract_instructions = """

    The user wants to scan a file or folder on their hard drive. 

    Extract the exact file path or directory path from their command.

    

    OUTPUT RULE: Return ONLY a valid JSON object.

    {

        "target_path": "C:\\path\\to\\file_or_folder"

    }

    If you cannot find a recognizable file or folder path, put "UNKNOWN".

    """

    

    try:

        extraction_response = client.models.generate_content(

            model="gemini-2.5-flash-lite",

            contents=f"{extract_instructions}\n\nUser Command: {user_command}",

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

            )

        )

        

        path_data = json.loads(extraction_response.text)

        target_path = path_data.get("target_path", "UNKNOWN")

        

    except Exception as e:

        return f"Red Team Error: The Extraction Brain failed to parse the path. {e}"



    if target_path == "UNKNOWN":

        return "Red Team Error: I couldn't find a valid file or folder path in your command. Please give me an exact path to scan."



    # --- STEP 2: FILE SYSTEM VACUUM (UPGRADED WITH SAFETY LIMITS) ---

    print(f"[Red Team] Target acquired: {target_path}")

    print("[Red Team] Vacuuming files for analysis...")

    

    path = Path(target_path)

    content_to_scan = ""



    if not path.exists():

        return f"Red Team Error: The path '{target_path}' does not exist on this machine."



    # Safety limits to prevent context window overload

    ALLOWED_EXTENSIONS = {'.py', '.js', '.html', '.css', '.txt', '.json', '.cpp', '.c', '.java', '.go'}

    MAX_FILE_SIZE = 50000  # ~50KB



    if path.is_dir():

        for file_path in path.rglob("*"):

            if (file_path.is_file() and 

                not file_path.name.startswith(".") and 

                file_path.suffix in ALLOWED_EXTENSIONS):

                

                if file_path.stat().st_size < MAX_FILE_SIZE:

                    try:

                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:

                            content_to_scan += f"\n\n--- Start of {file_path.name} ---\n"

                            content_to_scan += f.read()

                            content_to_scan += f"\n--- End of {file_path.name} ---\n"

                    except Exception:

                        pass 

                else:

                    print(f"[Red Team] Skipping large file to protect memory: {file_path.name}")

                    

    elif path.is_file():

        try:

            with open(path, "r", encoding="utf-8", errors="ignore") as f:

                content_to_scan = f.read()

        except Exception as e:

            return f"Red Team Error: Could not read the file. {e}"



    if not content_to_scan.strip():

        return f"Red Team Error: No readable text or code found inside '{target_path}'."



    # --- STEP 3: THE VULNERABILITY SCAN ---

    print("[Red Team] Initiating Deep Scan via AI...")

    scan_instructions = f"""

    You are an elite Red Team Penetration Tester and Ethical Hacker. 

    Your objective is to aggressively analyze the provided code for any security vulnerabilities.

    

    Look for things like:

    - Hardcoded credentials or API keys

    - SQL Injection vulnerabilities

    - Command injection risks

    - Logic flaws that could be exploited

    

    Provide a tactical report detailing the vulnerability and how a malicious actor might exploit it. 

    DO NOT rewrite the code for them. Only report the threats. Do not use markdown backticks.



    Target Content:

    {content_to_scan}

    """

    

    try:

        scan_response = client.models.generate_content(

            model="gemini-2.5-flash-lite",

            contents=scan_instructions

        )

        threat_report = scan_response.text

    except Exception as e:

        return f"Red Team Error: The vulnerability scan failed. {e}"



    # --- STEP 4: GUI WINDOW 1 (THE THREAT REPORT) ---

    print("[Red Team] Scan complete. Launching Threat Report GUI...")

    

    root = tk.Tk()

    root.title(f"Red Team Hacker: Threat Report - {path.name}")

    root.geometry("800x600") 

    root.attributes("-topmost", True) 

    

    user_decision = tk.StringVar(value="IGNORE") 

    

    def click_fix():

        user_decision.set("FIX")

        root.destroy() 

        

    def click_ignore():

        user_decision.set("IGNORE")

        root.destroy() 

        

    header_text = f"TARGET: {target_path}\nSTATUS: SCAN COMPLETE"

    tk.Label(root, text=header_text, font=("Consolas", 12, "bold"), fg="#dc3545", justify="left").pack(pady=10, padx=20, anchor="w")

    

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=20, font=("Consolas", 10), bg="#1e1e1e", fg="#00ff00")

    text_area.insert(tk.INSERT, threat_report)

    text_area.config(state=tk.DISABLED) 

    text_area.pack(pady=10, padx=20)

    

    btn_frame = tk.Frame(root)

    btn_frame.pack(pady=15)

    

    tk.Button(btn_frame, text="🛠️ ROUTE TO SOFTWARE ENGINEER TO FIX", bg="#ffc107", fg="black", font=("Arial", 11, "bold"), width=40, command=click_fix).pack(side=tk.LEFT, padx=10)

    tk.Button(btn_frame, text="❌ IGNORE & CLOSE", bg="#dc3545", fg="white", font=("Arial", 11, "bold"), width=20, command=click_ignore).pack(side=tk.RIGHT, padx=10)

    

    root.mainloop() 

    

    # --- STEP 5: THE ROUTING HANDOFF ---

    if user_decision.get() == "FIX":

        print("\n[Red Team] Critical Action Authorized. Routing data to Software Engineer...")

        

        patch_prompt = f"""

        I am the Red Team Hacker. I just scanned a file and found severe vulnerabilities. 

        I need you to rewrite the code to patch these issues.

        

        HERE IS THE ORIGINAL BROKEN CODE:

        {content_to_scan}

        

        HERE IS MY THREAT REPORT IDENTIFYING THE BUGS:

        {threat_report}

        

        OUTPUT RULE: You MUST return ONLY the raw, fully patched code. 

        Do not use markdown backticks (like ```python). 

        Do not include any conversational text, explanations, or greetings. 

        Output ONLY the exact code so it can be directly saved to the file.

        """

        

        try:

            from software_engineer import software_engineer_agent

            print("[Software Engineer] Drafting secure patch. Please wait...")

            patch_plan = software_engineer_agent(patch_prompt)

        except ImportError:

            return "\n[Error] Could not find 'software_engineer.py'. Please make sure it is in the same folder!"

        except Exception as e:

            return f"\n[Error] The Software Engineer failed to write the patch: {e}"

            

        # --- STEP 6: GUI WINDOW 2 (THE PATCH REVIEW & AUTO-SAVE) ---

        print("[Software Engineer] Patch complete. Launching Approval GUI...")

        

        review_root = tk.Tk()

        review_root.title(f"Software Engineer: Patch Review - {path.name}")

        review_root.geometry("900x700") 

        review_root.attributes("-topmost", True) 

        

        final_decision = tk.StringVar(value="DENY") 

        

        def click_approve():

            final_decision.set("APPROVE")

            review_root.destroy() 

            

        def click_deny():

            final_decision.set("DENY")

            review_root.destroy() 

            

        review_header = f"TARGET: {target_path}\nACTION REQUIRED: Review the patched code below."

        tk.Label(review_root, text=review_header, font=("Consolas", 12, "bold"), fg="#28a745", justify="left").pack(pady=10, padx=20, anchor="w")

        

        # Text Area displaying the fixed code

        code_area = scrolledtext.ScrolledText(review_root, wrap=tk.WORD, width=100, height=25, font=("Consolas", 10), bg="#2b2b2b", fg="white")

        code_area.insert(tk.INSERT, patch_plan)

        code_area.config(state=tk.DISABLED) 

        code_area.pack(pady=10, padx=20)

        

        review_btn_frame = tk.Frame(review_root)

        review_btn_frame.pack(pady=15)

        

        tk.Button(review_btn_frame, text="💾 APPROVE & OVERWRITE FILE", bg="#28a745", fg="white", font=("Arial", 11, "bold"), width=35, command=click_approve).pack(side=tk.LEFT, padx=10)

        tk.Button(review_btn_frame, text="❌ DENY & DISCARD", bg="#dc3545", fg="white", font=("Arial", 11, "bold"), width=25, command=click_deny).pack(side=tk.RIGHT, padx=10)

        

        review_root.mainloop()



        # --- STEP 7: EXECUTE THE SAVE (UPGRADED WITH MARKDOWN STRIPPING) ---

        if final_decision.get() == "APPROVE":

            

            # Clean up potential markdown artifacts

            clean_code = patch_plan.strip()

            if clean_code.startswith("```"):

                clean_code = "\n".join(clean_code.split("\n")[1:-1])



            try:

                # If they targeted a specific file, cleanly overwrite it

                if path.is_file():

                    with open(path, "w", encoding="utf-8") as f:

                        f.write(clean_code)

                    return f"\n[SUCCESS] The file '{path.name}' has been successfully overwritten with the secure code!"

                

                # If they targeted a whole folder, saving multiple stitched files back is dangerous. 

                # Instead, we save the massive patch file safely into the folder.

                elif path.is_dir():

                    safe_save_path = path / "security_patch_output.txt"

                    with open(safe_save_path, "w", encoding="utf-8") as f:

                        f.write(clean_code)

                    return f"\n[SUCCESS] Folder scan patched! Saved a safe copy of the new code to: {safe_save_path}"

                    

            except Exception as e:

                return f"\n[Error] Failed to save the file to your hard drive: {e}"

        else:

            return "\n[Red Team] User denied the patch. The original file remains completely untouched."

            

    else:

        return "\n[Red Team] User elected to ignore vulnerabilities. Returning to standby."



# ==========================================

# 3. MANUAL OVERRIDE

# ==========================================

if __name__ == "__main__":

    if len(sys.argv) > 1:

        print(red_team_hacker(sys.argv[1]))

    else:

        print("Please provide a command containing a file path to scan.")

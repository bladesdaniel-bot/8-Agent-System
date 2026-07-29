import os
import time
import requests
import json
import ollama
from datetime import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
COMFYUI_URL = "http://127.0.0.1:8188"
TARGET_DIR = r"C:\Users\blade\OneDrive\Desktop\Image Tasks\output"
INPUT_DIR = r"C:\Users\blade\OneDrive\Desktop\Image Tasks\input"
WORKFLOW_PATH = r"C:\Users\blade\OneDrive\Desktop\Image Tasks\workflow_api.json"
VISION_MODEL = "llava"

# ==========================================
# 2. MEMORY SYSTEM SETUP
# ==========================================
DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\AI_Agent_Memory"
MEMORY_FILE = os.path.join(DESKTOP_PATH, "graphic_designer_memory_bank.json")

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
# 3. HELPER FUNCTIONS
# ==========================================
def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    requests.post(f"{COMFYUI_URL}/prompt", data=data)

def check_for_new_images():
    if not os.path.exists(INPUT_DIR): return None
    files = os.listdir(INPUT_DIR)
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            return os.path.join(INPUT_DIR, file)
    return None

def identify_image(image_path, past_lessons):
    print(f"[Graphic Designer] Analyzing content of: {os.path.basename(image_path)}...")
    try:
        prompt = f"--- PAST MEMORY & LESSONS LEARNED ---\n{past_lessons}\n\n--- CURRENT TASK ---\nDescribe what is in this image in detail."
        response = ollama.chat(
            model=VISION_MODEL,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_path]
            }]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error identifying image: {e}"

# ==========================================
# 4. GRAPHIC DESIGNER AGENT
# ==========================================
def graphic_designer_agent(user_instructions, image_path):
    print(f"\n[Graphic Designer] Analyzing: {image_path}")
    
    # --- MEMORY INJECTION ---
    past_lessons = load_past_memory()
    
    # Vision Task
    if "identify" in user_instructions.lower() or "what is" in user_instructions.lower():
        description = identify_image(image_path, past_lessons)
        print(f"\n[Graphic Designer Vision] {description}\n")
        save_memory(f"Identify {os.path.basename(image_path)}", description, True)
        return

    # ComfyUI Workflow Task
    try:
        with open(WORKFLOW_PATH, "r") as f:
            workflow = json.load(f)
        if "6" in workflow:
            workflow["6"]["inputs"]["text"] = user_instructions
        queue_prompt(workflow)
        print("[Graphic Designer] Job sent to ComfyUI successfully.")
        save_memory(f"ComfyUI Job: {user_instructions}", "Job queued successfully", True)
    except Exception as e:
        error_msg = f"Failed: {e}"
        print(f"[Graphic Designer Error] {error_msg}")
        save_memory(f"ComfyUI Job: {user_instructions}", error_msg, False)

# ==========================================
# 5. MAIN LOOP
# ==========================================
def main_loop():
    print("Graphic Designer Agent is running (ComfyUI + Vision Mode)...")
    while True:
        new_image = check_for_new_images()
        if new_image:
            user_task = input(f"\n--- NEW IMAGE DETECTED ---\nFile: {new_image}\nWhat do you want to do? > ")
            graphic_designer_agent(user_task, new_image)
            processed_dir = os.path.join(INPUT_DIR, "processed")
            if not os.path.exists(processed_dir): os.makedirs(processed_dir)
            os.rename(new_image, os.path.join(processed_dir, os.path.basename(new_image)))
        time.sleep(5) 

if __name__ == "__main__":
    main_loop()

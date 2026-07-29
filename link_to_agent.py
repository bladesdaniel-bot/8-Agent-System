import os
import time
import requests
import json

# ==========================================
# 1. LOCAL OLLAMA CONFIG
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"
# The CEO always uses your fastest, most reliable local model to make its routing decisions
CEO_BRAIN_MODEL = "qwen2.5" 

def call_ollama(prompt, model_to_use=CEO_BRAIN_MODEL):
    """Helper function to send prompts directly to the local Ollama server."""
    payload = {
        "model": model_to_use,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json().get("response", "")

# ==========================================
# AGENT 1: THE DEVELOPER
# ==========================================
def generate_code(user_task):
    dev_instructions = """
    You are the Lead Software Engineer in an 8-Agent System. You are reporting directly to your manager, Daniel.
    
    1. If Daniel just says hello, asks how you are, or makes conversational small talk, reply naturally and professionally without writing any code. Let him know you are standing by.
    2. If Daniel asks you to build or code something, provide a brief, friendly conversational introduction explaining what you are doing, then provide the requested Python code.
    
    CRITICAL SECURE CODING GUIDELINE:
    When generating code for sending emails via SMTP, you must handle ports correctly to avoid SSL/TLS connection failures:
    - If the port is 465, use `smtplib.SMTP_SSL()` (Implicit SSL). Do NOT call `starttls()`.
    - If the port is 587, use `smtplib.SMTP()` and call `starttls()` (Explicit TLS).
    """
    
    prompt = f"{dev_instructions}\n\nDaniel's Input: {user_task}"
    # Fetch the model the CEO selected from the system environment, default to qwen2.5 if missing
    assigned_model = os.environ.get("CEO_SELECTED_MODEL", "qwen2.5")
    return call_ollama(prompt, model_to_use=assigned_model)

# ==========================================
# AGENT 2: THE AUDITOR
# ==========================================
def audit_code(draft_code):
    auditor_instructions = """
    You are the strict but professional Cybersecurity Auditor in an 8-Agent System. You also report directly to Daniel.
    
    1. If the input provided is just conversational text (no code to review), simply reply with a friendly acknowledgment (e.g., "Systems secure. Standing by for code review, Daniel.")
    2. If there is code provided to review, check for security vulnerabilities and syntax bugs.
    3. If the code is flawless, respond conversationally confirming it is secure, and explicitly include the phrase 'AUDIT PASSED: APPROVED.'
    4. If there are issues, provide a friendly but firm explanation of the exact problems found.
    """
    
    prompt = f"{auditor_instructions}\n\nData to Review:\n{draft_code}"
    assigned_model = os.environ.get("CEO_SELECTED_MODEL", "qwen2.5")
    return call_ollama(prompt, model_to_use=assigned_model)

# ==========================================
# AGENT 3: THE CEO ROUTER (WITH DYNAMIC MODEL SELECTION)
# ==========================================
def get_ceo_routing(user_task):
    task_clean = user_task.lower().strip()

    # ------------------------------------------------------------
    # ⚡ LOCAL KEYWORD INTERCEPTOR (ZERO-TOKEN ROUTING)
    # ------------------------------------------------------------
    email_keywords = ["sweep", "email", "inbox", "clean", "spam", "draft", "mail", "send to"]
    if any(keyword in task_clean for keyword in email_keywords):
        print("⚡ Local Match Detected: Routing directly to 'email' on fast model")
        os.environ["CEO_SELECTED_MODEL"] = "qwen2.5" # Default to fast model for simple local overrides
        return 'email'
    # ------------------------------------------------------------

    # The CEO now decides BOTH the Agent and the LLM Model
    prompt = f"""
    You are the CEO routing a task in an 8-Agent system. 
    Analyze the user's command and assign the best Agent AND the best local LLM model for the job.
    
    Available Models:
    - 'qwen2.5' (Use for fast, simple logic, basic python, or data formatting)
    - 'supergemma4-26b-uncensored-gguf-v2' (Use for heavy coding, red-team penetration scripts, or complex analysis)
    
    Valid Agents: 'email', 'cyber', 'sec_auditor', 'graphic', 'red_team', 'soft_eng', 'dev_mgr'

    CRITICAL: You MUST respond in ONLY strict, raw JSON format. Do not include markdown blocks like ```json. Do not include conversational filler or thoughts. 
    
    Example output format:
    {{"agent": "soft_eng", "model": "supergemma4-26b-uncensored-gguf-v2"}}

    User Command: "{user_task}"
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            raw_response = call_ollama(prompt, model_to_use=CEO_BRAIN_MODEL).strip()
            
            # Clean up potential markdown formatting if the LLM ignores instructions
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            elif raw_response.startswith("```"):
                raw_response = raw_response[3:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
                
            response_clean = raw_response.strip()
            
            decision_data = json.loads(response_clean)
            target_agent = decision_data.get("agent", "dev_mgr")
            target_model = decision_data.get("model", "qwen2.5")
            
            # Save the CEO's model choice to the system environment so the dashboard/workers can see it
            os.environ["CEO_SELECTED_MODEL"] = target_model
            print(f"👑 CEO selected Agent: [{target_agent}] using Model: [{target_model}]")
            
            valid_keys = ['email', 'cyber', 'sec_auditor', 'graphic', 'red_team', 'soft_eng', 'dev_mgr']
            if target_agent in valid_keys:
                return target_agent
            else:
                return 'dev_mgr'
                
        except Exception as e:
            print(f"⚠️ CEO Router parsing error. Retrying... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(2)
            
            if attempt == max_retries - 1:
                # Failsafe: Default to Dev Manager and fast model if CEO gets confused
                os.environ["CEO_SELECTED_MODEL"] = "qwen2.5"
                return 'dev_mgr'
print("Agent linked successfully!")

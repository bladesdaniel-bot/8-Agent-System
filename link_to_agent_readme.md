# link_to_agent.py

# 8-Agent AI Routing & Development Agency

This project is a multi-agent artificial intelligence agency powered by Google Gemini. It features a conversational Developer, a strict Security Auditor, and an intelligent "CEO Router" equipped with a cost-saving zero-token local interceptor to manage an 8-agent ecosystem.

## 🌟 Key Features

### 1. The CEO Router (Intelligent Task Delegation)
The core of this system is the CEO Router, which acts as the director of the 8-Agent agency. It decides which specialized agent should handle a user's request. It features a dual-layer routing mechanism:
* Zero-Token Local Interceptor: Instantly scans prompts for common keywords (like "email", "sweep", "inbox"). If a match is found, it routes the task locally without making an API call, saving time and API tokens.
* AI Fallback Routing: If the request is complex, the CEO uses Gemini to analyze the prompt and route it to the correct department within the agency (e.g., email, cyber, sec_auditor, graphic, red_team, soft_eng, dev_mgr).
* Robust Error Handling: Includes an automatic retry mechanism with exponential backoff to handle API rate limits (429) gracefully.

### 2. The Developer Agent
A conversational coding agent acting as the Lead Software Engineer, reporting directly to the user ("Daniel"). 
* Understands the difference between casual conversation and complex coding tasks.
* Enforces strict, secure coding guidelines (e.g., properly handling implicit SSL vs. explicit TLS for SMTP connections).

### 3. The Auditor Agent
A strict QA and cybersecurity agent.
* Scans generated code for vulnerabilities and syntax errors.
* Returns a clear "AUDIT PASSED: APPROVED" status for flawless code, or detailed feedback for necessary revisions.
* Capable of casual conversation if no code is present in the prompt.

## 📋 Prerequisites
* Python 3.9+
* Google GenAI SDK
* A valid Google Gemini API Key

## 🚀 Setup & Installation

1. Install required dependencies:
   pip install google-genai python-dotenv

2. Configure your environment:
   Create a file named .env in the root directory of your project and add your API key:
   GEMINI_API_KEY=your_actual_api_key_here

## 💻 Usage

You can integrate these functions into your main application loop. Here is an example of how to use them:

from your_script_name import get_ceo_routing, generate_code, audit_code

user_request = "Draft a Python script to send an email via port 587."

# 1. Route the task via the CEO
agent_assignment = get_ceo_routing(user_request)
print(f"Task assigned to: {agent_assignment}")

# 2. If assigned to development, generate code
if agent_assignment in ['dev_mgr', 'soft_eng', 'email']:
    draft = generate_code(user_request)
    print("Developer Draft Generated.")
    
    # 3. Audit the draft
    audit_report = audit_code(draft)
    print(f"Audit Report: {audit_report}")

## 🔒 Security Note
This system utilizes generative AI to output executable Python code. The Auditor agent provides a strong layer of defense, but all AI-generated code should be manually reviewed before execution in a production environment.

# 🧠 Local Multi-Agent AI Framework

A highly autonomous, privacy-first local AI framework driven by an 8-Agent architecture. This system utilizes a dynamic CEO router to delegate complex workflows to specialized sub-agents, leveraging local Large Language Models via Ollama, with secure cloud fallbacks. 

Designed for safety, transparency, and capability, the framework features persistent JSON-based memory banks (RAG) and Human-In-The-Loop (HITL) Tkinter GUI checkpoints. The interface is strictly designed with binary approval/denial toggles to ensure sensitive operations—like compiling code, patching files, or sending emails—are clear, deliberate, and always verified by a human operator.

---

## 🚀 Core Architecture & Features

### Dynamic CEO Routing (`ai_model_router.py`)
The "CEO" acts as the central brain of the framework. Instead of simply answering prompts, the CEO analyzes the user's task and outputs strict JSON directives.
*   **Zero-Token Interceptor:** Hardcoded local keyword detection bypasses the LLM for instantaneous routing of simple tasks (e.g., using keywords like "sweep" or "spam" to route directly to the Email Agent).
*   **Dynamic Model Assignment:** The CEO assigns both the **Agent** and the **LLM Model** best suited for the job. It routes simple logic to fast models and heavy development/security analysis to massive parameters.

### Dual-Routing LLM Engine (`api_router.py`)
*   **Local Priority:** Routes all operations through local `localhost:11434` endpoints to guarantee zero data leakage.
*   **Cloud Fallback:** If the local engine fails or is offline, the system seamlessly routes traffic to Gemini via the Google GenAI SDK.

### Persistent RAG Memory
Agents write to and read from independent JSON memory banks (e.g., `software_engineer_memory_bank.json`). 
*   **Keyword Relevance Scoring:** Before executing a task, the agent scans its memory bank, extracting past tasks with overlapping keywords to learn from prior mistakes and successes without blowing out the token context window.

### Human-In-The-Loop (HITL) Validation
The system uses native Tkinter windows to pause execution for human verification. To prevent UI clutter and user fatigue, popups are streamlined to feature specific "Approve" or "Deny" / "Fix" or "Ignore" binary toggles, rather than overwhelming multi-button layouts.

---

## 🧠 The Brains: AI Models
The framework dynamically shifts workloads across an extensive, locally-hosted model registry. This roster utilizes highly specialized, often "abliterated" or uncensored models to prevent standard safety filters from falsely blocking offensive cybersecurity tasks or unconstrained code generation:

*   **`general_fast`** (`qwen2.5:latest`): The rapid-response workhorse. Used by the CEO for instant task routing, simple logic parsing, and conversational UI interactions.
*   **`supergemma_expert`** (`hf.co/jiunsong/supergemma4-26b-uncensored-gguf-v2:latest`): A massive, uncensored heavy-lifter. Primarily assigned to the Red Team Hacker and Security Auditor for analyzing malicious payloads and deep threat-hunting without guardrail interference.
*   **`code_expert`** (`hf.co/mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-abliterated-i1-GGUF:latest`): An elite, abliterated 30B coding brain optimized for complex, multi-file software engineering and robust application generation.
*   **`qwen_coder`** (`huihui_ai/qwen2.5-abliterate:7b-instruct`): A fast, uncensored 7B coding model utilized by the Developer agent for rapid script generation, syntax fixing, and prototyping.
*   **`gemma_uncensored`** (`fredrezones55/Gemma-4-Uncensored-HauhauCS-Aggressive:e4b`): A highly aggressive, uncensored variant tailored for raw, unfiltered logic reasoning and offensive red-team penetration scripts.
*   **`vision_expert`** (`studiobrn/uncensoredmodai:latest`): The visual analysis engine, used by the Graphic Designer and routing systems to process images or generate complex visual prompt logic without constraints.
*   **`llama_general`** (`llama3.1:latest`): A solid, general-purpose fallback model for versatile task management, conversational assistance, and documentation drafting.
*   **`llama_abliterated` & `llama_3_1_abliterated`** (`abliterated-llama:latest` / `llama-3.1-abliterated:latest`): Uncensored LLaMA variants providing flexible, general-purpose reasoning unhindered by safety guardrails, perfect for broad SecOps analysis.

---

## 🤖 The 8-Agent Roster

### 1. 👑 The CEO Router
*   **Function:** Parses the initial user prompt and delegates execution across the framework.
*   **Capabilities:** Analyzes intent, assigns the most efficient local LLM from the registry, and manages the zero-token interceptor for immediate task routing.

### 2. 💻 Software Engineer
*   **Function:** Writes, tests, and compiles production-grade code.
*   **Capabilities:** 
    *   Iterative auto-fixing of syntax errors.
    *   Automatic dependency injection (e.g., installing missing modules via pip).
    *   Direct compilation of `.py` scripts into standalone, windowless desktop `.exe` applications using PyInstaller, ensuring no messy external DLL dependencies are left behind.

### 3. 🛡️ Red Team Hacker
*   **Function:** Offensive security analysis and penetration testing of local directories.
*   **Capabilities:** 
    *   Recursively scans allowed file types up to a 50KB limit.
    *   Generates comprehensive Tkinter threat reports outlining vulnerabilities.
    *   **Strict Patching Protocol:** When patching code, the agent is strictly forbidden from doing full-file rewrites. It isolates vulnerabilities and provides exact line-number replacements so that working production logic is never accidentally compromised by an AI hallucination.

### 4. 📋 Security Auditor
*   **Function:** Defensive system monitoring and physical hardware oversight.
*   **Capabilities:** 
    *   Pulls live hardware telemetry (CPU, RAM, Disk usage) via `psutil`.
    *   Executes localized PowerShell diagnostics (e.g., `netcheck.ps1`) to monitor network integrity.
    *   Analyzes inbound data and file payloads for malware signatures or network blocks.

### 5. 🔐 Cybersecurity Agent
*   **Function:** The strict code-reviewer and syntax auditor.
*   **Capabilities:** 
    *   Acts as a secondary checkpoint for code generated by other agents.
    *   Scans draft code for security vulnerabilities, injection risks, and syntax bugs. 
    *   Only issues an "AUDIT PASSED: APPROVED" status when the code is confirmed flawless.

### 6. 📧 Email Agent
*   **Function:** Automated inbox management and communication handling.
*   **Capabilities:** 
    *   Instantly triggered by the CEO's zero-token interceptor when keywords like "sweep," "inbox," "spam," or "draft" are detected.
    *   Manages outbound communications and inbox cleanup.
    *   Integrates with the system's secure SMTP configurations to prevent connection failures.

### 7. 🎨 Graphic Designer
*   **Function:** Visual asset generation and prompt engineering.
*   **Capabilities:** 
    *   Interfaces with image-generation backends (like ComfyUI) via local APIs.
    *   Specializes in formatting complex generation parameters (e.g., handling specific color temperatures, lighting constraints, and negative prompting) to produce highly specific visual assets on demand.

### 8. ⚙️ Developer / SecOps
*   **Function:** Foundation development with built-in security guardrails.
*   **Capabilities:** 
    *   Generates core logic while enforcing strict secure coding guidelines.
    *   Handles critical protocol enforcement, such as correctly assigning `smtplib.SMTP_SSL()` for Port 465 (Implicit SSL) versus `starttls()` for Port 587 (Explicit TLS).

---

## ⚙️ Prerequisites & Setup

### 1. Install Ollama & Pull Models
This framework requires [Ollama](https://ollama.com/) running locally. Pull the necessary models from the registry:
```bash
ollama run qwen2.5:latest
ollama run hf.co/jiunsong/supergemma4-26b-uncensored-gguf-v2:latest
ollama run hf.co/mradermacher/Huihui-Qwen3-Coder-30B-A3B-Instruct-abliterated-i1-GGUF:latest
ollama run llama3.1:latest
```
*(Add additional `ollama run` commands for any specific `abliterated` models you wish to use).*

### 2. Install Python Dependencies
Ensure you have an active Python environment. Install the framework requirements:
```bash
pip install requests flask psutil python-dotenv google-genai pyinstaller
```

### 3. Environment Configuration
Create a `.env` file in the root directory of the project:
```env
OLLAMA_API_KEY=local
GEMINI_API_KEY=your_google_api_key_here  # Used only as a fallback
```

### 4. Directory Structure Initialization
The framework will automatically create necessary directories on first run, including:
*   `Desktop/My Projects/AI_Agent_Memory/` (JSON memory banks)
*   `Desktop/Completed_Coding_Projects/` (Generated code and standalone `.exe` tools)
*   `RemoteLogs/` (Flask webhook captures)

---

## 🖥️ Usage Guide

### Starting the Main Dashboard
Launch the primary Tkinter interface to interact with the CEO:
```bash
python agent_dashboard.py
```
Type your objective into the prompt. The CEO will intercept the command, spin up the required agent, and execute the workflow with the appropriate model.

### Running Agents Independently
Agents can be executed in isolation via command-line arguments:

**Scan a file for vulnerabilities:**
```bash
python red_team_hacker.py "C:\path\to\your\script.py"
```

**Generate and compile a new application:**
```bash
python software_engineer.py
```

**Start the remote logging webhook:**
```bash
python webhook_server.py
```

# Local Dev-Sec-Ops AI Agent Pipeline

An automated, locally-hosted AI coding pipeline that utilizes two distinct AI personas—a **Developer** and a **Cybersecurity Auditor**—to write, review, and refine Python code autonomously. By leveraging a local Ollama instance, this tool ensures that your prompts and generated code remain 100% private and offline.

## Overview

When you request a script, the **Developer Agent** drafts the initial code. The **Auditor Agent** then inspects this draft for security vulnerabilities, syntax errors, and inefficiencies. If the Auditor finds issues, the feedback is sent back to the Developer for a revision. This loop continues until the Auditor explicitly approves the code or the maximum revision limit (3 iterations) is reached. 

It also features a **Persistent Memory System** that records past tasks, allowing the Developer agent to learn from previous mistakes and maintain context across different sessions.

## Key Features

* **Multi-Agent Loop:** Automated back-and-forth between a coding agent and a QA/Security agent.
* **100% Offline & Private:** Uses local LLM inference via the Ollama REST API (`http://localhost:11434`), keeping all codebase data on your machine.
* **Persistent Memory Bank:** Auto-logs tasks, outcomes, and success states into a JSON file (`developer_sec_ops_memory_bank.json`). The last 5 tasks are injected into the Developer's prompt to provide historical context.
* **Auto-Correction:** The Developer agent actively reads the Auditor's bulleted feedback and rewrites the code to fix identified vulnerabilities before presenting it to you.
* **Model Agnostic:** Defaults to `qwen2.5`, but can easily be overridden via an environment variable to use any model pulled to your Ollama instance.

## Prerequisites

1. **Python 3.8+**
2. **Ollama:** Must be installed and running locally on port 11434.
3. **Python Packages:**
   `pip install requests`
4. **Local LLM Model:** Pull the default model (or your preferred coding model) via Ollama:
   `ollama run qwen2.5`

## Configuration

Before running, you may want to adjust a few variables to fit your environment:

**1. Memory Directory Path**
Update the `DESKTOP_PATH` variable in the script to match where you want your JSON memory bank stored. By default, it is set to:
`DESKTOP_PATH = r"C:\Users\blade\OneDrive\Desktop\My Projects\AI_Agent_Memory"`

**2. Changing the AI Model**
The script defaults to the `qwen2.5` model. You can change this by setting the `CEO_SELECTED_MODEL` environment variable in your terminal before running the script, for example (on Windows):
`$env:CEO_SELECTED_MODEL="llama3"`

## How to Use

1. Ensure Ollama is running in the background.
2. Run the script from your terminal:
   `python dev_sec_ops.py`
3. The terminal will prompt you:
   `What do you want the Developer to build? (e.g., 'A script to scrape weather data'):`
4. Enter your prompt and press Enter.
5. Watch the terminal as the Developer and Auditor agents negotiate the code. 
6. Once the Auditor outputs `AUDIT PASSED: APPROVED`, the final, sanitized code will be printed to your terminal.

## The Agent Pipeline Workflow

1. **Memory Injection:** The script loads the last 5 entries from the memory JSON to provide context.
2. **Drafting (Iteration 1):** The Developer agent generates raw Python code based on your prompt.
3. **Auditing:** The Auditor agent reviews the code for exposed API keys, injection flaws, and syntax bugs.
4. **Negotiation:** 
   * If the Auditor finds flaws, it returns a bulleted list of issues. The Developer takes this list and writes Iteration 2.
   * This loops a maximum of 3 times.
5. **Final Output:** The script prints the final approved codebase and saves the interaction to the memory bank.

# AI Cybersecurity & Compliance Pipeline

A locally-hosted, multi-agent AI system designed to autonomously audit system logs, identify active security threats, and write custom Python patches. Powered by Ollama, this pipeline enforces a strict "Human-in-the-Loop" architecture, requiring explicit human approval via a Tkinter GUI before any automated fixes are deployed.

## Features

* Multi-Agent Architecture: Utilizes four distinct AI personas working in sequence:
  - Cybersecurity Auditor: Analyzes IP logs for active hacking attempts and unauthorized access.
  - General Security Auditor: Scans system reports for compliance issues, outdated software, and policy violations.
  - Developer Agent: Writes secure, targeted Python scripts to patch identified vulnerabilities.
  - CEO Agent: Translates technical data into a punchy, executive-level summary detailing the situation, risks, and proposed changes.
* Human-in-the-Loop GUI: Intercepts the automated pipeline with a custom Tkinter pop-up window, forcing human review of the CEO's summary and the Developer's code before deployment.
* Persistent Memory Bank: Logs all tasks, approvals, and denials into a local JSON memory file, allowing the system to maintain a historical audit trail of security events.
* Local Execution: Runs entirely offline using Ollama (defaulting to the qwen2.5 model), ensuring sensitive security logs never leave your local environment.

## Prerequisites

* Python 3.8+
* Ollama (running locally at http://localhost:11434)
* A local LLM model pulled via Ollama (e.g., qwen2.5)

## Configuration

Before running the application, ensure the directory paths match your local setup inside the script:

    OLLAMA_URL = "http://localhost:11434/api/generate"
    DESKTOP_PATH = r"C:\path\to\your\Memory_Folder"

## Installation

1. Clone the repository to your local machine.
2. Install the necessary Python dependencies:
   
    pip install requests

3. Ensure Ollama is actively running in the background.

## Usage

1. (Optional) Create `system_logs.txt` and `system_health.txt` in the root directory. If these files are not present, the system will automatically use simulated threat data (e.g., failed SSH logins).
2. Run the main pipeline:

    python cybersecurity_agent.py

3. Wait for the agents to process the data. 
4. A Tkinter GUI window titled "CEO SECURITY ALERT" will appear. Review the situation details, risk analysis, and the generated patch code.
5. Click "APPROVE & DEPLOY" to save the script as `auto_patch.py`, or "DENY & DISCARD" to abort the operation.

## System Workflow

1. Ingestion: Reads network and system health logs.
2. Analysis: Parallel auditing by the Cybersecurity and General Security agents.
3. Development: The Developer agent synthesizes the JSON threat reports into actionable Python code.
4. Review: The CEO agent formats the data for human consumption.
5. Deployment: The system awaits manual execution approval via the graphical interface.

## License

Distributed under the MIT License.

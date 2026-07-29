# Local AI Security Auditor Agent

An offline, privacy-first cybersecurity monitoring agent powered by local LLM inference via Ollama. This tool analyzes system telemetry, runs local PowerShell network diagnostics, scans email payloads for threats, and maintains a persistent memory bank of historical security audits.

## Features

* **100% Offline & Private Analysis:** Executes threat audits locally using Ollama (`supergemma4-26b-uncensored-gguf-v2:latest`), ensuring sensitive hardware logs, network state, and email payloads are never transmitted to external cloud endpoints.
* **Real-Time Hardware Telemetry:** Collects system performance metrics (CPU usage, virtual memory, and root/drive disk space) using `psutil`.
* **Automated Network Diagnostics:** Triggers local PowerShell diagnostics (`netcheck.ps1`) via subprocess execution to inspect active network states and detected blockages.
* **Email & Payload Scanning:** Ingests raw text or email files passed via command-line arguments to analyze body text for phishing vectors, malicious links, or malware signatures.
* **Persistent Memory Bank:** Records audit results, timestamps, and status outcomes to a JSON file (`security_auditor_memory_bank.json`). The last 5 audit entries are dynamically injected into subsequent analysis prompts to provide historical context.
* **GUI Integration Ready:** Outputs automated state updates directly to `status.json` (`critical` vs. `healthy`) for seamless integration with frontend dashboards or status UI widgets.

## Directory & File Dependencies

The script interacts with several local files and paths:

| File / Path | Type | Description |
| :--- | :--- | :--- |
| `security_auditor_memory_bank.json` | JSON Output/Input | Auto-created in `DESKTOP_PATH`. Stores long-term audit history. |
| `netcheck.ps1` | PowerShell Script | Executed to gather network diagnostic data. |
| `security_auditor_instructions.md` | Markdown Input | Optional system instructions/guidelines for the AI auditor. |
| `status.json` | JSON Output | Written after each run to signal system health state to external UI components. |

## Prerequisites

1. **Python 3.8+**
2. **Ollama Installed & Running:** Ensure Ollama is running locally.
3. **Pull Required Model:**
   Run `ollama run hf.co/jiunsong/supergemma4-26b-uncensored-gguf-v2:latest` in your terminal.
4. **Python Package Dependencies:**
   Run `pip install psutil python-dotenv ollama`

## Configuration

Update the paths defined in the script to match your local development environment:

**Memory Directory:**
`DESKTOP_PATH = r"C:\Path\To\Your\AI_Agent_Memory"`

**Network Diagnostics Script:**
`script_path = r"C:\Path\To\Your\NetworkTools\netcheck.ps1"`

## Usage

**1. Standard System & Network Audit**
To run a routine audit on system hardware and network status:
`python security_auditor.py`

**2. Audit with Email/Payload Inspection**
To pass a raw email file or threat payload for AI analysis, supply the file path as the first CLI argument:
`python security_auditor.py "C:\Path\To\suspicious_email.txt"`

## How It Works

1. **Data Gathering:** The script queries real-time CPU, RAM, and Disk metrics via `psutil` and invokes `netcheck.ps1` using PowerShell with `-ExecutionPolicy Bypass`.
2. **Context Assembly:** System health, network output, email text, custom markdown instructions, and the 5 most recent memory logs are compiled into a unified audit prompt.
3. **Local Inference:** The prompt is dispatched to the local Ollama instance.
4. **Threat Detection & Logging:**
   * If `CRITICAL`, `MALWARE`, `PHISHING`, or network `BLOCKED` keywords are flagged in the response, `status.json` updates to `"critical"`.
   * Otherwise, `status.json` updates to `"healthy"`.
   * The complete report is appended to `security_auditor_memory_bank.json`.# Local AI Security Auditor Agent

An offline, privacy-first cybersecurity monitoring agent powered by local LLM inference via Ollama. This tool analyzes system telemetry, runs local PowerShell network diagnostics, scans email payloads for threats, and maintains a persistent memory bank of historical security audits.

## Features

* **100% Offline & Private Analysis:** Executes threat audits locally using Ollama (`supergemma4-26b-uncensored-gguf-v2:latest`), ensuring sensitive hardware logs, network state, and email payloads are never transmitted to external cloud endpoints.
* **Real-Time Hardware Telemetry:** Collects system performance metrics (CPU usage, virtual memory, and root/drive disk space) using `psutil`.
* **Automated Network Diagnostics:** Triggers local PowerShell diagnostics (`netcheck.ps1`) via subprocess execution to inspect active network states and detected blockages.
* **Email & Payload Scanning:** Ingests raw text or email files passed via command-line arguments to analyze body text for phishing vectors, malicious links, or malware signatures.
* **Persistent Memory Bank:** Records audit results, timestamps, and status outcomes to a JSON file (`security_auditor_memory_bank.json`). The last 5 audit entries are dynamically injected into subsequent analysis prompts to provide historical context.
* **GUI Integration Ready:** Outputs automated state updates directly to `status.json` (`critical` vs. `healthy`) for seamless integration with frontend dashboards or status UI widgets.

## Directory & File Dependencies

The script interacts with several local files and paths:

| File / Path | Type | Description |
| :--- | :--- | :--- |
| `security_auditor_memory_bank.json` | JSON Output/Input | Auto-created in `DESKTOP_PATH`. Stores long-term audit history. |
| `netcheck.ps1` | PowerShell Script | Executed to gather network diagnostic data. |
| `security_auditor_instructions.md` | Markdown Input | Optional system instructions/guidelines for the AI auditor. |
| `status.json` | JSON Output | Written after each run to signal system health state to external UI components. |

## Prerequisites

1. **Python 3.8+**
2. **Ollama Installed & Running:** Ensure Ollama is running locally.
3. **Pull Required Model:**
   Run `ollama run hf.co/jiunsong/supergemma4-26b-uncensored-gguf-v2:latest` in your terminal.
4. **Python Package Dependencies:**
   Run `pip install psutil python-dotenv ollama`

## Configuration

Update the paths defined in the script to match your local development environment:

**Memory Directory:**
`DESKTOP_PATH = r"C:\Path\To\Your\AI_Agent_Memory"`

**Network Diagnostics Script:**
`script_path = r"C:\Path\To\Your\NetworkTools\netcheck.ps1"`

## Usage

**1. Standard System & Network Audit**
To run a routine audit on system hardware and network status:
`python security_auditor.py`

**2. Audit with Email/Payload Inspection**
To pass a raw email file or threat payload for AI analysis, supply the file path as the first CLI argument:
`python security_auditor.py "C:\Path\To\suspicious_email.txt"`

## How It Works

1. **Data Gathering:** The script queries real-time CPU, RAM, and Disk metrics via `psutil` and invokes `netcheck.ps1` using PowerShell with `-ExecutionPolicy Bypass`.
2. **Context Assembly:** System health, network output, email text, custom markdown instructions, and the 5 most recent memory logs are compiled into a unified audit prompt.
3. **Local Inference:** The prompt is dispatched to the local Ollama instance.
4. **Threat Detection & Logging:**
   * If `CRITICAL`, `MALWARE`, `PHISHING`, or network `BLOCKED` keywords are flagged in the response, `status.json` updates to `"critical"`.
   * Otherwise, `status.json` updates to `"healthy"`.
   * The complete report is appended to `security_auditor_memory_bank.json`.

# 🥷 Red Team Hacker Agent
## Automated Security Scanning & Remediation Bot

The **Red Team Hacker** is an advanced autonomous agent designed for proactive security auditing. It performs deep-dive vulnerability scans on local source code, identifies security flaws, and coordinates with the Software Engineer agent to perform automated, human-approved remediation.

---

## 🚀 Key Features

* **Intelligent File Vacuuming:** Intelligently crawls directories for source code files, respecting size limits and ignoring non-essential or hidden files to stay within token context windows.
* **Deep Security Scan:** Leverages Google Gemini to act as a penetration tester, identifying hardcoded credentials, injection vulnerabilities (SQL/Command), and dangerous logic flaws.
* **Two-Step Remediation Pipeline:** * **Scan Phase:** Produces a detailed tactical threat report.
    * **Patch Phase:** Routes the broken code to the Software Engineer for secure rewriting.
* **Human-in-the-Loop (HITL):** Uses secure, top-level Tkinter GUI windows to ensure no code is overwritten without your explicit authorization.
* **Safe Overwrite Protection:** Strips markdown artifacts from AI-generated code to prevent syntax errors and safely manages file writes.

---

## 🏗️ System Architecture



---

## 🛠️ Technical Stack

* **AI Engine:** Google Gemini (`gemini-2.5-flash-lite`) for rapid code analysis.
* **Security Logic:** Custom heuristic scanning for common code vulnerabilities.
* **GUI Layer:** `tkinter` for interactive threat reporting and patch verification.
* **Inter-Agent Protocol:** Direct module integration with `software_engineer.py` for automated patching.

---

## 📖 How to Use

### 1. Running a Scan
Trigger the agent by passing the file or directory path as an argument:
```bash
python red_team_hacker.py "Scan C:\my_project_folder"

# AI Software Engineer Agent

A locally-hosted, autonomous AI coding assistant powered by Ollama. This agent generates, tests, executes, and compiles Python code based on natural language prompts. It features a persistent memory system, self-healing syntax correction, and automated deployment capabilities.

## Features

* Autonomous Code Generation: Interfaces with local LLMs (default: qwen2.5:latest) via Ollama to write production-grade Python scripts.
* Persistent Memory System: Logs past tasks, outcomes, and lessons learned into a JSON memory bank. It injects relevant historical context into new prompts based on keyword relevance.
* Self-Healing Execution: Automatically runs a syntax check on generated code. If it fails, the agent feeds the error traceback back to the LLM to patch and fix its own code (up to 3 retries).
* Executable Compilation: Detects requests for standalone applications and automatically compiles the output into a Windows `.exe` using PyInstaller.
* Action Auditing: Maintains a detailed master manifest and audit trail of all generated files and agency actions.

## Prerequisites

* Python 3.8+
* Ollama (running locally at http://localhost:11434)
* A local LLM model pulled via Ollama (e.g., qwen2.5:latest)

## Configuration

Before running, update the configuration paths at the top of the script to match your local environment:

    OLLAMA_URL = "http://localhost:11434/api/generate"
    PYTHON_EXE = r"C:\path\to\your\python.exe" 
    DESKTOP_PATH = r"C:\path\to\your\Memory_Folder"
    DELIVERABLES_PATH = r"C:\path\to\your\Completed_Projects"

## Installation

1. Clone the repository and navigate into the directory.
2. Install the required dependencies using pip:
   
    pip install requests pygame pyinstaller

3. Ensure Ollama is running in the background.

## Usage

Run the agent script directly from your terminal:

    python software_engineer.py

Upon initialization, the system will verify directory paths and memory files. You will be prompted with:

    [!] Enter the coding task for the Software Engineer: 
    [?] Enter a custom filename (or press Enter for auto-timestamp): 

Provide your task. If you request an "executable" or an ".exe", the agent will automatically attempt to package the final script into your Deliverables folder.

## Architecture Highlights

* Memory Injection: Uses a custom `load_past_memory()` function that scores historical logs against current prompt keywords, ensuring the agent learns from previous syntax mistakes.
* Subprocess Execution: Uses `subprocess.run` to handle background execution and capture stdout/stderr for the self-correction loop.
* Dynamic Handoff: Alerts the user immediately upon successful compilation or script validation, providing exact file paths to the generated deliverables.

## License

Distributed under the MIT License.

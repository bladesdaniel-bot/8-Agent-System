# AI Graphic Designer Agent

## Overview
The AI Graphic Designer Agent is a local, Python-based automation script that bridges local LLM vision capabilities with ComfyUI's image generation workflow. It continuously monitors a designated input folder for new images, prompts the user for instructions, and processes the images using either a local Ollama vision model (LLaVA) for analysis or ComfyUI for generation and editing. 

A core feature of this agent is its **Memory System**, which logs all past tasks and outcomes. This allows the agent to maintain context and apply lessons learned to future vision prompts.

## Key Features
* **Directory Monitoring:** Automatically watches an input folder for new images (`.png`, `.jpg`, `.jpeg`).
* **Vision Analysis Mode:** Uses local Ollama (`llava`) to identify and deeply describe image contents, factoring in past memory logs.
* **ComfyUI Integration:** Sends user instructions directly into a predefined ComfyUI JSON workflow (dynamically updating Node #6's text prompt) and queues the job.
* **Persistent Memory Bank:** Saves a history of all tasks, outcomes, and success states to a local JSON file to give the vision agent ongoing context.
* **Auto-Cleanup:** Automatically moves processed images into a `processed` subfolder to prevent infinite loops.

## Prerequisites
To run this agent, you will need the following installed and running locally:

1. **Python 3.8+**
2. **ComfyUI:** Must be running locally (default: `http://127.0.0.1:8188`).
3. **Ollama:** Must be installed and running locally.
4. **LLaVA Model:** Pull the vision model via Ollama by running `ollama run llava` in your terminal.
5. **Python Packages:** 
   `pip install requests ollama`

## Configuration
Before running the script, update the directory paths in the **1. CONFIGURATION** and **2. MEMORY SYSTEM SETUP** sections of the code to match your local machine.

### Environment Variables
* `COMFYUI_URL`: The local URL of your ComfyUI instance (default: `http://127.0.0.1:8188`).
* `TARGET_DIR`: The output directory for finished ComfyUI images.
* `INPUT_DIR`: The folder the agent watches for new images.
* `WORKFLOW_PATH`: The absolute path to your exported ComfyUI `workflow_api.json` file.
* `DESKTOP_PATH`: The directory where the memory bank JSON will be saved.

### ComfyUI Workflow Requirements
This script assumes your ComfyUI workflow (`workflow_api.json`) is set up so that **Node "6"** is a Text/Prompt node. If your workflow uses a different node ID for the prompt, you must update the following line in the script:

if "6" in workflow:
    workflow["6"]["inputs"]["text"] = user_instructions


## How to Use

1. **Start your local servers:**
   Launch ComfyUI and ensure the Ollama application is running in the background.

2. **Run the script:**
   `python graphic_designer_agent.py`
   The terminal will display: `Graphic Designer Agent is running (ComfyUI + Vision Mode)...`

3. **Trigger the Agent:**
   Drop an image file (`.jpg`, `.png`) into your configured `INPUT_DIR`.

4. **Issue Commands:**
   The terminal will detect the image and pause, asking:
   `What do you want to do? >`
   
   * **To use Vision Analysis:** Type commands containing the words **"identify"** or **"what is"** (e.g., *"Identify the main subject in this image"*). The LLaVA model will analyze the image and output a description.
   * **To use ComfyUI:** Type any other generation/editing command. The script will inject your text into the ComfyUI workflow and queue the prompt.

5. **Review:**
   Once handled, the original image is moved to `INPUT_DIR/processed/`, and the interaction is permanently logged in the memory bank JSON.

## The Memory System
The script automatically generates a `graphic_designer_memory_bank.json` file. Every time an action is completed (whether a ComfyUI job is queued or an image is identified), the agent logs:
* Timestamp
* Task Requested
* Outcome (Job queued successfully, error message, or vision description)
* Success State (Boolean)

When you ask the agent to identify future images, the last 5 memory logs are injected into the Ollama prompt, allowing the agent to "remember" previous context and learn from past errors or ongoing project themes.

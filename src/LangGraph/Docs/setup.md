Setup Instructions for Modernized Adaptive Learning System
Project Overview
This project modernizes the Adaptive Learning system initially built using Microsoft Autogen and FSM-based orchestration. It transitions to a modular, testable, and schema-validated architecture using LangGraph and Pydantic, improving agent independence, system maintainability, and compatibility with modern AI development workflows. The redesign follows principles from Google’s ADK and Agent2Agent architectures.

The updated system integrates LangGraph-based agents with an interactive UI built on the Panel framework, allowing students to receive dynamic tutoring, code execution feedback, and learning performance analysis through a responsive and testable pipeline.
Prerequisites
• Python 3.12
• uv for dependency and virtual environment management
• Git
• WSL (Ubuntu 24.04) for Windows users or native Linux
• Docker Desktop (optional but recommended)
• Visual Studio Code
Installation Steps
1. Install WSL (for Windows)
   wsl --install -d Ubuntu-24.04
   Reboot the system after installation.

2. Install Required Linux Packages
   sudo apt update && sudo apt install -y \
   software-properties-common curl zip unzip tar ca-certificates \
   git wget build-essential vim jq firefox wslu

3. Install uv and Set Up Python Environment
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv venv --python 3.12
   source .venv/bin/activate

4. Clone the Repository
   git clone https://github.com/Rivier-Computer-Science/Adaptive-Learning.git
   cd Adaptive-Learning

5. Install Python Dependencies
   uv pip install -r requirements.txt
Environment Configuration
6. Set OpenAI API Key
   export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
   (Use set instead of export on Windows)


Running the Application
7. Launch the UI and LangGraph Workflow
   uv run python -m src.UI.panel_gui_tabs_jg
   This will open the Panel interface with the Learn tab.
Optional: Firebase Migration
To migrate user data:
   python migrate_firestore_users.py
   Ensure .env is properly configured before running.
Browser Settings for WSL
If browser does not auto-launch from WSL:
   sudo apt install wslu
   echo 'export BOKEH_BROWSER=wsluview' >> ~/.bashrc
Project Architecture Summary
The system uses LangGraph to orchestrate the following refactored agents:
- StudentAgent – Accepts input from the user via the Learn tab.
- CodeRunnerAgent – Executes submitted code and returns output or errors.
- KnowledgeTracerAgent – Analyzes performance history and estimates mastery.
- UI Agent – Interfaces with the Panel UI to display agent responses.

Each agent is implemented as a LangGraph node with strict Pydantic schemas for input/output validation. The overall graph execution is deterministic and schema-driven, with early validation halting malformed input. Agents can be independently tested with mock inputs.
Testing and Validation
• Unit tests are written for each agent using mock inputs
• Integration tests verify correct LangGraph pipeline execution
• Invalid input triggers Pydantic validation errors before execution
• UI refreshes correctly after each run, preserving learning flow
Documentation Components
This setup file is accompanied by:
- docs/student_agent.md
- docs/code_runner_agent.md
- docs/knowledge_tracer_agent.md
- docs/ui_integration.md
- docs/state_graph.md
- docs/architecture.png


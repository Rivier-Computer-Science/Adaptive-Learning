# 🧠 Final Project Summary – Adaptive Learning with LangGraph

##  Project Title
**Multi-Agent Adaptive Learning Interface using LangGraph and Panel**

## 👥 Team Members
- **Ramya Bandi** *(Developer, Documentation & Testing Lead)*

## 🎯 Project Objective
To build a prototype adaptive learning system powered by LangGraph that accepts student goals, evaluates Python code, and estimates mastery level using multi-agent coordination. This includes:
- LangGraph-based student agent, code runner, and knowledge tracer
- A dynamic Panel-based UI for goal submission and result visualization
- Test suite to validate pipeline execution
- Logging and error handling for edge-case analysis

---

## Sprint Summary

### **Sprint 1: Setup and Agent Initialization**
- Cloned and installed LangGraph with necessary dependencies
- Refactored `StudentAgent` and other components into LangGraph node format
- Created sample test payloads
- Committed to foundational pipeline execution

### **Sprint 2: Agent Integration and Routing**
- Connected all agents (Student, CodeRunner, KnowledgeTracer) via `langgraph_main.py`
- Validated LangGraph routing and fallback flow
- Added test coverage for each agent's standalone execution
- Refined logging for better debug visibility

### **Sprint 3: Documentation and Pipeline Test**
- Created step-by-step markdown docs:
  - `student_agent.md`, `code_runner_agent.md`, `knowledge_tracer_agent.md`
  - `UI_Integration.md`, `state_graph.md`
- Executed full pipeline tests using `test_pipeline_run.py`
- Added sample input with logging outputs
- Introduced README walkthrough structure

### **Sprint 4: UI Polish, Code Cleanup, Testing**
- Improved UI layout using Panel and widgets
- Added `Run Sample Goal` button for demos
- Polished code indentation, naming, and height adjustments
- Validated panel server launch and final LangGraph output

---

## 📂 Key Pull Requests

- [Sprint 1 PR: Refactor StudentAgent into LangGraph node](https://github.com/Rivier-Computer-Science/Adaptive-Learning/issues/397)
- [Sprint 2 PR: Refactor CodeRunnerAgent into LangGraph execution node](https://github.com/Rivier-Computer-Science/Adaptive-Learning/pull/439)
- [Sprint 3 PR: Pipeline Test + Docs](https://github.com/Rivier-Computer-Science/Adaptive-Learning/pull/459)
- [Sprint 4 PR: Final UI Polish + Test](https://github.com/Rivier-Computer-Science/Adaptive-Learning/pull/472)

---


### Pipeline Output

Final Result: Success
Student Agent: Goal 'Learn Loops' with priority High added.
Code Output: 0 1 2 3 4
Tracer Output: Status – Mastered, Mastery Level – 0.8


## Final Thoughts
This project demonstrates the power of composable AI agents using LangGraph in an educational context. The UI provides a clean interface for goal submission, while the backend coordinates response generation, code execution, and mastery tracking.

###  Lessons Learned
- Multi-agent coordination in LangGraph requires well-structured payloads and graceful fallbacks.
- Panel is powerful for fast UI prototyping with reactive outputs.
- Logs and error capture improved debugging during agent orchestration.

### Future Enhancements
- Integrate Firestore for persistent goal history
- Add support for multiple code languages
- Extend UI to show student progress charts over time

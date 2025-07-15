from src.Models.langgraph_state import LangGraphState

def run(state: LangGraphState) -> dict:
    print("⚠️ Fallback reached: invalid or failed state.")
    return {
        "tracer_output": None,
        "code_output": None,
        "student_input": state.student_input,
        "error": "Fallback: invalid input or failed code execution"
    }

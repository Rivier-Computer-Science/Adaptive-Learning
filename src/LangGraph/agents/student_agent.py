from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict
from src.Models.student_models import StudentInput, StudentOutput
from src.Models.code_models import CodeExecutionState
from src.Models.code_models import CodeExecutionState
from src.Models.langgraph_state import LangGraphState
from src.Models.knowledge_tracer_models import KnowledgeTracerState

def handle_student_input(input: Optional[StudentInput]) -> StudentOutput:
    if not input or not input.goal_name:
        return StudentOutput(message="Goal name is missing.", goal_added=False)

    return StudentOutput(
        message=f"Goal '{input.goal_name}' with priority {input.priority} added.",
        goal_added=True
    )



def run(state: LangGraphState) -> dict:
    # Forward student_input
    student_input = state.student_input

    # Simulated tracer input — just for demo
    dummy_tracer_input = KnowledgeTracerState(
        concept="Python Loops",
        correct_answers=8,
        total_questions=10
    )

    return {
        "student_input": student_input,
        "tracer_input": dummy_tracer_input  

    }



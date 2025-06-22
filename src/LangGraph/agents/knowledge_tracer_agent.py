from pydantic import BaseModel, Field
from typing import Optional
from langgraph.graph import StateGraph
from src.Models.knowledge_tracer_models import KnowledgeTracerState

class KnowledgeTracerOutput(BaseModel):
    concept : str
    mastery_level : float
    status : str # "mastered", "intermediate", "novice"

from src.Models.langgraph_state import LangGraphState  # ✅ import main state
from src.Models.knowledge_tracer_models import KnowledgeTracerState, KnowledgeTracerOutput

def run(state: LangGraphState) -> dict:
    tracer_input = state.tracer_input  # ✅ get it from LangGraph state
    if not tracer_input:
        return {"tracer_output": None}  # or raise a clear error

    accuracy = tracer_input.correct_answers / tracer_input.total_questions
    if accuracy >= 0.8:
        status = "mastered"
    elif accuracy >= 0.5:
        status = "intermediate"
    else:
        status = "beginner"

    output = KnowledgeTracerOutput(
        concept=tracer_input.concept,
        mastery_level=round(accuracy, 2),
        status=status
    )
    return {"tracer_output": output}



if __name__ == "__main__":
    # Sample input
    test_input = {
        "correct_answers": 7,
        "total_questions": 10,
        "concept" : "Fractions"
    }

    builder = StateGraph(KnowledgeTracerState)
    builder.add_node("KnowledgeTracerAgent", run)
    builder.set_entry_point("KnowledgeTracerAgent")
    graph = builder.compile()

    result = graph.invoke(test_input)

    print("LangGraph Result:", result.get("tracer_output"))  # ✅ should now print "mastered"

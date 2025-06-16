from pydantic import BaseModel, Field
from typing import Optional
from langgraph.graph import StateGraph

class KnowledgeTracerOutput(BaseModel):
    concept : str
    mastery_level : float
    status : str # "mastered", "Intermediate", "novice"

class KnowledgeTracerState(BaseModel):
    correct_answers: int = Field(..., ge=0)
    total_questions: int = Field(..., gt=0)
    concept : str = Field(..., description = "Concept being evaluated")
    output: Optional[KnowledgeTracerOutput] = None  # Required to store the result in LangGraph state


def run(state: KnowledgeTracerState) -> dict:
    accuracy = state.correct_answers / state.total_questions
    if accuracy >= 0.8:
        status = "mastered"
    elif accuracy >= 0.5:
        status = "intermediate"
    else:
        status = "beginner"
    output = KnowledgeTracerOutput(
        concept = state.concept,
        mastery_level = round(accuracy, 2),
        status = status
    )
    return {
            "output" : output
            }

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

    print("LangGraph Result:", result.get("output"))  # ✅ should now print "mastered"

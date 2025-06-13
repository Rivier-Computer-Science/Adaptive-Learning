from pydantic import BaseModel, Field
from typing import Optional
from langgraph.graph import StateGraph

class KnowledgeTracerState(BaseModel):
    correct_answers: int = Field(..., ge=0)
    total_questions: int = Field(..., gt=0)
    output: Optional[str] = None  # Required to store the result in LangGraph state

def run(state: KnowledgeTracerState) -> dict:
    accuracy = state.correct_answers / state.total_questions
    if accuracy >= 0.8:
        mastery = "mastered"
    elif accuracy >= 0.5:
        mastery = "intermediate"
    else:
        mastery = "beginner"
    return {"output": mastery}

if __name__ == "__main__":
    # Sample input
    test_input = {
        "correct_answers": 7,
        "total_questions": 10
    }

    builder = StateGraph(KnowledgeTracerState)
    builder.add_node("KnowledgeTracerAgent", run)
    builder.set_entry_point("KnowledgeTracerAgent")
    graph = builder.compile()

    result = graph.invoke(test_input)

    print("LangGraph Result:", result.get("output"))  # ✅ should now print "mastered"

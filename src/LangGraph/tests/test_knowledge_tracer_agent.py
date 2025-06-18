from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from langgraph.graph import StateGraph

# --- Define output schema
class KnowledgeTracerOutput(BaseModel):
    concept: str
    mastery_level: float
    status: str  # "mastered", "intermediate", "beginner"

# --- Define agent state
class KnowledgeTracerState(BaseModel):
    correct_answers: int = Field(..., ge=0)
    total_questions: int = Field(..., gt=0)
    concept: str
    output: Optional[KnowledgeTracerOutput] = None

# --- KnowledgeTracerAgent logic
def run(state: KnowledgeTracerState) -> dict:
    accuracy = state.correct_answers / state.total_questions
    if accuracy >= 0.8:
        status = "mastered"
    elif accuracy >= 0.5:
        status = "intermediate"
    else:
        status = "beginner"
    output = KnowledgeTracerOutput(
        concept=state.concept,
        mastery_level=round(accuracy, 2),
        status=status
    )
    return {"output": output}

# --- Unit Tests
def test_knowledge_tracer():
    test_cases = [
        {"correct_answers": 8, "total_questions": 10, "concept": "Algebra", "expected_status": "mastered"},
        {"correct_answers": 5, "total_questions": 10, "concept": "Geometry", "expected_status": "intermediate"},
        {"correct_answers": 2, "total_questions": 10, "concept": "Calculus", "expected_status": "beginner"},
        {"correct_answers": 0, "total_questions": 10, "concept": "Trigonometry", "expected_status": "beginner"},
        {"correct_answers": 10, "total_questions": 10, "concept": "Statistics", "expected_status": "mastered"}
    ]

    for case in test_cases:
        state = KnowledgeTracerState(**{k: case[k] for k in ["correct_answers", "total_questions", "concept"]})
        result = run(state)
        output = result["output"]
        assert isinstance(output, KnowledgeTracerOutput), "Output must match schema"
        assert output.status == case["expected_status"], f"Expected {case['expected_status']} but got {output.status}"
        print(f"Passed for {case['concept']} -> {output.status} with mastery level {output.mastery_level}")

# --- Integration Test using LangGraph
def test_langgraph_integration():
    builder = StateGraph(KnowledgeTracerState)
    builder.add_node("KnowledgeTracerAgent", run)
    builder.set_entry_point("KnowledgeTracerAgent")
    graph = builder.compile()

    sample_input = {
        "correct_answers": 6,
        "total_questions": 10,
        "concept": "Fractions"
    }

    result = graph.invoke(sample_input)
    output = result.get("output")
    assert output.status == "intermediate"
    print("LangGraph integration test passed:", output)

# --- Run all tests
if __name__ == "__main__":
    print("Running unit tests...")
    test_knowledge_tracer()
    print("\nRunning integration test...")
    test_langgraph_integration()

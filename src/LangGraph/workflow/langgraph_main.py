from langgraph.graph import StateGraph
from src.LangGraph.student_agent_node import run, StudentInput

builder = StateGraph(StudentInput)
builder.add_node("StudentAgent", run)
builder.set_entry_point("StudentAgent")
graph = builder.compile()

# Test invocation
output = graph.invoke({
    "goal_name": "Learn Python",
    "description": "Complete Python basics",
    "target_date": "2024-12-01T00:00:00",
    "priority": "High",
    "category": "Programming"
})

print(output)

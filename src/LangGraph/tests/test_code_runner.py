from src.LangGraph.agents.code_runner_agent import run, CodeExecutionInput
from langgraph.graph import StateGraph

# Define the graph node
builder = StateGraph(CodeExecutionInput)
builder.add_node("CodeRunnerAgent", run)
builder.set_entry_point("CodeRunnerAgent")
graph = builder.compile()

if __name__ == "__main__":
    test_input = {
        "code": "x = 2 + 3\nprint(x)"
    }

    result = graph.invoke(test_input)
    print("Graph Output Keys:", result.keys())
    print("Full Graph Result:", result)


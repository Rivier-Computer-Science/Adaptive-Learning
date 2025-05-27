from langgraph.graph import StateGraph
from src.Agents.scenario_input_agent import run as scenario_input, ScenarioInput

# Define the LangGraph
builder = StateGraph(ScenarioInput)
builder.add_node("ScenarioInputAgent", scenario_input)
builder.set_entry_point("ScenarioInputAgent")

graph = builder.compile()

if __name__ == "__main__":
    # Test input
    input_data = {"scenario": "Increase topic difficulty"}
    output = graph.invoke(input_data)
    print(output)

from langgraph.graph import StateGraph
from src.LangGraph.agents.student_agent import run as run_student
from src.LangGraph.agents.code_runner_agent import run as run_code_runner
from src.LangGraph.agents.knowledge_tracer_agent import run as run_knowledge_tracer
from src.Models.langgraph_state import LangGraphState
from src.LangGraph.agents.failure_handler_agent import run as failure_handler

# builder.add_edge("StudentAgent", "CodeRunnerAgent")
# builder.add_edge("CodeRunnerAgent", "KnowledgeTracerAgent")

# Route from StudentAgent to CodeRunner or Failure
def route_after_student_agent(state: LangGraphState) -> str:
    if not state.student_input or not state.student_input.goal_name.strip():
        return "FailureHandler"
    return "CodeRunnerAgent"

# Route from CodeRunnerAgent to KnowledgeTracerAgent or Failure
def route_after_code_runner(state: LangGraphState) -> str:
    if not state.code_output or not state.code_output.success:
        return "FailureHandler"
    return "KnowledgeTracerAgent"
# Define and compile the LangGraph, but DO NOT invoke it here
builder = StateGraph(LangGraphState)
builder.add_node("StudentAgent", run_student)
builder.add_node("CodeRunnerAgent", run_code_runner)
builder.add_node("KnowledgeTracerAgent", run_knowledge_tracer)
builder.add_node("FailureHandler", failure_handler)

builder.set_entry_point("StudentAgent")
builder.add_conditional_edges(
    "StudentAgent",
    route_after_student_agent,
    {
        "CodeRunnerAgent": "CodeRunnerAgent",
        "FailureHandler": "FailureHandler"
    }
)

builder.add_conditional_edges(
    "CodeRunnerAgent",
    route_after_code_runner,
    {
        "KnowledgeTracerAgent": "KnowledgeTracerAgent",
        "FailureHandler": "FailureHandler"
    }
)

graph = builder.compile()

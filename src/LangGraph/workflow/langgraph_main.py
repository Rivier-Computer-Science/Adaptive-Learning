from langgraph.graph import StateGraph
from src.LangGraph.agents.student_agent import run as run_student
from src.LangGraph.agents.code_runner_agent import run as run_code_runner
from src.LangGraph.agents.knowledge_tracer_agent import run as run_knowledge_tracer
from src.Models.langgraph_state import LangGraphState

# Define and compile the LangGraph, but DO NOT invoke it here
builder = StateGraph(LangGraphState)
builder.add_node("StudentAgent", run_student)
builder.add_node("CodeRunnerAgent", run_code_runner)
builder.add_node("KnowledgeTracerAgent", run_knowledge_tracer)

builder.set_entry_point("StudentAgent")
builder.add_edge("StudentAgent", "CodeRunnerAgent")
builder.add_edge("CodeRunnerAgent", "KnowledgeTracerAgent")

graph = builder.compile()

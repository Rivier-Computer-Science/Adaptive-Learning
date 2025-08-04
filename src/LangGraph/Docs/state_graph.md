# LangGraph StateGraph Documentation

## Overview

The LangGraph `StateGraph` replaces the legacy FSM (TeachMeFSM) with a modern, modular graph-based orchestration system. It composes agents as reusable nodes with deterministic routing logic and state transition management. The graph determines the path of execution based on dynamic state evaluation, enabling robust error handling and adaptive learning flows.

## Purpose

- Replace finite state machine logic with LangGraph-based dynamic routing
- Model agents as independent, testable graph nodes
- Define conditional transitions using state-based functions
- Allow scalable, readable, and maintainable multi-agent orchestration

## LangGraph Role

The `StateGraph` defines the full execution pipeline:
1. Starts with the `StudentAgent`
2. Routes conditionally to the `CodeRunnerAgent` or `FailureHandler`
3. From `CodeRunnerAgent`, proceeds to `KnowledgeTracerAgent` or `FailureHandler`
4. Uses clearly defined node functions and routing logic
5. Terminates after reaching final nodes

## State Definition

Defined in: `src/Models/langgraph_state.py`

```
class LangGraphState(BaseModel):
    student_input: Optional[StudentInput] = None
    code_input: Optional[str] = None
    code_output: Optional[CodeExecutionState] = None    
    tracer_input: Optional[KnowledgeTracerState] = None  
    tracer_output: Optional[KnowledgeTracerOutput] = None
    error: Optional[str] = None
    student_output: Optional[StudentOutput] = None
```

This class holds shared state between all graph nodes.

## Graph Structure

Located in: `src/LangGraph/workflow.py` (or equivalent)

### Node Registration

```
builder = StateGraph(LangGraphState)
builder.add_node("StudentAgent", run_student)
builder.add_node("CodeRunnerAgent", run_code_runner)
builder.add_node("KnowledgeTracerAgent", run_knowledge_tracer)
builder.add_node("FailureHandler", failure_handler)
```

### Entry Point

```
builder.set_entry_point("StudentAgent")
```

### Conditional Routing

From StudentAgent:

```
def route_after_student_agent(state: LangGraphState) -> str:
    if not state.student_input or not state.student_input.goal_name.strip():
        return "FailureHandler"
    return "CodeRunnerAgent"

builder.add_conditional_edges(
    "StudentAgent",
    route_after_student_agent,
    {
        "CodeRunnerAgent": "CodeRunnerAgent",
        "FailureHandler": "FailureHandler"
    }
)
```

From CodeRunnerAgent:

```
def route_after_code_runner(state: LangGraphState) -> str:
    if not state.code_output or not state.code_output.success:
        return "FailureHandler"
    return "KnowledgeTracerAgent"

builder.add_conditional_edges(
    "CodeRunnerAgent",
    route_after_code_runner,
    {
        "KnowledgeTracerAgent": "KnowledgeTracerAgent",
        "FailureHandler": "FailureHandler"
    }
)
```

### Compile the Graph

```
graph = builder.compile()
```

## Commit History

- 06/22/2025 – MMA.4.1: Replaced FSM with LangGraph StateGraph
- 06/23/2025 – MMA.4.2: Composed multi-agent pipeline with conditional routing

## Notes

- Each node function must return updated state with expected keys
- Conditional logic is extensible to support future agents
- The graph ensures resilience by routing errors to a `FailureHandler` node

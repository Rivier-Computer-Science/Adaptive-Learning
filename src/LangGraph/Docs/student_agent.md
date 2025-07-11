# StudentAgent Documentation

## Overview

The `StudentAgent` is responsible for capturing and validating user input related to learning goals. It acts as the entry point in the LangGraph workflow and simulates interaction with downstream agents such as the `KnowledgeTracerAgent`. This agent was refactored from legacy FSM/Autogen logic to a LangGraph-compatible node with clear schema validation using Pydantic.

This agent is modular, independently testable, and designed to produce schema-compliant output for downstream processing.

## Purpose

- Receive structured user input (e.g., learning goals)
- Validate the presence of required fields
- Forward input along with simulated tracer data to the next agent
- Generate structured feedback messages

## LangGraph Role

The `StudentAgent` functions as the **starting node** in the LangGraph-based adaptive learning workflow. It prepares initial state for downstream components and ensures that the user’s learning intent is correctly captured and structured.

## Input Schema (`StudentInput`)

Defined in: `src/Models/student_models.py`

```
class StudentInput(BaseModel):
    goal_name: str
    description: str
    target_date: datetime
    priority: str
    category: str
```

## Output Schema (`StudentOutput`)

Defined in: `src/Models/student_models.py`

```
class StudentOutput(BaseModel):
    message: str
    goal_added: bool
```

## Agent Logic

Located in: `src/LangGraph/agents/student_agent.py`

### Handler Function

```
def handle_student_input(input: Optional[StudentInput]) -> StudentOutput:
    if not input or not input.goal_name:
        return StudentOutput(message="Goal name is missing.", goal_added=False)

    return StudentOutput(
        message=f"Goal '{input.goal_name}' with priority {input.priority} added.",
        goal_added=True
    )
```

### LangGraph Node Wrapper

```
def run(state: LangGraphState) -> dict:
    student_input = state.student_input
    student_output = handle_student_input(student_input)

    dummy_tracer_input = KnowledgeTracerState(
        concept="Python Loops",
        correct_answers=8,
        total_questions=10
    )

    return {
        "student_input": student_input,
        "tracer_input": dummy_tracer_input,
        "student_output": student_output
    }
```

## Unit Tests

Located in: `src/LangGraph/tests/test_student_agent.py`

### Test Cases

- **Valid Input Test** – Ensures goal is added correctly
- **Missing Goal Name** – Returns appropriate error message
- **LangGraph Run Wrapper** – Confirms input passthrough and tracer simulation

Sample:

```
def test_valid_input(self):
    input_data = StudentInput(
        goal_name="Learn Algebra",
        description="Master algebra basics",
        target_date=datetime(2024, 12, 1),
        priority="High",
        category="Math"
    )
    output = handle_student_input(input_data)
    self.assertTrue(output.goal_added)
```

Run with:

```
pytest src/LangGraph/tests/test_student_agent.py
```

## Commit History

- **5/27/2025** – MMA.1.1: Refactored agent to LangGraph node
- **5/29/2025** – MMA.1.2: Defined Pydantic schemas
- **6/1/2025** – MMA.1.3: Unit test coverage added
- **6/5/2025** – MMA.1.4: Output validated against schema

## Notes

- This agent currently simulates downstream KnowledgeTracer input.
- Goal validation is limited to the presence of `goal_name`; deeper validation (e.g., future date, valid category) is deferred to future tasks.
- The agent is compatible with UI integration via the LangGraph pipeline.

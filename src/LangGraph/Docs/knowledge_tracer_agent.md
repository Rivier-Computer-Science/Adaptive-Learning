# KnowledgeTracerAgent Documentation

## Overview

The `KnowledgeTracerAgent` evaluates a student's conceptual understanding by analyzing their performance on exercises. It calculates a mastery level score and assigns a mastery status label ("mastered", "intermediate", or "beginner") based on accuracy. The agent is integrated into the LangGraph pipeline and produces schema-compliant structured output.

## Purpose

- Accept student performance input (correct answers, total questions, and concept)
- Calculate mastery level (accuracy)
- Return a standardized output with mastery status
- Enable conditional branching in the LangGraph pipeline based on understanding

## LangGraph Role

This agent processes the output of the StudentAgent or other logic-driven steps. Its results can be used to drive adaptive content delivery, feedback generation, or performance tracking.

## Input Schema (`KnowledgeTracerState`)

Defined in: `src/Models/knowledge_tracer_models.py`

```
class KnowledgeTracerState(BaseModel):
    correct_answers: int
    total_questions: int
    concept: str
    tracer_output: Optional[KnowledgeTracerOutput] = None
```

## Output Schema (`KnowledgeTracerOutput`)

Defined in: `src/Models/knowledge_tracer_models.py`

```
class KnowledgeTracerOutput(BaseModel):
    concept: str
    mastery_level: float
    status: str  # "mastered", "intermediate", "beginner"
```

## Agent Logic

Located in: `src/LangGraph/agents/knowledge_tracer_agent.py`

```
def run(state: LangGraphState) -> dict:
    tracer_input = state.tracer_input
    if not tracer_input:
        return {"tracer_output": None}

    accuracy = tracer_input.correct_answers / tracer_input.total_questions
    if accuracy >= 0.8:
        status = "mastered"
    elif accuracy >= 0.5:
        status = "intermediate"
    else:
        status = "beginner"

    output = KnowledgeTracerOutput(
        concept=tracer_input.concept,
        mastery_level=round(accuracy, 2),
        status=status
    )
    return {"tracer_output": output}
```

## Unit Tests

Located in: `src/LangGraph/tests/test_knowledge_tracer_agent.py`

### Test Cases

- Mastered level: ≥ 80% correct answers
- Intermediate level: 50–79%
- Beginner level: < 50%
- Handles missing input gracefully

Example:

```
def test_mastered_level(self):
    state = LangGraphState(
        tracer_input=KnowledgeTracerState(
            correct_answers=9,
            total_questions=10,
            concept="Algebra"
        )
    )
    result = run(state)
    output: KnowledgeTracerOutput = result["tracer_output"]
    self.assertEqual(output.status, "mastered")
    self.assertAlmostEqual(output.mastery_level, 0.9)
    self.assertEqual(output.concept, "Algebra")
```

Run with:

```
pytest src/LangGraph/tests/test_knowledge_tracer_agent.py
```

## Commit History

- 06/12/2025 – MMA.3.1: Refactored KnowledgeTracerAgent into LangGraph node
- 06/15/2025 – MMA.3.2: Defined mastery output schema
- 06/17/2025 – MMA.3.3: Validated logic using quiz simulation data

## Notes

- Agent logic assumes valid `total_questions` > 0. Add defensive checks in future versions.
- Output is Pydantic-compliant for downstream processing.
- Easily extendable to add difficulty-based mastery or time-based metrics.

# CodeRunnerAgent Documentation

## Overview

The `CodeRunnerAgent` is responsible for securely executing Python code within the LangGraph pipeline. It replaces the legacy execution logic with a modular LangGraph node that includes error handling and structured output. The agent uses a Pydantic model to validate and return the code execution results, including standard output, standard error, and success flags.

## Purpose

- Accept Python code as input from the LangGraph state
- Run the code using Python's subprocess module in a safe, time-bounded environment
- Return structured output including:
  - The original code
  - stdout
  - stderr
  - execution success status

## LangGraph Role

This agent is invoked after student input or programmer agent output when code execution is required. It is encapsulated in a LangGraph node and returns its output in the form of a CodeExecutionState.

## Input

The agent consumes the `code_input` field from the LangGraph state, which is a string of Python code.

## Output Schema (`CodeExecutionState`)

Defined in: `src/Models/code_models.py`

```
class CodeExecutionState(BaseModel):
    code: str
    stdout: Optional[str]
    stderr: Optional[str]
    success: Optional[bool]
```

Includes validation to ensure code is not empty.

## Agent Logic

Located in: `src/LangGraph/agents/code_runner_agent.py`

```
def run(state: LangGraphState) -> dict:
    code = state.code_input or ""
    if not code.strip():
        return {
            "code_output": CodeExecutionState(
                code="",
                stdout=None,
                stderr="Code is empty",
                success=False
            )
        }

    try:
        import subprocess
        result = subprocess.run(["python3", "-c", code], capture_output=True, text=True, timeout=5)
        return {
            "code_output": CodeExecutionState(
                code=code,
                stdout=result.stdout.strip() or None,
                stderr=result.stderr.strip() or None,
                success=result.returncode == 0
            )
        }
    except subprocess.TimeoutExpired:
        return {
            "code_output": CodeExecutionState(
                code=code,
                stdout=None,
                stderr="Execution timed out",
                success=False
            )
        }
    except Exception as e:
        return {
            "code_output": CodeExecutionState(
                code=code,
                stdout=None,
                stderr=str(e),
                success=False
            )
        }
```

## Unit Tests

Located in: `src/LangGraph/tests/test_code_runner_agent.py`

### Test Cases

- Valid Python code returns success with expected stdout
- Invalid Python code returns syntax error in stderr
- Infinite loop times out after 5 seconds

```
def test_valid_code(self):
    state = LangGraphState(code_input="print('Hello')")
    result = run(state)
    self.assertTrue(result["code_output"].success)
    self.assertEqual(result["code_output"].stdout, "Hello")
    self.assertIsNone(result["code_output"].stderr)
```

Run with:

```
pytest src/LangGraph/tests/test_code_runner_agent.py
```

## Commit History

- 06/08/2025 – MMA.2.1: Refactored CodeRunnerAgent into LangGraph node
- 06/08/2025 – MMA.2.2: Defined schema and error handling
- 06/10/2025 – MMA.2.3: Completed unit test coverage

## Notes

- The agent uses a strict timeout of 5 seconds to prevent long-running or infinite code blocks.
- Errors such as syntax issues or exceptions are captured in `stderr`.
- Output is fully schema-compliant for downstream agents or UI rendering.

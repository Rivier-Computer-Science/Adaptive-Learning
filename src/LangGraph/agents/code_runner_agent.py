from pydantic import BaseModel, Field, field_validator
from typing import Optional
import subprocess

# Combined state model: includes both input and output
class CodeExecutionState(BaseModel):
    code: str = Field(..., description="Python code to execute")
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    success: Optional[bool] = None

    @field_validator("code")
    @classmethod
    def check_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty")
        return v

# Execution logic for LangGraph node
def run(state: CodeExecutionState) -> dict:
    try:
        process = subprocess.run(
            ["python3", "-c", state.code],
            capture_output=True,
            text=True,
            timeout=5
        )
        return {
            "stdout": process.stdout.strip() if process.stdout else None,
            "stderr": process.stderr.strip() if process.stderr else None,
            "success": process.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"stdout": None, "stderr": "Execution timed out", "success": False}
    except Exception as e:
        return {"stdout": None, "stderr": str(e), "success": False}

# Test execution using LangGraph
if __name__ == "__main__":
    from langgraph.graph import StateGraph

    test_input = {
        "code": "x = 5 + 7\nprint('Result:', x)"
    }

    builder = StateGraph(CodeExecutionState)
    builder.add_node("CodeRunnerAgent", run)
    builder.set_entry_point("CodeRunnerAgent")
    graph = builder.compile()

    result = graph.invoke(test_input)

    print("Graph Output Keys:", result.keys())
    print("Execution Result:")
    print("Stdout:", result.get("stdout"))
    print("Stderr:", result.get("stderr"))
    print("Success:", result.get("success"))

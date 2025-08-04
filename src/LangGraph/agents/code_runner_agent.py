from subprocess import run as subprocess_run, TimeoutExpired
from typing import Dict
from src.Models.code_models import CodeExecutionState  # ✅ updated import
from src.Models.langgraph_state import LangGraphState 

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


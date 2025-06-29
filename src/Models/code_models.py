
from pydantic import BaseModel, Field, field_validator
from typing import Optional

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

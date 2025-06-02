from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudentInput(BaseModel):
    goal_name: str
    description: str
    target_date: datetime
    priority: str
    category: str

class StudentOutput(BaseModel):
    message: str
    goal_added: bool

def run(input: StudentInput) -> StudentOutput:
    # Simulate logic from add_goal()
    if not input.goal_name:
        return StudentOutput(message="Goal name is missing.", goal_added=False)
    
    # Imagine storing or processing this goal
    return StudentOutput(
        message=f"Goal '{input.goal_name}' with priority {input.priority} added.",
        goal_added=True
    )

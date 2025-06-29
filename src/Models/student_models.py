# src/Models/student_models.py
from pydantic import BaseModel
from datetime import datetime

class StudentInput(BaseModel):
    goal_name: str
    description: str
    target_date: datetime
    priority: str
    category: str

class StudentOutput(BaseModel):
    message: str
    goal_added: bool

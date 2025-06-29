from pydantic import BaseModel, Field
from typing import Optional

class KnowledgeTracerOutput(BaseModel):
    concept: str
    mastery_level: float
    status: str  # "mastered", "intermediate", "beginner"

class KnowledgeTracerState(BaseModel):
    correct_answers: int = Field(..., description="Number of correct answers")
    total_questions: int = Field(..., description="Total number of questions answered")
    concept: str = Field(..., description="Concept being evaluated")
    tracer_output: Optional[KnowledgeTracerOutput] = None

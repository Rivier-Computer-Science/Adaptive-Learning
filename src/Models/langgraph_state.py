from pydantic import BaseModel
from typing import Optional 
from src.Models.code_models import CodeExecutionState
from src.Models.student_models import StudentInput, StudentOutput
from src.Models.knowledge_tracer_models import KnowledgeTracerState, KnowledgeTracerOutput



class LangGraphState(BaseModel):
    student_input: Optional[StudentInput] = None
    code_input: Optional[str] = None
    code_output: Optional[CodeExecutionState] = None    
    tracer_input: Optional[KnowledgeTracerState] = None  
    tracer_output: Optional[KnowledgeTracerOutput] = None
    error: Optional[str] = None
    student_output: Optional[StudentOutput] = None


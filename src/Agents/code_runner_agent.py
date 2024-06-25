##################### Code Runner #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class CodeRunnerAgent(MyConversableAgent):  
    description = """
            CodeRunnerAgent is a proficient and efficient assistant specialized in executing Python code.
            When asked, you execute the Python code.
            """
    
    system_message = """
            You are CodeRunnerAgent, a Python code execution assistant. 
            When asked, you execute the Python code.
             """
    def __init__(self, **kwargs):
        super().__init__(
            name="CodeRunnerAgent",
            code_execution_config={"last_n_messages": 2, "work_dir": "coding"},
            human_input_mode="NEVER",
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )
##################### Problem Generator #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class ProblemGeneratorAgent(MyConversableAgent):
    description = """
                        You generate math problems at the appropriate level for the Student. 
                        You ask the Level Adapter for the level of difficulty and generate a question.
                        You display the question to the Student.
                        You ask the Student to provide human input to answer the question.
                        You only talk with the Student and Level Adapter. 
                 """
    def __init__(self):
        super().__init__(
                name="ProblemGenerator",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )    
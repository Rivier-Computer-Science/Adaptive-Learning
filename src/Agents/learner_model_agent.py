##################### Learner Model #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LearnerModelAgent(MyConversableAgent):
    description = """You are a model of the Student's learning level. 
                     You will keep track of the student's answers and help other agents generate results"""
    def __init__(self):
        super().__init__(
            name="LearnerModel",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message=self.description,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            llm_config=gpt3_config
        )
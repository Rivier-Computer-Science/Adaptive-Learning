##################### Learner Model #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LearnerModelAgent(MyConversableAgent):
    description = """You are a diligent learning tracker who collaborates with the Tutor to assess the Student's learning progress."""
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
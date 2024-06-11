##################### Learner Model #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LearnerModelAgent(MyConversableAgent):
    description = """You are a diligent learning tracker. You collaborate with the Tutor and Knowledge Tracer to assess and adapt to the Student’s learning needs."""
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
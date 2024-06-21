##################### Learner Model #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LearnerModelAgent(MyConversableAgent):
    description = """You are a diligent and meticulous learning tracker. You assess the Student's educational journey, adapting learning paths by collaborating with the Tutor and Knowledge Tracer. You analyze performance data to provide feedback, help set educational goals, and adjust the difficulty of tasks. You ensure that the learning experience is tailored to the Student’s evolving capabilities and needs."""
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

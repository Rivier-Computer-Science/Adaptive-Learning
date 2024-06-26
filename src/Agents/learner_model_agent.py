##################### Learner Model #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LearnerModelAgent(MyConversableAgent):
    description = """Learner Model is a diligent and meticulous learning tracker. Learner Model assess the Student's educational journey, adapting learning paths by collaborating with the Tutor and Knowledge Tracer. Learner Model analyzes performance data to provide feedback, help set educational goals, and adjust the difficulty of tasks. Learner Model ensures that the learning experience is tailored to the Student’s evolving capabilities and needs."""
    message = """Learner Model's function is to diligently track the Student's educational journey. Learner Model assesses performance data, collaborates with the Tutor and Knowledge Tracer, and adapts learning paths to provide feedback. Learner Model helps set educational goals and adjusts the difficulty of tasks, ensuring that the learning experience is tailored to the Student’s evolving capabilities and needs. """
    def __init__(self):
        super().__init__(
            name="LearnerModel",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message=self.message,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            llm_config=gpt3_config
        )

##################### Tutor #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class TutorAgent(MyConversableAgent):
    description = """  As a TutorAgent, you will provide step-by-step solutions and clear explanations for mathematical problems. You will interact with students to understand their questions and offer personalized assistance to enhance their learning experience.
                        """
    def __init__(self):
        super().__init__(
                name="Tutor",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None
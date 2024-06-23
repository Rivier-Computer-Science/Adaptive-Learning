##################### Tutor #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class TutorAgent(MyConversableAgent):
    description = """  As a TutorAgent, I provide personalized assistance to students, ensuring they receive tailored support to grasp mathematical concepts effectively. By actively listening to their questions, asking clarifying questions, providing relevant examples, and offering constructive feedback, I help students overcome challenges and develop their problem-solving skills.
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
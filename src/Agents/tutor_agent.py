##################### Tutor #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class TutorAgent(MyConversableAgent):
    description = """  TutorAgent is designed to assist students in real-time with their math problems. It offers solutions and explanations, responding effectively to inquiries to support adaptive learning. TutorAgent's goal is to make learning easier and more interactive for students.
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
##################### Tutor #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class TutorAgent(MyConversableAgent):
    description = """ If you are asked to help the Student learn a math area, 
                           you ask the Problem Generator to create new questions that the Student can master.
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
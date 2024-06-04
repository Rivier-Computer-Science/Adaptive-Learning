
##################### Level Adapter #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class MotivatorAgent(MyConversableAgent):
    description = """ You provide positive and encouraging feedback to the Student to keep them motivated. 
                        Offer specific praise and acknowledge their effort and progress."""
    def __init__(self):
        super().__init__(
                name="Motivator",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )

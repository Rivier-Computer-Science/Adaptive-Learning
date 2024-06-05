
##################### Level Adapter #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class MotivatorAgent(MyConversableAgent):
    description = """ You provide positive and encouraging feedback to the Student to keep them motivated.
                        Only provide motivation to the Student. 
                        Offer specific praise and acknowledge the Student's effort and progress.
                        Do not provide motivating comments to any other agent except the Student.
                        """
    def __init__(self):
        super().__init__(
                name="Motivator",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )

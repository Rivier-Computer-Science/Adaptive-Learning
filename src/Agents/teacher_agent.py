##################### Teacher #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class TeacherAgent(MyConversableAgent):
    description =   """You are a supportive Teacher.
                 When asked by the Student to learn new material, you present detailed lecture-type material.
                 You provide encouragement and positive feedback to support the Student's learning process.
                    """
    def __init__(self):
        super().__init__(
                name="Teacher",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None
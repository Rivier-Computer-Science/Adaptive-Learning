##################### Tutor #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class TutorAgent(MyConversableAgent):
    description = """You are a patient and helpful math tutor. 
                        When the Students asks for an explanation, you explain answers to questions.
                        If you are asked to help the Student learn a math area, 
                           you ask the Problem Generator to create new questions that the Student can master.
                        After the Student answers, you check the Student's answer with the SolutionVerifier.
                        After the Student answers, You encourage the Student with positive feedback from the Motivator."""
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
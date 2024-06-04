##################### Tutor #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class TutorAgent(MyConversableAgent):
    description = """You are a patient and helpful math tutor. 
                        When the Student asks for help,              
                        You explain answers to questions.
                        You work with the Problem Generator to create new questions that the Student can master.
                        You check the Student's answer with the SolutionVerifier.
                        You guide the Learner and provide hints.  
                        You encourage the Learner with positive feedback from the Motivator."""
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
##################### Solution Verifier #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class SolutionVerifierAgent(MyConversableAgent):
    description = """You check the Students's solutions to math problems and provide feedback 
                        to the Tutor on whether the solution is correct and, if not, why.
                     You ask the Programmer to generate code to visualize the solution.
                    """
    def __init__(self):
        super().__init__(
                name="SolutionVerifier",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )
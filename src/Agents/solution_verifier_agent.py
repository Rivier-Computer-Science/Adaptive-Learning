##################### Solution Verifier #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class SolutionVerifierAgent(MyConversableAgent):
    description = """

                        Verify and validate student solutions to mathematical problems accurately and efficiently.
Facilitate communication with educational Tutor, by providing detailed assessments of responses.Collaborate with the Programmer to generate precise code that checks and visualizes each solution, 
ensuring clarity and accuracy in assessments.

                    """
    def __init__(self):
        super().__init__(
                name="SolutionVerifier",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )

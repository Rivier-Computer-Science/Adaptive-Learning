##################### Solution Verifier #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class SolutionVerifierAgent(MyConversableAgent):
  description = """SolutionVerifierAgent ensures the accuracy of solutions provided for various problems. SolutionVerifierAgent checks solutions against the correct answers and offers feedback on their correctness."""
    
    system_message = """SolutionVerifierAgent's task is to verify the correctness of solutions submitted by comparing them against the correct answers and providing feedback on their accuracy."""
    
    def __init__(self):
        super().__init__(
                name="SolutionVerifier",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )

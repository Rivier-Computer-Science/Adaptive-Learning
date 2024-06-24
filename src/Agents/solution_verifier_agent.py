##################### Solution Verifier #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class SolutionVerifierAgent(MyConversableAgent):
  description = """I am the SolutionVerifierAgent responsible for ensuring the accuracy of solutions provided for various problems. I check solutions against the correct answers and offer feedback on their correctness."""
    
    system_message = """My task is to verify the correctness of solutions submitted by comparing them against the correct answers and providing feedback on their accuracy."""
    
    def __init__(self):
        super().__init__(
                name="SolutionVerifier",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )

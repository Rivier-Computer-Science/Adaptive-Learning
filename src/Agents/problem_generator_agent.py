from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

# Adjust import as per your actual structure

class ProblemGeneratorAgent(MyConversableAgent):
    description = """ProblemGenerator is designed to generate mathematical problems based on the current curriculum and the student's learning level.
                ProblemGenerator ensures that the problems generated are appropriate and challenging."""
                    
    system_message = """ProblemGenerator will generate mathematical problems based on the current curriculum and the student's learning level.
                        ProblemGenerator ensures that the problems generated are appropriate and challenging."""
    

    def __init__(self):
        super().__init__(
            name="ProblemGenerator",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message=self.system_message,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            llm_config=gpt3_config  # Ensure gpt3_config is correctly defined or imported
        )

from agents import MyAssisstantAgent
import gpt4_config  # Make sure this is correctly imported or defined in your environment
 
class ProblemGeneratorAgent(MyAssisstantAgent):
    description = """Can you give me a math problem for a 5th grader."""
    
    def __init__(self):
        super().__init__(
            name="Problem Generator",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message=self.description,
            description=self.description
        )
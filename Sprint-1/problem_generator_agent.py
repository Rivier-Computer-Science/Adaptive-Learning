from agents import MyAssisstantAgent
import gpt4_config  # Make sure this is correctly imported or defined in your environment
 
class ProblemGeneratorAgent(MyAssisstantAgent):
    description = """You ask the Level Adapter for the level of difficulty and generate a question."""
    
    def __init__(self):
        super().__init__(
            name="Problem Generator",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message=self.description,
            description=self.description
        )
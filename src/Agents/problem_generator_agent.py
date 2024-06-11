# problem_generator_agent.py

from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class ProblemGeneratorAgent(MyConversableAgent):
    description = """"In your role as a problem generator, you generate math problems spanning different topics and complexity levels to aid in learning and practice."""
    def __init__(self):
        super().__init__(
                name="ProblemGenerator",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )

    def generate_problem(self, skill_level):
        if skill_level == 2:
            return "Solve 5 + 3"
        elif skill_level == 4:
            return "Solve 12 * 8"
        elif skill_level == 6:
            return "Solve the integral of x^2"
        else:
            return "Skill level not recognized"

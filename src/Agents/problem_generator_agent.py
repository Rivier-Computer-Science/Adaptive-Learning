# problem_generator_agent.py

import os
import sys

# Ensure the src directory is in the sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../../src'))
sys.path.append(src_dir)

from Agents.conversable_agent import MyConversableAgent
from Models.llm_config import gpt3_config

class ProblemGeneratorAgent(MyConversableAgent):
    description = "You are a math problem generator, assisting users by providing practice questions tailored to their skill level and topic of interest."
    
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

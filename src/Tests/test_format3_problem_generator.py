# src/Tests/test_format3_problem_generator.py

import unittest
from src.Agents.agents import ProblemGeneratorAgent

class TestFormat3ProblemGenerator(unittest.TestCase):
    
    def test_description_prompt(self):
        # Format 3 description prompt for Problem Generator Agent
        description_prompt = (
            "Describe the role and function of the Problem Generator agent "
            "in the adaptive learning system."
        )
        self.assertIsInstance(description_prompt, str)
        self.assertNotEqual(len(description_prompt), 0)
    
    def test_observation_prompt(self):
        # Format 3 observation prompt for Problem Generator Agent
        observation_prompt = (
            "Observe the behavior and interaction patterns of the Problem Generator agent "
            "during a tutoring session."
        )
        self.assertIsInstance(observation_prompt, str)
        self.assertNotEqual(len(observation_prompt), 0)

if __name__ == "__main__":
    unittest.main()

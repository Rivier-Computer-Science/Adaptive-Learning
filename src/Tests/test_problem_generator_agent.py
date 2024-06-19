# C:\Users\Nagis\OneDrive\Desktop\Professional seminar\Adaptive-Learning\src\Tests\test_problem_generator_agent.py

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust the system path to include the project directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Agents.problem_generator_agent import ProblemGeneratorAgent

class TestProblemGeneratorAgent(unittest.TestCase):

    def setUp(self):
        self.agent = ProblemGeneratorAgent()

    def test_description(self):
        expected_description = "I'm a math problem generator, assisting users by providing practice questions tailored to their skill level and topic of interest."
        self.assertEqual(self.agent.description, expected_description)

    def test_generate_problem_mock(self):
        # Mock the behavior of generating a problem based on skill level
        with patch('Agents.problem_generator_agent.ProblemGeneratorAgent') as MockAgent:
            instance = MockAgent.return_value
            instance.generate_problem = MagicMock(side_effect=lambda skill_level: {
                2: "Solve 5 + 3",
                4: "Solve 12 * 8",
                6: "Solve the integral of x^2"
            }.get(skill_level, "Skill level not recognized"))

            # Test for skill level 2
            problem_skill_2 = instance.generate_problem(2)
            self.assertEqual(problem_skill_2, "Solve 5 + 3")

            # Test for skill level 4
            problem_skill_4 = instance.generate_problem(4)
            self.assertEqual(problem_skill_4, "Solve 12 * 8")

            # Test for skill level 6
            problem_skill_6 = instance.generate_problem(6)
            self.assertEqual(problem_skill_6, "Solve the integral of x^2")

            # Test for unknown skill level
            problem_skill_unknown = instance.generate_problem(8)
            self.assertEqual(problem_skill_unknown, "Skill level not recognized")

if __name__ == "__main__":
    unittest.main()

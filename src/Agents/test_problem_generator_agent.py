# test_problem_generator_agent.py

import os
import sys
import unittest

# Ensure the src directory is in the sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../../src'))
sys.path.append(src_dir)

from Agents.problem_generator_agent import ProblemGeneratorAgent

class TestProblemGeneratorAgent(unittest.TestCase):
    def test_description_prompt(self):
        # Initialize ProblemGeneratorAgent
        problem_generator = ProblemGeneratorAgent()

        # Expected description
        expected_description = "You are a math problem generator, assisting users by providing practice questions tailored to their skill level and topic of interest."
        
        # Check if the description matches the expected description
        self.assertEqual(problem_generator.description, expected_description)
    
    def test_generate_problem(self):
        # Initialize ProblemGeneratorAgent
        problem_generator = ProblemGeneratorAgent()

        # Test skill level 2
        problem_skill_2 = problem_generator.generate_problem(2)
        self.assertEqual(problem_skill_2, "Solve 5 + 3")

        # Test skill level 4
        problem_skill_4 = problem_generator.generate_problem(4)
        self.assertEqual(problem_skill_4, "Solve 12 * 8")

        # Test skill level 6
        problem_skill_6 = problem_generator.generate_problem(6)
        self.assertEqual(problem_skill_6, "Solve the integral of x^2")

        # Test unrecognized skill level
        problem_skill_unknown = problem_generator.generate_problem(8)
        self.assertEqual(problem_skill_unknown, "Skill level not recognized")

if __name__ == '__main__':
    unittest.main()

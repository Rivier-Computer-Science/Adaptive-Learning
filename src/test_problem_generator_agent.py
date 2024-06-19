import sys
import unittest
from problem_generator_agent import ProblemGeneratorAgent
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class TestProblemGeneratorAgent(unittest.TestCase):
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

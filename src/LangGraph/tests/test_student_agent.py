
# src/LangGraph/tests/test_student_agent.py

import unittest
from datetime import datetime
from src.LangGraph.agents.student_agent import run, StudentInput, StudentOutput

class TestStudentAgent(unittest.TestCase):

    def test_valid_input(self):
        input_data = StudentInput(
            goal_name="Learn Algebra",
            description="Master algebra basics",
            target_date=datetime(2024, 12, 1),
            priority="High",
            category="Math"
        )
        output = run(input_data)
        self.assertTrue(output.goal_added)
        self.assertIn("Learn Algebra", output.message)

    def test_missing_goal_name(self):
        input_data = StudentInput(
            goal_name="",
            description="Missing goal name",
            target_date=datetime(2024, 12, 1),
            priority="Medium",
            category="Science"
        )
        output = run(input_data)
        self.assertFalse(output.goal_added)
        self.assertIn("missing", output.message)

if __name__ == '__main__':
    unittest.main()

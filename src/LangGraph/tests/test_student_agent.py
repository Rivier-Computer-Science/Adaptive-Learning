# src/LangGraph/tests/test_student_agent.py

import unittest
from datetime import datetime
from src.Models.student_models import StudentInput, StudentOutput
from src.Models.langgraph_state import LangGraphState
from src.Models.knowledge_tracer_models import KnowledgeTracerState
from src.LangGraph.agents.student_agent import handle_student_input, run


class TestStudentAgent(unittest.TestCase):

    def test_valid_input(self):
        input_data = StudentInput(
            goal_name="Learn Algebra",
            description="Master algebra basics",
            target_date=datetime(2024, 12, 1),
            priority="High",
            category="Math"
        )
        output = handle_student_input(input_data)
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
        output = handle_student_input(input_data)
        self.assertFalse(output.goal_added)
        self.assertIn("missing", output.message.lower())

    def test_run_function_sets_tracer_input(self):
        input_data = StudentInput(
            goal_name="Loops in Python",
            description="Understand for/while loops",
            target_date=datetime(2025, 1, 1),
            priority="High",
            category="Programming"
        )
        state = LangGraphState(student_input=input_data)
        result = run(state)

        # Ensure student_input is preserved
        self.assertEqual(result["student_input"].goal_name, "Loops in Python")

        # Ensure tracer_input is simulated
        tracer: KnowledgeTracerState = result["tracer_input"]
        self.assertEqual(tracer.concept, "Python Loops")
        self.assertEqual(tracer.correct_answers, 8)
        self.assertEqual(tracer.total_questions, 10)


if __name__ == '__main__':
    unittest.main()

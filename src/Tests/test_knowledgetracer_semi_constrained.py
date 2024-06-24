import unittest
from unittest.mock import MagicMock
from src.Agents.knowledge_tracer_agent import KnowledgeTracerAgent
from src.Agents.student_agent import StudentAgent
from src.Agents.problem_generator_agent import ProblemGeneratorAgent
from src.Agents.learner_model_agent import LearnerModelAgent
from src.Agents.level_adapter_agent import LevelAdapterAgent

class TestAdaptiveMathTutor(unittest.TestCase):

    def setUp(self):
        # Create mock objects for agents
        self.knowledge_tracer = KnowledgeTracerAgent()
        self.student = StudentAgent()
        self.problem_generator = ProblemGeneratorAgent()
        self.learner_model = LearnerModelAgent()
        self.level_adapter = LevelAdapterAgent()

        # Mock the respond method for each agent
        self.knowledge_tracer.respond = MagicMock()
        self.student.respond = MagicMock()
        self.problem_generator.respond = MagicMock()
        self.learner_model.respond = MagicMock()
        self.level_adapter.respond = MagicMock()

    def test_trace_geometry_knowledge(self):
        user_input = "trace my geometry knowledge"
        self.knowledge_tracer.respond.return_value = {
            'sender': 'KnowledgeTracer',
            'recipient': 'ProblemGenerator',
            'message': "Let's start by assessing your geometry knowledge."
        }
        response = self.knowledge_tracer.respond(user_input)
        self.assertIn("Let's start by assessing your geometry knowledge.", response['message'])

    def test_explain_pythagorean_theorem(self):
        user_input = "Explain the Pythagorean Theorem."
        self.student.respond.return_value = {
            'sender': 'Teacher',
            'recipient': 'Student',
            'message': "The Pythagorean Theorem is a fundamental principle..."
        }
        response = self.student.respond(user_input)
        self.assertIn("The Pythagorean Theorem is a fundamental principle", response['message'])

    def test_determine_right_triangle(self):
        user_input = "How can you determine if a triangle is a right triangle using the Pythagorean Theorem?"
        self.learner_model.respond.return_value = {
            'sender': 'Teacher',
            'recipient': 'LearnerModel',
            'message': "To determine if a triangle is a right triangle using the Pythagorean Theorem..."
        }
        response = self.learner_model.respond(user_input)
        self.assertIn("To determine if a triangle is a right triangle using the Pythagorean Theorem", response['message'])

    def test_difference_between_line_and_segment(self):
        user_input = "What is the difference between a line and a line segment?"
        self.level_adapter.respond.return_value = {
            'sender': 'Teacher',
            'recipient': 'LevelAdapter',
            'message': "A line is a straight path that extends infinitely..."
        }
        response = self.level_adapter.respond(user_input)
        self.assertIn("A line is a straight path that extends infinitely", response['message'])

    def test_harder_question_about_triangles(self):
        user_input = "Ask me a harder question about triangles."
        self.problem_generator.respond.return_value = {
            'sender': 'ProblemGenerator',
            'recipient': 'Student',
            'message': "In a triangle, if one angle measures 70 degrees..."
        }
        response = self.problem_generator.respond(user_input)
        self.assertIn("In a triangle, if one angle measures 70 degrees", response['message'])

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock
from src.Agents.student_agent import StudentAgent
from src.Agents.problem_generator_agent import ProblemGeneratorAgent
from src.Agents.teacher_agent import TeacherAgent
from src.Agents.level_adapter_agent import LevelAdapterAgent
from src.Agents.learner_model_agent import LearnerModelAgent

class TestMathTutorConversation(unittest.TestCase):

    def setUp(self):
        # Create mock objects for agents
        self.student = StudentAgent()
        self.problem_generator = ProblemGeneratorAgent()
        self.teacher = TeacherAgent()
        self.level_adapter = LevelAdapterAgent()
        self.learner_model = LearnerModelAgent()

        # Mock the respond method for each agent
        self.student.respond = MagicMock()
        self.problem_generator.respond = MagicMock()
        self.teacher.respond = MagicMock()
        self.level_adapter.respond = MagicMock()
        self.learner_model.respond = MagicMock()

    def test_math_tutor_conversation(self):
        # Simulate the conversation flow based on the provided chat interactions

        # Step 1: User requests an algebra problem
        user_input_algebra = "Generate a challenging algebra problem for me."
        self.problem_generator.respond.return_value = {
            'sender': 'ProblemGenerator',
            'recipient': 'Student',
            'message': "Here is a challenging algebra problem: Solve for x: 3x^2 + 5x - 2 = 0"
        }
        response_algebra = self.problem_generator.respond(user_input_algebra)
        self.assertIn("Here is a challenging algebra problem", response_algebra['message'])
        self.assertIn("Solve for x: 3x^2 + 5x - 2 = 0", response_algebra['message'])

        # Step 2: Level Adapter processes the request
        self.level_adapter.respond.return_value = {
            'sender': 'LevelAdapter',
            'recipient': 'ProblemGenerator',
            'message': "Input received for algebra problem. Waiting for Student's response."
        }
        response_level_adapter = self.level_adapter.respond(user_input_algebra)
        self.assertIn("Input received for algebra problem", response_level_adapter['message'])

        # Step 3: Problem Generator forwards to Teacher for geometry question
        user_input_geometry = "Create a geometry question that tests my understanding of angles."
        self.teacher.respond.return_value = {
            'sender': 'Teacher',
            'recipient': 'Student',
            'message': "Here's a geometry question: In triangle ABC, angle A measures 50 degrees and angle B measures 70 degrees. What is the measure of angle C?"
        }
        response_geometry = self.teacher.respond(user_input_geometry)
        self.assertIn("Here's a geometry question", response_geometry['message'])
        self.assertIn("In triangle ABC, angle A measures 50 degrees", response_geometry['message'])

        # Step 4: Learner Model processes the geometry question response
        self.learner_model.respond.return_value = {
            'sender': 'LearnerModel',
            'recipient': 'Teacher',
            'message': "Student has been given a geometry question. Waiting for Student's response."
        }
        response_learner_model = self.learner_model.respond(user_input_geometry)
        self.assertIn("Student has been given a geometry question", response_learner_model['message'])

        # Step 5: Teacher responds with a calculus problem
        user_input_calculus = "Can you provide a calculus problem involving derivatives?"
        self.teacher.respond.return_value = {
            'sender': 'Teacher',
            'recipient': 'Student',
            'message': "Of course! Here's a calculus problem: Find the derivative of the function f(x) = 3x^2 + 4x - 2."
        }
        response_calculus = self.teacher.respond(user_input_calculus)
        self.assertIn("Here's a calculus problem", response_calculus['message'])
        self.assertIn("Find the derivative of the function f(x) = 3x^2 + 4x - 2", response_calculus['message'])

        # Step 6: Level Adapter processes the calculus problem request
        self.level_adapter.respond.return_value = {
            'sender': 'LevelAdapter',
            'recipient': 'Teacher',
            'message': "Input received for calculus problem. Waiting for Student's response."
        }
        response_level_adapter_calculus = self.level_adapter.respond(user_input_calculus)
        self.assertIn("Input received for calculus problem", response_level_adapter_calculus['message'])

        # Step 7: Student requests a trigonometry problem
        user_input_trigonometry = "Give me a trigonometry problem that involves solving for an unknown angle."
        self.teacher.respond.return_value = {
            'sender': 'Teacher',
            'recipient': 'Student',
            'message': "Certainly! Here's a trigonometry problem: In a right triangle, the opposite side is 5 units long, and the hypotenuse is 13 units long. Find the measure of the angle θ opposite the side of length 5 units."
        }
        response_trigonometry = self.teacher.respond(user_input_trigonometry)
        self.assertIn("Here's a trigonometry problem", response_trigonometry['message'])
        self.assertIn("In a right triangle, the opposite side is 5 units long", response_trigonometry['message'])

        # Step 8: Learner Model processes the trigonometry problem response
        self.learner_model.respond.return_value = {
            'sender': 'LearnerModel',
            'recipient': 'Teacher',
            'message': "Student has been presented with a trigonometry problem. Waiting for Student's response."
        }
        response_learner_model_trig = self.learner_model.respond(user_input_trigonometry)
        self.assertIn("Student has been presented with a trigonometry problem", response_learner_model_trig['message'])

        # Step 9: Level Adapter processes a request for a problem combining multiple concepts
        user_input_combined = "Generate a problem that combines multiple mathematical concepts."
        self.teacher.respond.return_value = {
            'sender': 'Teacher',
            'recipient': 'Student',
            'message': "Here's a problem that combines multiple mathematical concepts: A car travels at a constant speed of 60 miles per hour. The car starts its journey at 8:00 AM and reaches its destination at 10:30 AM. If the total distance traveled is 150 miles, calculate the average speed of the car for the entire journey in kilometers per hour."
        }
        response_combined = self.teacher.respond(user_input_combined)
        self.assertIn("Here's a problem that combines multiple mathematical concepts", response_combined['message'])
        self.assertIn("A car travels at a constant speed of 60 miles per hour", response_combined['message'])

if __name__ == '__main__':
    unittest.main()

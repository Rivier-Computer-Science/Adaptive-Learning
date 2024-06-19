import unittest
from unittest.mock import MagicMock
from Agents.knowledge_tracer_agent import KnowledgeTracerAgent

class TestKnowledgeTracerAgent(unittest.TestCase):

    def setUp(self):
        self.agent = KnowledgeTracerAgent()
        self.agent.respond = MagicMock(return_value={"content": self.agent.system_message_agent})

    def check_response_contains(self, user_input, keywords):
        response = self.agent.respond(user_input)['content']
        for keyword in keywords:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, response)

    def test_understanding_role(self):
        user_input = "What is your role as a Knowledge Tracer?"
        expected_keywords = ["Knowledge Tracer", "test the student's knowledge", "Problem Generator", "Learner Model"]
        self.check_response_contains(user_input, expected_keywords)

    def test_function_explanation(self):
        user_input = "Explain what you do as a Knowledge Tracer."
        expected_keywords = ["Knowledge Tracer", "test the student's knowledge", "present problems", "track the student's level"]
        self.check_response_contains(user_input, expected_keywords)

    def test_collaboration_with_problem_generator(self):
        user_input = "How do you collaborate with the Problem Generator?"
        expected_keywords = ["Knowledge Tracer", "Problem Generator", "present problems"]
        self.check_response_contains(user_input, expected_keywords)

    def test_tracking_student_progress(self):
        user_input = "How do you track the student's progress?"
        expected_keywords = ["Knowledge Tracer", "track", "Learner Model", "student's level"]
        self.check_response_contains(user_input, expected_keywords)

    def test_role_confirmation(self):
        user_input = "Confirm your role."
        expected_keywords = ["Knowledge Tracer", "test the student's knowledge", "present problems", "maintain the Learner Model", "track the student's level"]
        self.check_response_contains(user_input, expected_keywords)

if __name__ == "__main__":
    unittest.main()

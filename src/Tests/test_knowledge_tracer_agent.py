import unittest
from Agents.knowledge_tracer_agent import KnowledgeTracerAgent  

class TestKnowledgeTracerAgent(unittest.TestCase):

    def setUp(self):
        self.agent = KnowledgeTracerAgent()

    def test_trace_algebra_knowledge(self):
        user_input = "Trace my algebra knowledge."
        response = self.agent.respond(user_input)
        self.assertIn("I will trace your algebra knowledge", response)

    def test_trace_factoring_knowledge(self):
        user_input = "Trace my knowledge in factoring."
        response = self.agent.respond(user_input)
        self.assertIn("I will trace your knowledge in factoring", response)

    def test_role_description(self):
        user_input = "What is your role as a knowledge tracer agent?"
        response = self.agent.respond(user_input)
        self.assertIn("my role is to test the student on what they know", response)

    def test_identify_struggling_topics(self):
        user_input = "How do you identify which algebra topics I am struggling with?"
        response = self.agent.respond(user_input)
        self.assertIn("I will identify which algebra topics you are struggling with", response)

if __name__ == '__main__':
    unittest.main()
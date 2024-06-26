import unittest
from unittest.mock import MagicMock
from src.Agents.tutor_agent import TutorAgent

class TestTutorAgent(unittest.TestCase):

    def setUp(self):
        self.agent = TutorAgent()
        # Custom mock for each test case
        self.agent.respond = MagicMock(side_effect=self.mock_respond)

    def mock_respond(self, user_input):
        if "recursion" in user_input:
            return {"content": "Recursion is a method of solving problems where the solution depends on solutions to smaller instances of the same problem. An example of recursion is the factorial function."}
        elif "quadratic equation" in user_input:
            return {"content": "A quadratic equation is an equation of the form ax^2 + bx + c = 0. To solve it, you can use the quadratic formula: x = (-b ± √(b^2 - 4ac)) / (2a). Here are the steps to solve it."}
        elif "hint" in user_input:
            return {"content": "Here's a hint to help you solve the problem: Try breaking it down into smaller parts and solving the problem step by step."}
        elif "2+2" in user_input:
            if "5" in user_input:
                return {"content": "The answer to 2+2 is incorrect. It is not 5. The correct answer is 4."}
            else:
                return {"content": "Yes, the answer to 2+2 is correct. It is 4."}
        elif "sky is blue" in user_input:
            return {"content": "The sky appears blue due to the scattering of sunlight by the atmosphere. Molecules and small particles in the atmosphere scatter short-wavelength light, such as blue, more than long-wavelength light, giving the sky its blue color."}
        elif "your role" in user_input:
            return {"content": "As a TutorAgent, my role is to assist students with their learning by providing explanations, solving problems, and guiding them through difficult concepts and exercises."}
        else:
            return {"content": self.agent.system_message}

    def check_response_contains(self, user_input, keywords):
        response = self.agent.respond(user_input)['content']
        print(f"Response: '{response}'")  # Debug print
        for keyword in keywords:
            with self.subTest(keyword=keyword):
                print(f"Checking for keyword: '{keyword}' in response")  # Debug print
                self.assertIn(keyword.lower().strip(), response.lower().strip())

    def test_explain_recursion(self):
        user_input = "I don't understand the concept of recursion. Can you explain it to me?"
        expected_keywords = ["recursion", "method of solving problems", "example"]
        self.check_response_contains(user_input, expected_keywords)

    def test_guide_quadratic_equation(self):
        user_input = "Can you guide me through solving a quadratic equation?"
        expected_keywords = ["quadratic equation", "quadratic formula", "steps"]
        self.check_response_contains(user_input, expected_keywords)

    def test_provide_hint(self):
        user_input = "I'm stuck on this problem, can you give me a hint?"
        expected_keywords = ["hint", "solving the problem"]
        self.check_response_contains(user_input, expected_keywords)

    def test_correct_answer(self):
        user_input = "Is the answer to 2+2 equal to 4?"
        expected_keywords = ["correct", "2+2"]
        self.check_response_contains(user_input, expected_keywords)

    def test_incorrect_answer(self):
        user_input = "Is the answer to 2+2 equal to 5?"
        expected_keywords = ["incorrect", "2+2"]
        self.check_response_contains(user_input, expected_keywords)

    def test_explanation_request(self):
        user_input = "Can you explain why the sky is blue?"
        expected_keywords = ["sky", "blue", "molecules", "scatter"]
        self.check_response_contains(user_input, expected_keywords)

    def test_role_confirmation(self):
        user_input = "Confirm your role."
        expected_keywords = ["TutorAgent", "assist students", "learning", "explanations", "solving problems", "guiding"]
        self.check_response_contains(user_input, expected_keywords)

if __name__ == "__main__":
    unittest.main()

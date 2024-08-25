# TASK2 test_feedback_generator.py

import unittest
from feedback_generator import FeedbackGenerator

class TestFeedbackGenerator(unittest.TestCase):
    def setUp(self):
        self.fg = FeedbackGenerator()

    def test_generate_feedback(self):
        question = "What is 2+2?"
        answer = "4"
        user_level = 1

        feedback = self.fg.generate_feedback(question, answer, user_level)
        
        # Print the entire feedback for debugging
        print("Feedback Content:\n", feedback)
        
        # Ensure that feedback includes the base message and all expected explanations
        self.assertIn("Here's your feedback based on your answer.", feedback)
        self.assertIn("Explanation for concept1", feedback)
        self.assertIn("Explanation for concept2", feedback)

if __name__ == "__main__":
    unittest.main()

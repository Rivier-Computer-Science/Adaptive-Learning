# TASK2 feedback_generator.py

from explanation_generator import ExplanationGenerationAlgorithm

class FeedbackGenerator:
    def __init__(self):
        self.explanation_generator = ExplanationGenerationAlgorithm()

    def generate_feedback(self, question, answer, user_level):
        # Generate explanations based on the question, answer, and user level
        explanations = self.explanation_generator.generate_explanation(question, answer, user_level)
        feedback = "Here's your feedback based on your answer.\n"
        feedback += explanations
        return feedback

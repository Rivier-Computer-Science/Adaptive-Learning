import unittest
from explanation_algorithm import ExplanationGenerationAlgorithm

class TestExplanationGeneration(unittest.TestCase):

    def setUp(self):
        self.algorithm = ExplanationGenerationAlgorithm()

    def test_generate_explanation(self):
        question = "What is concept1?"
        answer = "Concept1 is..."
        user_level = "beginner"
        expected_explanation = "Explanation for concept1\nExplanation for concept2"
        result = self.algorithm.generate_explanation(question, answer, user_level)
        self.assertEqual(result, expected_explanation)

    def test_analyze_question_and_answer(self):
        question = "What is concept1?"
        answer = "Concept1 is..."
        expected_concepts = ["concept1", "concept2"]
        result = self.algorithm.analyze_question_and_answer(question, answer)
        self.assertEqual(result, expected_concepts)

    def test_select_explanation(self):
        key_concepts = ["concept1", "concept2"]
        user_level = "beginner"
        expected_explanation = "Explanation for concept1\nExplanation for concept2"
        result = self.algorithm.select_explanation(key_concepts, user_level)
        self.assertEqual(result, expected_explanation)

if __name__ == '__main__':
    unittest.main()

#TASK1
class ExplanationGenerationAlgorithm:
    def __init__(self):
        self.explanation_db = self.load_explanation_database()

    def load_explanation_database(self):
        # Load the explanation database from a file or database
        return {
            "concept1": "Explanation for concept1",
            "concept2": "Explanation for concept2",
            # Add more concepts and explanations
        }

    def generate_explanation(self, question, answer, user_level):
        # Analyze the question and answer to identify key concepts
        key_concepts = self.analyze_question_and_answer(question, answer)

        # Select relevant explanations
        explanation = self.select_explanation(key_concepts, user_level)

        return explanation

    def analyze_question_and_answer(self, question, answer):
        # Placeholder for analyzing the question and answer to extract key concepts
        # Replace with actual logic to identify key concepts
        return ["concept1", "concept2"]

    def select_explanation(self, key_concepts, user_level):
        # Placeholder for selecting relevant explanations from the database
        # Replace with actual logic to select and tailor explanations based on user level
        explanations = [self.explanation_db[concept] for concept in key_concepts if concept in self.explanation_db]
        return "\n".join(explanations)

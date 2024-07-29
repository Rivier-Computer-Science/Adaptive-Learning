class ExplanationGenerationAlgorithm:
    def __init__(self):
        pass

    def generate_explanation(self, question, answer, user_level):
        # Example implementation
        return f"Detailed explanation for {question} at {user_level} level.\nAdditional info about related topics."
    
    def get_practice_problems(self, key_concepts, user_level):
        # Example practice problems based on key concepts and user level
        problems = {
            "easy": ["Easy problem 1", "Easy problem 2"],
            "medium": ["Medium problem 1", "Medium problem 2"],
            "hard": ["Hard problem 1", "Hard problem 2"]
        }
        return problems[user_level]

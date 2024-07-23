# adaptive_difficulty.py

difficulty_levels = ["easy", "medium", "hard"]

increase_threshold = 3  # Number of correct answers needed to increase difficulty
decrease_threshold = 3  # Number of incorrect answers needed to decrease difficulty

class AdaptiveDifficulty:
    def __init__(self):
        self.current_difficulty = "medium"
        self.correct_streak = 0
        self.incorrect_streak = 0

    def update_difficulty(self, correct):
        if correct:
            self.correct_streak += 1
            self.incorrect_streak = 0
            if self.correct_streak >= increase_threshold:
                self.increase_difficulty()
        else:
            self.incorrect_streak += 1
            self.correct_streak = 0
            if self.incorrect_streak >= decrease_threshold:
                self.decrease_difficulty()

    def increase_difficulty(self):
        if self.current_difficulty != "hard":
            self.current_difficulty = "hard" if self.current_difficulty == "medium" else "medium"
            self.correct_streak = 0

    def decrease_difficulty(self):
        if self.current_difficulty != "easy":
            self.current_difficulty = "medium" if self.current_difficulty == "hard" else "easy"
            self.incorrect_streak = 0

    def get_current_difficulty(self):
        return self.current_difficulty

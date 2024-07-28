class AdaptiveDifficulty:
    def __init__(self):
        self.difficulty_levels = ["easy", "medium", "hard"]
        self.current_difficulty_index = 0  # Start with "easy"
        self.correct_streak = 0
        self.incorrect_streak = 0

    def get_current_difficulty(self):
        return self.difficulty_levels[self.current_difficulty_index]

    def update_performance(self, correct: bool):
        if correct:
            self.correct_streak += 1
            self.incorrect_streak = 0
            if self.correct_streak >= 3 and self.current_difficulty_index < len(self.difficulty_levels) - 1:
                self.current_difficulty_index += 1
                self.correct_streak = 0
        else:
            self.incorrect_streak += 1
            self.correct_streak = 0
            if self.incorrect_streak >= 3 and self.current_difficulty_index > 0:
                self.current_difficulty_index -= 1
                self.incorrect_streak = 0

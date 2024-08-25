import unittest
import sys
import os

# Add the directory containing adaptive_difficulty.py to the sys.path
adaptive_difficulty_path = r'C:\Users\dsrik\OneDrive\Desktop\CS699\Sprint-2\Adaptive-Learning-3\src\UI'
sys.path.append(adaptive_difficulty_path)

from adaptive_difficulty import AdaptiveDifficulty

class TestAdaptiveDifficulty(unittest.TestCase):

    def setUp(self):
        self.adaptive_difficulty = AdaptiveDifficulty()

    def test_initial_difficulty_level(self):
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "easy")

    def test_increase_difficulty(self):
        # Answer 3 questions correctly in a row
        for _ in range(3):
            self.adaptive_difficulty.update_performance(correct=True)
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "medium")

        # Answer 3 more questions correctly in a row
        for _ in range(3):
            self.adaptive_difficulty.update_performance(correct=True)
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "hard")

    def test_decrease_difficulty(self):
        # First increase the difficulty to "medium"
        for _ in range(3):
            self.adaptive_difficulty.update_performance(correct=True)
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "medium")

        # Now answer 3 questions incorrectly in a row
        for _ in range(3):
            self.adaptive_difficulty.update_performance(correct=False)
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "easy")

    def test_no_change_on_mixed_performance(self):
        # Answer 2 questions correctly, 1 incorrectly
        for _ in range(2):
            self.adaptive_difficulty.update_performance(correct=True)
        self.adaptive_difficulty.update_performance(correct=False)
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "easy")

    def test_difficulty_does_not_exceed_bounds(self):
        # Try to increase difficulty beyond "hard"
        for _ in range(10):
            self.adaptive_difficulty.update_performance(correct=True)
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "hard")

        # Try to decrease difficulty beyond "easy"
        for _ in range(10):
            self.adaptive_difficulty.update_performance(correct=False)
        self.assertEqual(self.adaptive_difficulty.get_current_difficulty(), "easy")

if __name__ == '__main__':
    unittest.main()

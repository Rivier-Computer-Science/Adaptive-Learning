# TASK2 run_integration_test.py
import sys
import os

# Add the directory containing feedback_generator.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feedback_generator import FeedbackGenerator

def main():
    fg = FeedbackGenerator()

    # Simulated input
    question = "What is 2+2?"
    answer = "4"
    user_level = 1

    # Generate and display feedback
    feedback = fg.generate_feedback(question, answer, user_level)
    print(feedback)

if __name__ == "__main__":
    main()

#TASK1
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from explanation_generator import ExplanationGenerationAlgorithm

def main():
    algo = ExplanationGenerationAlgorithm()

    # Simulated question and answer
    question = "What is 2+2?"
    answer = "4"
    user_level = 1  # Beginner level

    explanation = algo.generate_explanation(question, answer, user_level)
    print(f"Explanation: {explanation}")

if __name__ == "__main__":
    main()

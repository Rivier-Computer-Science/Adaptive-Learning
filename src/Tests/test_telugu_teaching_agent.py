from src.Agents.agents_telugu import agents_dict
from src.Agents.chat_manager_fsms_telugu import FSM
from src.Agents.telugu_teaching_agent import TeluguTeachingAgent
from unittest.mock import Mock  # Import Mock

# Define the mock_adapt_level function at the top to reuse it in multiple tests
def mock_adapt_level(agent):
    if len(agent.quiz_results) > 0 and agent.quiz_results[-1]:  # Last answer was correct
        # Increase skill level and move to next lesson
        agent.skill_level += 1
        agent.current_lesson = min(agent.current_lesson + 1, len(agent.lessons) - 1)
    else:  # Last answer was incorrect
        # Decrease skill level and move to previous lesson
        agent.skill_level = max(0, agent.skill_level - 1)
        agent.current_lesson = max(0, agent.current_lesson - 1)

def test_adaptive_learning_with_phonetic():
    # Initialize FSM and agents
    fsm = FSM(agents=agents_dict)
    telugu_agent = agents_dict["telugu_teaching_agent"]
    problem_generator = agents_dict["problem_generator"]
    level_adapter = agents_dict["level_adapter"]

    # Mocking the `generate_question` method with a fallback mechanism
# Expanded list of mock questions to cover more interactions
    questions = [
    "Translate 'Hello' to Telugu",   # Basic greetings
    "Translate 'One' to Telugu",     # Numbers
    "Translate 'Two' to Telugu",     # Numbers
    "Translate 'Three' to Telugu",   # Numbers
    "Translate 'Four' to Telugu",    # Numbers
    "Translate 'Five' to Telugu",    # Numbers
    "Translate 'Six' to Telugu",     # Numbers
    "Translate 'Seven' to Telugu",   # Numbers
    "Translate 'Eight' to Telugu",   # Numbers
    "Translate 'Nine' to Telugu",    # Numbers
    "Translate 'Ten' to Telugu",     # Numbers
    "Translate 'Good Morning' to Telugu",  # Greetings
    "Translate 'Thank You' to Telugu",     # Common phrases
    "Translate 'Please' to Telugu",        # Common phrases
    "Translate 'Yes' to Telugu",           # Simple words
    "Translate 'No' to Telugu",            # Simple words
    "Translate 'Water' to Telugu",         # Simple nouns
    "Translate 'Food' to Telugu",          # Simple nouns
    "Translate 'House' to Telugu",         # Simple nouns
    "Translate 'I am learning Telugu' to Telugu"  # Advanced sentence
]

    # Mock the problem generator to use this expanded list of questions
    problem_generator.generate_question = Mock(side_effect=lambda: questions.pop(0) if questions else "Translate 'Another question'")

    problem_generator.generate_question = Mock(side_effect=lambda: questions.pop(0) if questions else "Translate 'Another question'")

    level_adapter.adapt_level = Mock(side_effect=mock_adapt_level)

    # Simulate user interaction for adaptive learning
    interactions = [
        {"input": "Namaste", "expected_result": True},  # Correct
        {"input": "Oka", "expected_result": True},      # Correct
        {"input": "Wrong Answer", "expected_result": False},  # Incorrect
        {"input": "Wrong Answer", "expected_result": False},  # Incorrect
        {"input": "Rendu", "expected_result": True},    # Correct
    ]

    print("Initial lesson and state:")
    print(telugu_agent.present_lesson())
    print(f"Initial skill level: {telugu_agent.skill_level}")
    print(f"Initial current lesson index: {telugu_agent.current_lesson}\n")

    for i, interaction in enumerate(interactions):
        fsm.current_state = "AwaitingProblem"
        question = problem_generator.generate_question()

        print(f"Generated Question: {question}")

        user_input = interaction["input"]
        print(f"Student response: {user_input}")

        feedback = telugu_agent.run_lesson(user_input)
        print(f"Feedback: {feedback}")

        fsm.current_state = "AdaptingLevel"
        level_adapter.adapt_level(telugu_agent)

        print(f"Skill level after response {i + 1}: {telugu_agent.skill_level}")
        print(f"Current lesson index: {telugu_agent.current_lesson}")
        print(f"Next lesson: {telugu_agent.present_lesson()}\n")

    print("Adaptive learning test complete.\n")

# Test the full sequence of interactions and edge cases
def test_full_sequence_with_edge_cases():
    fsm = FSM(agents=agents_dict)
    telugu_agent = agents_dict["telugu_teaching_agent"]
    problem_generator = agents_dict["problem_generator"]
    level_adapter = agents_dict["level_adapter"]

    # Extend the mock questions list with a fallback
    questions = [
        "Translate 'Hello' to Telugu",
        "Translate 'One' to Telugu",
        "Translate 'Two' to Telugu",
        "Translate 'Three' to Telugu"
    ]
    problem_generator.generate_question = Mock(side_effect=lambda: questions.pop(0) if questions else "Translate 'Fallback question'")

    level_adapter.adapt_level = Mock(side_effect=mock_adapt_level)

    interactions = [
        {"input": "Namaste", "expected_result": True},   # Correct
        {"input": "Oka", "expected_result": True},       # Correct
        {"input": "Wrong Answer", "expected_result": False},  # Incorrect
        {"input": "Wrong Answer", "expected_result": False},  # Incorrect again
        {"input": "Oka", "expected_result": True},       # Correct (recover)
        {"input": "Rendu", "expected_result": True},     # Correct
        {"input": "Mūḍu", "expected_result": True},      # Phonetic for three
        {"input": "Wrong Answer", "expected_result": False},  # Incorrect
        {"input": "Naku Telugu chala ishtam", "expected_result": True},  # Correct (advanced)
        {"input": "Wrong Answer", "expected_result": False},  # Incorrect again
    ]

    print("Initial lesson and state:")
    print(telugu_agent.present_lesson())
    print(f"Initial skill level: {telugu_agent.skill_level}\n")

    for i, interaction in enumerate(interactions):
        fsm.current_state = "AwaitingProblem"
        question = problem_generator.generate_question()
        print(f"Generated Question: {question}")

        user_input = interaction["input"]
        feedback = telugu_agent.run_lesson(user_input)
        print(f"Feedback: {feedback}")

        fsm.current_state = "AdaptingLevel"
        level_adapter.adapt_level(telugu_agent)

        print(f"Skill level after response {i + 1}: {telugu_agent.skill_level}")
        print(f"Current lesson index: {telugu_agent.current_lesson}\n")

    print("Full sequence adaptive learning test complete.\n")


# Run all the tests
test_adaptive_learning_with_phonetic()
test_full_sequence_with_edge_cases()
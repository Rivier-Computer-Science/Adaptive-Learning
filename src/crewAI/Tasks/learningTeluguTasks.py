from crewai import Task
from src.crewAI.Agents.learningTeluguAgents import *

select_telugu_topic = Task(
    name="Select Telugu Topic",
    description=(
        "Greet the user warmly in Telugu and invite them to begin their Telugu language learning journey. "
        "Present 2-3 example topics such as 'Basic Alphabets (అక్షరాలు)', 'Common Words (సాధారణ పదాలు)', or 'Simple Sentences (సరళమైన వాక్యాలు)'. "
        "Do not mention that you are an AI. Once the user selects a topic, end the task. "
        "Avoid any further conversation or confirmation after topic selection."
    ),
    expected_output="Topic: <selected_topic>",
    agent=telugu_teacher,
    human_input=True
)

teach_telugu_topic = Task(
    name="Teach Telugu Topic",
    description="Explain the selected Telugu topic clearly with structured lessons, visuals (if supported), and real-life examples.",
    expected_output="Clear explanation and simple examples covering the selected topic.",
    context=[select_telugu_topic],
    agent=telugu_teacher,
    human_input=False
)

generate_telugu_problem = Task(
    name="Generate Telugu Problem",
    description=(
        "Create one relevant practice problem or question based on the topic that was taught. "
        "Make sure it's appropriate for a beginner and encourages thinking."
    ),
    expected_output="One Telugu language question or exercise.",
    context=[select_telugu_topic, teach_telugu_topic],
    agent=telugu_problem_gen,
    human_input=False
)

verify_telugu_problem = Task(
    name="Verify Telugu Problem Answer",
    description=(
        "Evaluate the student's answer to the problem. "
        "Reply only with: Final_Evaluation: Correct or Final_Evaluation: Incorrect. "
        "If incorrect, provide a brief reason."
    ),
    expected_output="Final_Evaluation: Correct | Final_Evaluation: Incorrect",
    context=[select_telugu_topic, teach_telugu_topic, generate_telugu_problem],
    agent=telugu_verifier,
    human_input=True
)

update_telugu_learner_model = Task(
    name="Update Telugu Learner Model",
    description=(
        "Based on the student's answer and evaluation, update their profile to reflect areas of improvement, strength, and topic understanding."
    ),
    expected_output="Updated learner profile with new progress metrics and topic history.",
    context=[select_telugu_topic, teach_telugu_topic, generate_telugu_problem, verify_telugu_problem],
    agent=telugu_learner,
    human_input=False
)

adjust_telugu_difficulty_level = Task(
    name="Adjust Telugu Difficulty Level",
    description="Analyze the updated learner model and adapt the next problem's difficulty to match the student's current level.",
    expected_output="Difficulty level: Easy | Medium | Hard, with justification.",
    context=[select_telugu_topic, teach_telugu_topic, generate_telugu_problem, verify_telugu_problem, update_telugu_learner_model],
    agent=telugu_level_adapter,
    human_input=False
)

motivate_telugu_student = Task(
    name="Motivate Telugu Student",
    description="Based on the learner’s progress, provide an emotionally uplifting and goal-oriented motivational message.",
    expected_output="Motivational message that boosts learner confidence and momentum.",
    context=[select_telugu_topic, teach_telugu_topic, generate_telugu_problem, verify_telugu_problem, update_telugu_learner_model, adjust_telugu_difficulty_level],
    agent=telugu_motivator,
    human_input=False
)

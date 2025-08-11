from crewai import Task
from src.crewAI.Agents.learningLanguageAgents import *

select_language_topic = Task(
    name="Select Language Topic",
    description=(
        "Greet the user warmly and invite them to begin their language learning journey in {language}. "
        "Present 2-3 example topics such as 'Basic Alphabets', 'Common Words', or 'Simple Sentences'. "
        "Do not mention that you are an AI. Once the user selects a topic, end the task. "
        "Avoid any further conversation or confirmation after topic selection."
    ),
    expected_output="Topic: <selected_topic>",
    agent=language_teacher,
    human_input=True
)

present_language_lesson = Task(
    name="Present Language Lesson",
    description="Explain the selected language: {language} topic clearly with structured lessons, visuals (if supported), and real-life examples.",
    expected_output="Clear explanation and simple examples covering the selected topic.",
    context=[select_language_topic],
    agent=language_teacher,
    human_input=False
)

generate_language_problem = Task(
    name="Generate Language Problem",
    description=(
        "Create one relevant practice problem or question based on the topic that was taught in {language}. "
        "Make sure it's appropriate for a beginner and encourages thinking."
    ),
    expected_output="One language question or exercise.",
    context=[select_language_topic, present_language_lesson],
    agent=language_problem_gen,
    human_input=False
)

await_student_answer = Task(
    name="Await Student Answer",
    description=(
        "Present the generated problem to the student and wait for their response. "
        "Provide clear instructions on how to answer the question in {language}."
    ),
    expected_output="Student's answer to the language problem.",
    context=[select_language_topic, present_language_lesson, generate_language_problem],
    agent=language_student,
    human_input=True
)

verify_language_answer = Task(
    name="Verify Language Answer",
    description=(
        "Evaluate the student's answer to the problem in {language}. "
        "Reply only with: Final_Evaluation: Correct or Final_Evaluation: Incorrect. "
        "If incorrect, provide a brief reason."
    ),
    expected_output="Final_Evaluation: Correct | Final_Evaluation: Incorrect",
    context=[select_language_topic, present_language_lesson, generate_language_problem, await_student_answer],
    agent=language_verifier,
    human_input=False
)

update_language_learner_model = Task(
    name="Update Language Learner Model",
    description=(
        "Based on the student's answer and evaluation, update their profile to reflect areas of improvement, strength, and topic understanding in {language}."
    ),
    expected_output="Updated learner profile with new progress metrics and topic history.",
    context=[select_language_topic, present_language_lesson, generate_language_problem, await_student_answer, verify_language_answer],
    agent=language_learner,
    human_input=False
)

adapt_language_difficulty_level = Task(
    name="Adapt Language Difficulty Level",
    description="Analyze the updated learner model and adapt the next problem's difficulty to match the student's current level.",
    expected_output="Difficulty level: Easy | Medium | Hard, with justification.",
    context=[select_language_topic, present_language_lesson, generate_language_problem, await_student_answer, verify_language_answer, update_language_learner_model],
    agent=language_level_adapter,
    human_input=False
)

motivate_language_student = Task(
    name="Motivate Language Student",
    description="Based on the learner's progress, provide an emotionally uplifting and goal-oriented motivational message.",
    expected_output="Motivational message that boosts learner confidence and momentum.",
    context=[select_language_topic, present_language_lesson, generate_language_problem, await_student_answer, verify_language_answer, update_language_learner_model, adapt_language_difficulty_level],
    agent=language_motivator,
    human_input=False
)

provide_language_tutoring = Task(
    name="Provide Language Tutoring",
    description=(
        "Based on the student's performance and the verification results, provide personalized tutoring guidance. "
        "Address any specific mistakes or areas where the student needs additional support."
    ),
    expected_output="Personalized tutoring guidance and support for the student.",
    context=[select_language_topic, present_language_lesson, generate_language_problem, await_student_answer, verify_language_answer, update_language_learner_model],
    agent=language_tutor,
    human_input=False
) 
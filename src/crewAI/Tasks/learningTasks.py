from crewai import Task
from src.crewAI.crewAgents import *

select_math_topic = Task(
    description=(
        "Greet the user with a warm welcome. Ask them to select a math topic to start with. "
        "Don't mention you're an AI. List 2-3 example topics like Algebra, Geometry, or Calculus. "
        "Exit the task after the user has selected a topic. Don't ask for confirmation if the user has selected a topic. "
        "There should be no other conversation after the user has selected a topic."
    ),
    name="Select Math Topic",
    expected_output="Return a topic that the user has given through human feedback. Output format: Topic: <topic>",
    agent=teacher,
    human_input=True  # This enables console input from the user
)

teach_math_topic = Task(
    description="Teach the selected math topic using a clear and structured explanation. Take the topic from the user's response in the previous task.",
    name="Teach Math Topic",
    agent=teacher,
    context=[select_math_topic],
    expected_output="Well-explained lesson on the selected topic.",
    human_input=False,
)

generate_math_problem = Task(
    description="Generate a problem related to the recently taught topic for the student to solve. Take the topic from the user's response in the previous task. Keep the maximum number of problems to 1. ",
    name="Generate Math Problem",
    agent=problem_gen,
    context=[select_math_topic, teach_math_topic],
    expected_output="A single relevant math problem statement.",
    human_input=False,
)

# task4 = Task(
#     description="Read the generated problem and attempt to provide a complete answer.",
#     name="Solve Math Problem",
#     agent=student,
#     context=[task1, task2, task3],
#     expected_output="Return the student's answer in the following format. Output format: Student_Answer: <answer>",
#     human_input=True,
# )

verify_math_problem = Task(
    description=(
        "Verify the accuracy and correctness of the student's answer based on the problem statement from the previous task. "
        "If the answer is correct, say 'Correct'. "
        "If the answer is incorrect, say 'Incorrect' "
    ),
    name="Verify Math Problem",
    agent=verifier,
    context=[select_math_topic, teach_math_topic, generate_math_problem],
    expected_output="Evaluation of the answer to correct or incorrect. *** Strictly follow this output format when the task is completed: Final_Evaluation: <evaluation> ***",
    human_input=True,
)



# task6 = Task(
#     description="Based on the verified answer, write Python code that solves the problem programmatically.",
#     agent=programmer,
#     expected_output="Python code that addresses and solves the problem.",
#     human_input=False,
# )

# task7 = Task(
#     description="Run the code written by the programmer and capture the results.",
#     agent=runner,
#     expected_output="Code execution results including outputs or errors.",
#     human_input=False,
# )

# task8 = Task(
#     description="Verify that the code output matches expected results and correctly solves the problem.",
#     agent=verifier_code,
#     expected_output="Validation report on code correctness.",
#     human_input=False,
# )

update_learner_model = Task(
    description="Update the internal learner model based on the current task outcome.",
    name="Update Learner Model",
    agent=learner,
    context=[select_math_topic, teach_math_topic, generate_math_problem, verify_math_problem],
    expected_output="Updated learner profile reflecting current progress and weaknesses.",
    human_input=False,
)

adjust_difficulty_level = Task(
    description="Adjust the difficulty level of future problems based on the learner model.",
    name="Adjust Difficulty Level",
    agent=level_adapter,
    context=[select_math_topic, teach_math_topic, generate_math_problem, verify_math_problem, update_learner_model],
    expected_output="Modified difficulty settings for the next learning iteration.",
    human_input=False,
)

motivate_student = Task(
    description="Motivate the student by giving personalized encouragement and progress feedback.",
    name="Motivate Student",
    agent=motivator,
    context=[select_math_topic, teach_math_topic, generate_math_problem, verify_math_problem, update_learner_model, adjust_difficulty_level],
    expected_output="Motivational message tailored to student performance.",
    human_input=False,
)

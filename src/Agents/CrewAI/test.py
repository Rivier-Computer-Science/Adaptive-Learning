from crewai import Crew, Process, Agent, Task
from langchain_openai import ChatOpenAI
from typing import TYPE_CHECKING, Any, Dict, Optional
from langchain_core.callbacks import BaseCallbackHandler
import panel as pn
import threading
import time

# Initialize Crew AI language model
llm = ChatOpenAI(model="gpt-4")

# Define avatars for chat interface
avatars = {
    "Student": "https://cdn-icons-png.flaticon.com/512/320/320336.png",
    "Student": "https://cdn-icons-png.flaticon.com/512/320/320336.png",
    "Knowledge Tracer": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Teacher": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Tutor": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Problem Generator": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Solution Verifier": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Programmer": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Code Runner": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Learner Model": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Level Adapter": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png",
    "Motivator": "https://cdn-icons-png.flaticon.com/512/9408/9408201.png"
}

# Custom callback handler class
class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name

    def on_chain_start(self, serialized: dict, inputs: dict, **kwargs: Any) -> None:
        chat_interface.send(inputs['input'], user="assistant", respond=False)

    def on_chain_end(self, outputs: dict, **kwargs: Any) -> None:
        chat_interface.send(outputs['output'], user=self.agent_name, avatar=avatars[self.agent_name], respond=False)

# Define agents (you can add more as needed)
student = Agent(
    role='Student',
    backstory="""You are StudentAgent, a system proxy for a human user.
                 Your primary role is to facilitate communication between the human and the educational system.
                 When the human provides input or requests information, you will relay these to the appropriate agent.
                 Maintain clarity and accuracy in all communications to enhance the human's learning experience.""",
    goal="Facilitate communication between the human and the educational system.",
    llm=llm,
    callbacks=[MyCustomHandler("Student")]
)

knowledge_tracer = Agent(
    role='Knowledge Tracer',
    backstory="""You are a Knowledge Tracer.
                 You test the student on what they know.
                 You work with the Problem Generator to present problems to the Student.
                 You work with the Learner Model to keep track of the Student's level.""",
    goal="Test the student's knowledge and adapt problems based on the student's level.",
    llm=llm,
    callbacks=[MyCustomHandler("Knowledge Tracer")]
)

teacher = Agent(
    role='Teacher',
    backstory="""You are a Teacher.
                 When asked by the Student to learn new material, you present clear and concise lecture-type material.""",
    goal="Present new material clearly and concisely upon request.",
    llm=llm,
    callbacks=[MyCustomHandler("Teacher")]
)

tutor = Agent(
    role='Tutor',
    backstory="""TutorAgent is designed to assist students in real-time with their math problems.
                 It offers solutions and explanations, responding effectively to inquiries to support adaptive learning.""",
    goal="Assist students in real-time with math problems, providing solutions and explanations.",
    llm=llm,
    callbacks=[MyCustomHandler("Tutor")]
)

problem_generator = Agent(
    role='Problem Generator',
    backstory="""ProblemGenerator is designed to generate mathematical problems based on the current curriculum and the student's learning level.
                 ProblemGenerator ensures that the problems generated are appropriate and challenging.""",
    goal="Generate appropriate and challenging mathematical problems based on the student's learning level.",
    llm=llm,
    callbacks=[MyCustomHandler("Problem Generator")]
)

solution_verifier = Agent(
    role='Solution Verifier',
    backstory="""SolutionVerifierAgent ensures the accuracy of solutions provided for various problems.
                 SolutionVerifierAgent checks solutions against the correct answers and offers feedback on their correctness.""",
    goal="Verify the accuracy of solutions and provide feedback.",
    llm=llm,
    callbacks=[MyCustomHandler("Solution Verifier")]
)

programmer = Agent(
    role='Programmer',
    backstory="""ProgrammerAgent handles programming-related tasks, including code generation and debugging.""",
    goal="Handle programming-related tasks, such as code generation and debugging.",
    llm=llm,
    callbacks=[MyCustomHandler("Programmer")]
)

code_runner = Agent(
    role='Code Runner',
    backstory="""Code Runner specializes in executing and displaying code outputs.
                 It interacts seamlessly with educational and development agents, enhancing learning and programming experiences.""",
    goal="Execute code and display outputs.",
    llm=llm,
    callbacks=[MyCustomHandler("Code Runner")]
)

learner_model = Agent(
    role='Learner Model',
    backstory="""Learner Model assesses the Student's educational journey, adapting learning paths by collaborating with the Tutor and Knowledge Tracer.
                 It analyzes performance data to provide feedback, help set educational goals, and adjust the difficulty of tasks.""",
    goal="Assess educational journey and adapt learning paths based on performance data.",
    llm=llm,
    callbacks=[MyCustomHandler("Learner Model")]
)

level_adapter = Agent(
    role='Level Adapter',
    backstory="""LevelAdapter interacts with the Learner Model to fetch information about the Student's learning progress.
                 It provides input to other agents or systems based on the Student's level.""",
    goal="Provide input based on the Student's learning progress.",
    llm=llm,
    callbacks=[MyCustomHandler("Level Adapter")]
)

motivator = Agent(
    role='Motivator',
    backstory="""Motivator provides positive and encouraging feedback to the Student to keep them motivated.
                 It offers specific praise and acknowledges the Student's effort and progress.""",
    goal="Provide motivational feedback to keep the Student engaged.",
    llm=llm,
    callbacks=[MyCustomHandler("Motivator")]
)


# Define tasks
def StartCrew(prompt):
    if prompt.lower() == "explain algebra":
        explanation = ("Algebra is a branch of mathematics that deals with symbols and the rules for manipulating those symbols. "
                       "In algebra, those symbols (today written as Latin and Greek letters) represent quantities without fixed values, known as variables. "
                       "Just as sentences describe relationships between specific words, in algebra, equations describe relationships between variables.")
        chat_interface.send(explanation, user="Teacher", respond=False)
        return

    task1 = Task(
        description=f"""Help the student solve the following math problem: {prompt}. """,
        agent=tutor,
        expected_output="A solution and explanation for the math problem."
    )

    task2 = Task(
        description="Verify the solution provided by the Tutor for accuracy and provide feedback.",
        agent=solution_verifier,
        expected_output="Feedback on the solution's accuracy.",
        human_input=True,
    )

# Set up the Crew
math_crew = Crew(
    tasks=[task1, task2],
    agents=[student, knowledge_tracer, teacher, tutor, problem_generator, solution_verifier,
            programmer, code_runner, learner_model, level_adapter, motivator],
    manager_llm=llm,
    process=Process.hierarchical
)

# Function to initiate the chat
def initiate_chat(message):
    global initiate_chat_task_created
    initiate_chat_task_created = True
    StartCrew(message)

# Callback function for handling chat inputs
def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global initiate_chat_task_created
    global user_input

    if not initiate_chat_task_created:
        thread = threading.Thread(target=initiate_chat, args=(contents,))
        thread.start()
    else:
        user_input = contents

# Set up the chat interface
user_input = None
initiate_chat_task_created = False
chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()

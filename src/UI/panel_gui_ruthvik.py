###############################################################################
#
# Ruthvik - your goal is to modify only this file and get the Agents to respond
#           in some logical manner
#
#           Pick any reasonable prompt like help me learn Algebra
#
###############################################################################


import autogen
import panel as pn
import os
import asyncio
from typing import List, Dict
from src import globals
from src.UI.avatar import avatar

# Importing Agents
from ..Agents.student_agent import StudentAgent
from ..Agents.knowledge_tracer_agent import KnowledgeTracerAgent
from ..Agents.teacher_agent import TeacherAgent
from ..Agents.tutor_agent import TutorAgent
from ..Agents.problem_generator_agent import ProblemGeneratorAgent
from ..Agents.solution_verifier_agent import SolutionVerifierAgent
from ..Agents.programmer_agent import ProgrammerAgent
from ..Agents.code_runner_agent import CodeRunnerAgent
from ..Agents.learner_model_agent import LearnerModelAgent
from ..Agents.level_adapter_agent import LevelAdapterAgent
from ..Agents.motivator_agent import MotivatorAgent
from ..Agents.group_chat_manager_agent import CustomGroupChatManager

os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Setting up agents
student = StudentAgent()
knowledge_tracer = KnowledgeTracerAgent(
    human_input_mode='ALWAYS',
    description="""You are a Knowledge Tracer.
                    You test the student on what they know.
                    You work with the Problem Generator to present problems to the Student.
                    You work with the Learner Model to keep track of the Student's level.""",
    system_message="""You are a Knowledge Tracer.
                    You test the student on what they know.
                    You work with the Problem Generator to present problems to the Student.
                    You work with the Learner Model to keep track of the Student's level."""
)
teacher = TeacherAgent(
    human_input_mode='NEVER',
    description="""You are a Teacher.
                 When asked by the Student to learn new material, you present clear and concise lecture-type material.""",
    system_message="""You are a Teacher.
                 When asked by the Student to learn new material, you present clear and concise lecture-type material."""
)
tutor = TutorAgent(
    human_input_mode='NEVER',
    description="""TutorAgent is designed to assist students in real-time with their math problems. It offers solutions and explanations, responding effectively to inquiries to support adaptive learning.""",
    system_message="""TutorAgent is designed to assist students in real-time with their math problems. It offers solutions and explanations, responding effectively to inquiries to support adaptive learning."""
)
problem_generator = ProblemGeneratorAgent(
    human_input_mode='NEVER',
    description="""ProblemGenerator is designed to generate mathematical problems based on the current curriculum and the student's learning level.
                ProblemGenerator ensures that the problems generated are appropriate and challenging.""",
    system_message="""ProblemGenerator is designed to generate mathematical problems based on the current curriculum and the student's learning level.
                ProblemGenerator ensures that the problems generated are appropriate and challenging."""
)
solution_verifier = SolutionVerifierAgent(
    human_input_mode='ALWAYS',
    description="""SolutionVerifierAgent ensures the accuracy of solutions provided for various problems. SolutionVerifierAgent checks solutions against the correct answers and offers feedback on their correctness.""",
    system_message="""SolutionVerifierAgent ensures the accuracy of solutions provided for various problems. SolutionVerifierAgent checks solutions against the correct answers and offers feedback on their correctness."""
)
programmer = ProgrammerAgent()
code_runner = CodeRunnerAgent(
    human_input_mode='NEVER',
    description="""Code Runner specializes in executing and displaying code outputs, providing real-time feedback. It interacts seamlessly with educational and development agents, enhancing learning and programming experiences.""",
    system_message="""Code Runner specializes in executing and displaying code outputs, providing real-time feedback. It interacts seamlessly with educational and development agents, enhancing learning and programming experiences."""
)
learner_model = LearnerModelAgent(
    human_input_mode='ALWAYS',
    description="""Learner Model assesses the Student's educational journey, adapting learning paths by collaborating with the Tutor and Knowledge Tracer. Learner Model analyzes performance data to provide feedback, help set educational goals, and adjust the difficulty of tasks.""",
    system_message="""Learner Model assesses the Student's educational journey, adapting learning paths by collaborating with the Tutor and Knowledge Tracer. Learner Model analyzes performance data to provide feedback, help set educational goals, and adjust the difficulty of tasks."""
)
level_adapter = LevelAdapterAgent(
    human_input_mode='NEVER',
    description="""LevelAdapter fetches information about the Student's learning progress from the Learner Model and provides input to other agents or systems based on the Student's level.""",
    system_message="""LevelAdapter fetches information about the Student's learning progress from the Learner Model and provides input to other agents or systems based on the Student's level."""
)
motivator = MotivatorAgent(
    human_input_mode='NEVER',
    description="""Motivator provides positive and encouraging feedback to keep the Student motivated.""",
    system_message="""Motivator provides positive and encouraging feedback to keep the Student motivated."""
)

# Dictionary of all agents
agents_dict = {
    "student": student,
    "knowledge_tracer": knowledge_tracer,
    "teacher": teacher,
    "tutor": tutor,
    "problem_generator": problem_generator,
    "solution_verifier": solution_verifier,
    "programmer": programmer,
    "code_runner": code_runner,
    "learner_model": learner_model,
    "level_adapter": level_adapter,
    "motivator": motivator
}

# Define agent transitions
DISALLOWED_TRANSITIONS = 'DISALLOWED'

disallowed_agent_transitions = {
    student: [solution_verifier, programmer, code_runner, learner_model, level_adapter, motivator],
    tutor: [programmer, code_runner],
    teacher: [knowledge_tracer, problem_generator, solution_verifier, programmer, code_runner, learner_model, level_adapter, motivator],
    knowledge_tracer: [teacher, tutor, motivator],
    problem_generator: [teacher, solution_verifier, programmer, code_runner, motivator],
    solution_verifier: [student, teacher, problem_generator, learner_model, level_adapter, motivator],
    programmer: [student, tutor, teacher, knowledge_tracer, learner_model, level_adapter, motivator],
    code_runner: [student, teacher, tutor, knowledge_tracer, problem_generator, learner_model, level_adapter, motivator],
    learner_model: [student, teacher, problem_generator, solution_verifier, programmer, code_runner],
    level_adapter: [student, teacher, solution_verifier, programmer, code_runner, motivator],
    motivator: [tutor, teacher, knowledge_tracer, problem_generator, solution_verifier, programmer, code_runner, learner_model, level_adapter]
}

# Creating the GroupChat
groupchat = autogen.GroupChat(
    agents=list(agents_dict.values()),
    messages=[],
    max_round=40,
    send_introductions=True,
    speaker_transitions_type=DISALLOWED_TRANSITIONS,
    allowed_or_disallowed_speaker_transitions=disallowed_agent_transitions
)

# Custom GroupChat Manager
manager = CustomGroupChatManager(groupchat=groupchat)

# Panel Interface setup
def create_app():
    pn.extension(design="material")

    async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
        if not globals.initiate_chat_task_created:
            asyncio.create_task(manager.delayed_initiate_chat(tutor, manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")

    chat_interface = pn.chat.ChatInterface(callback=callback)

    def print_messages(recipient, messages, sender, config):
        print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

        content = messages[-1]['content']

        if all(key in messages[-1] for key in ['name']):
            chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)

        return False, None  # required to ensure the agent communication flow continues

    # Register chat interface with ConversableAgent
    for agent in groupchat.agents:
        agent.chat_interface = chat_interface
        agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

    # Create the Panel app object with the chat interface
    app = pn.template.BootstrapTemplate(title=globals.APP_NAME)
    app.main.append(
        pn.Column(
            chat_interface
        )
    )
    chat_interface.send("Welcome to the Adaptive Learning Environment! How can I assist you today?", user="System", respond=False)

    return app

# Main application entry point
if __name__ == "__main__":
    app = create_app()
    pn.serve(app)

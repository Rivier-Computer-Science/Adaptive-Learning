import autogen
import panel as pn
import openai
import os
import time
import asyncio
from typing import List, Dict
import logging
from src import globals
from src.UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

globals.input_future = None

from ..Agents.base_agent import MyBaseAgent
from ..Agents.conversable_agent import MyConversableAgent
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

student = StudentAgent()

kt_description = """You are a Knowledge Tracer.
                    You test the student on what they know.
                    You work with the Problem Generator to present problems to the Student.
                    You work with the Learner Model to keep track of the Student's level.
            """
knowledge_tracer = KnowledgeTracerAgent(
    human_input_mode='ALWAYS',
    description=kt_description,
    system_message=kt_description    
)

t_description =   """You are a Teacher.
                 When asked by the Student to learn new material, you present clear and concise lecture-type material.
                 """
teacher = TeacherAgent(
    human_input_mode='NEVER',
    description=t_description,
    system_message=t_description     
)

tut_description = """  TutorAgent is designed to assist students in real-time with their math problems. It offers solutions and explanations, responding effectively to inquiries to support adaptive learning. TutorAgent's goal is to make learning easier and more interactive for students.
                        """
tutor = TutorAgent(
    human_input_mode='NEVER',
    description=tut_description,
    system_message=tut_description      
)

pg_description = """ProblemGenerator is designed to generate mathematical problems based on the current curriculum and the student's learning level.
                ProblemGenerator ensures that the problems generated are appropriate and challenging."""
                    
pg_system_message = """ProblemGenerator will generate mathematical problems based on the current curriculum and the student's learning level.
                        ProblemGenerator ensures that the problems generated are appropriate and challenging."""

problem_generator = ProblemGeneratorAgent(
    human_input_mode='NEVER',
    description=pg_description,
    system_message=pg_system_message     
)

sv_description = """SolutionVerifierAgent ensures the accuracy of solutions provided for various problems. SolutionVerifierAgent checks solutions against the correct answers and offers feedback on their correctness."""
    
sv_system_message = """SolutionVerifierAgent's task is to verify the correctness of solutions submitted by comparing them against the correct answers and providing feedback on their accuracy."""

solution_verifier = SolutionVerifierAgent(
    human_input_mode='ALWAYS',
    description=sv_description,
    system_message=sv_description     
)

programmer = ProgrammerAgent()

cr_description = """As a vital component of a collaborative agent framework, Code Runner specializes in executing and displaying code outputs. Code Runner interacts seamlessly with educational and development agents, enhancing learning and programming experiences. By providing real-time feedback on code execution, Code Runner support users and other agents in refining and understanding complex code segments, contributing to a more robust and interactive learning environment."""
cr_system_message = """Code Runner's function is to execute and display code outputs, providing real-time feedback. Code Runner interacts seamlessly with educational and development agents, enhancing learning and programming experiences. By refining and understanding complex code segments, Code Runner supports users and other agents, contributing to a more robust and interactive learning environment. """
code_runner = CodeRunnerAgent(
    human_input_mode='NEVER',
    description=cr_description,
    system_message=cr_system_message  
)

lv_description ="""
    LevelAdapter is an agent that interacts with the Learner Model to fetch information about the Student's learning progress.
    LevelAdapter provides input to other agents or systems based on the Student's level.
    """    
lv_system_message ="""
    LevelAdapter is ready to interact with the Learner Model to provide information about the Student's learning progress.
    LevelAdapter can provide input to other agents or systems based on the Student's level.
    """
level_adapter = LevelAdapterAgent(
    human_input_mode='NEVER',
    description=lv_description,
    system_message=lv_system_message   
)

m_description = """ You provide positive and encouraging feedback to the Student to keep them motivated.
                        Only provide motivation to the Student. 
                        Offer specific praise and acknowledge the Student's effort and progress.
                        Do not provide motivating comments to any other agent except the Student.
                        """
motivator = MotivatorAgent(
    human_input_mode='NEVER',
    description=m_description,
    system_message=m_description  
)

lm_description="""Learner Model is a diligent and meticulous learning tracker. Learner Model assess the Student's educational journey, adapting learning paths by collaborating with the Tutor and Knowledge Tracer. Learner Model analyzes performance data to provide feedback, help set educational goals, and adjust the difficulty of tasks. Learner Model ensures that the learning experience is tailored to the Student’s evolving capabilities and needs."""
lm_system_message="""Learner Model's function is to diligently track the Student's educational journey. Learner Model assesses performance data, collaborates with the Tutor and Knowledge Tracer, and adapts learning paths to provide feedback. Learner Model helps set educational goals and adjusts the difficulty of tasks, ensuring that the learning experience is tailored to the Student’s evolving capabilities and needs. """        
learner_model = LearnerModelAgent(
    human_input_mode='ALWAYS',
    description=lm_description,
    system_message=lm_system_message
)

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

TRANSITIONS = 'DISALLOWED'

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
    motivator: [teacher, problem_generator, solution_verifier, programmer, code_runner, learner_model]
}

chat_manager = CustomGroupChatManager(agents_dict, disallowed_agent_transitions)

def create_app():
    output_pane = pn.pane.Markdown("", sizing_mode="stretch_both")
    chat_input = pn.widgets.TextInput(placeholder="Type your message here...", sizing_mode="stretch_width")
    send_button = pn.widgets.Button(name="Send", button_type="primary", sizing_mode="fixed")

    async def process_input(event):
        user_input = chat_input.value
        chat_input.value = ""

        student_response = await chat_manager.chat(student, user_input)
        tutor_response = await chat_manager.chat(tutor, student_response.content)

        output_pane.object += f"**Student:** {user_input}\n\n"
        output_pane.object += f"**Tutor:** {tutor_response.content}\n\n"

    send_button.on_click(lambda event: asyncio.create_task(process_input(event)))

    app_layout = pn.Column(
        avatar,
        output_pane,
        pn.Row(chat_input, send_button),
        sizing_mode="stretch_both"
    )

    return app_layout

if __name__.startswith("bokeh"):
    pn.extension()
    app = create_app()
    app.show(port=5007)

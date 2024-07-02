import autogen
import panel as pn
import os
import asyncio
from typing import List, Dict
from src import globals
from src.UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

globals.input_future = None


###############################################################################
#
# Test/Interrogate Algebra Use Case Description
#
# Use-Case Name: Test/Interrogate Algebra
# ID: 5.3
# Importance Level: Medium
# Primary Actor: Teacher Agent
# Use Case Type: Interactive
#
# Stakeholders and Interests:
#   - Primary Actor: Initiates the test/interrogation process to assess algebra knowledge.
#   - Student Agent: Receives questions and provides responses.
#   - Knowledge Tracer Agent: Monitors and logs student performance during the test/interrogation.
#
# Brief Description:
# This use case involves the Teacher Agent testing or interrogating a Student Agent on the topic of algebra. The Teacher Agent presents material, asks questions, evaluates responses, and may adjust the difficulty level based on the Student Agent's performance.
#
# Trigger:
# The Teacher Agent decides to assess the Student Agent's knowledge on the subject of algebra.
#
# Type:
# Interactive - involves direct interaction between Teacher Agent and Student Agent.
#
# Relationships:
#   - Association: Teacher interacts with Student.
#   - Include: Knowledge Tracer monitors and logs student performance.
#
# Normal Flow of Events:
# 1. Teacher Agent selects algebra as the subject to test.
# 2. Tutor Agent retrieves previous learning levels from the Knowledge Tracer Agent.
# 3. Tutor Agent asks Teacher Agent to present algebraic material at the Student Agent's level.
# 4. Teacher Agent presents algebraic material in lecture format.
# 5. Teacher Agent presents algebraic material in video format using educational resources like Khan Academy.
# 6. Tutor Agent asks Teacher Agent to determine the Student Agent's mastery of the material.
# 7. Teacher Agent waits for input on when to introduce new algebraic material.
#
# SubFlows:
# S-1: If Student Agent demonstrates insufficient mastery, Tutor Agent may request further review of existing material.
#
# Alternate/Exceptional Flows:
# - If the Student Agent consistently struggles with presented material, Teacher Agent may adjust the material format or difficulty level.
#
###############################################################################

# Note: Implementation details and agent interactions should be detailed in the panel_gui_test_interrogate_algebra.py file.
# Follow the provided guidelines for file structure and agent descriptions overriding.


############################################################################################
#
#  DEFINE AGENTS
#
############################################################################################
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


# Agents
#####################################################################################
student = StudentAgent()
knowledge_tracer = KnowledgeTracerAgent()
teacher = TeacherAgent()
tutor = TutorAgent()
problem_generator = ProblemGeneratorAgent()
solution_verifier = SolutionVerifierAgent()
programmer = ProgrammerAgent()
code_runner = CodeRunnerAgent()
learner_model = LearnerModelAgent()
level_adapter = LevelAdapterAgent()
motivator = MotivatorAgent()

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


####################################################################################################
#
#  Define Agent Transitions: Unconstrained, Allowed, or Disallowed
#
####################################################################################################
TRANSITIONS = 'DISALLOWED'

if TRANSITIONS == 'DISALLOWED':
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

    groupchat = autogen.GroupChat(
        agents=list(agents_dict.values()), 
        messages=[],
        max_round=40,
        send_introductions=True,
        speaker_transitions_type="disallowed",
        allowed_or_disallowed_speaker_transitions=disallowed_agent_transitions
    )
    
elif TRANSITIONS == 'ALLOWED':
    allowed_agent_transitions = {
        student: [tutor],
        tutor: [student, teacher, problem_generator, solution_verifier, motivator],
        teacher: [student, tutor, learner_model],
        knowledge_tracer: [student, problem_generator, learner_model, level_adapter],
        problem_generator: [tutor],
        solution_verifier: [programmer],
        programmer: [code_runner],
        code_runner: [tutor, solution_verifier],
        learner_model: [knowledge_tracer, level_adapter],
        level_adapter: [tutor, problem_generator, learner_model],
        motivator: [tutor]
    }

    groupchat = autogen.GroupChat(
        agents=list(agents_dict.values()), 
        messages=[],
        max_round=40,
        send_introductions=True,
        speaker_transitions_type="allowed",
        allowed_or_disallowed_speaker_transitions=allowed_agent_transitions
    )

else:  # Unconstrained
    groupchat = autogen.GroupChat(
        agents=list(agents_dict.values()), 
        messages=[],
        max_round=40,
        send_introductions=True,
    )


manager = CustomGroupChatManager(groupchat=groupchat)

####################################################################################
#
# Application Code
#
####################################################################################

# --- Panel Interface ---
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
    chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="System", respond=False)
    
    return app


if __name__ == "__main__":
    app = create_app()
    pn.serve(app)

import os
import sys
import panel as pn
import asyncio
from crewai import Crew, Process, Agent, Task
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from typing import Dict, Any

# Ensure the src directory is in the system path for absolute imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(src_dir)

# Import from src
from src import globals
from src.UI.avatar import avatar
from src.Agents.base_agent import MyBaseAgent
from src.Agents.conversable_agent import MyConversableAgent
from src.Agents.student_agent import StudentAgent
from src.Agents.knowledge_tracer_agent import KnowledgeTracerAgent
from src.Agents.teacher_agent import TeacherAgent
from src.Agents.tutor_agent import TutorAgent
from src.Agents.problem_generator_agent import ProblemGeneratorAgent
from src.Agents.solution_verifier_agent import SolutionVerifierAgent
from src.Agents.programmer_agent import ProgrammerAgent
from src.Agents.code_runner_agent import CodeRunnerAgent
from src.Agents.learner_model_agent import LearnerModelAgent
from src.Agents.level_adapter_agent import LevelAdapterAgent
from src.Agents.motivator_agent import MotivatorAgent

# Initialize panel extension
pn.extension(design="material")

# Set environment variable
os.environ["AUTOGEN_USE_DOCKER"] = "0"

globals.input_future = None

# Custom callback handler class
class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        chat_interface.send(inputs['input'], user="assistant", respond=False)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        chat_interface.send(outputs['output'], user=self.agent_name, avatar=avatar.get(self.agent_name, ""), respond=False)

llm = ChatOpenAI(model="gpt-4o")

# Initialize agents without 'backstory' and other custom arguments
student = StudentAgent(
    llm=llm,
    callbacks=[MyCustomHandler("StudentAgent")]
)

knowledge_tracer = KnowledgeTracerAgent(
    llm=llm,
    callbacks=[MyCustomHandler("KnowledgeTracerAgent")]
)

teacher = TeacherAgent(
    llm=llm,
    callbacks=[MyCustomHandler("TeacherAgent")]
)

tutor = TutorAgent(
    llm=llm,
    callbacks=[MyCustomHandler("TutorAgent")]
)

problem_generator = ProblemGeneratorAgent(
    llm=llm,
    callbacks=[MyCustomHandler("ProblemGeneratorAgent")]
)

solution_verifier = SolutionVerifierAgent(
    llm=llm,
    callbacks=[MyCustomHandler("SolutionVerifierAgent")]
)

programmer = ProgrammerAgent(
    llm=llm,
    callbacks=[MyCustomHandler("ProgrammerAgent")]
)

code_runner = CodeRunnerAgent(
    llm=llm,
    callbacks=[MyCustomHandler("CodeRunnerAgent")]
)

learner_model = LearnerModelAgent(
    llm=llm,
    callbacks=[MyCustomHandler("LearnerModelAgent")]
)

level_adapter = LevelAdapterAgent(
    llm=llm,
    callbacks=[MyCustomHandler("LevelAdapterAgent")]
)

motivator = MotivatorAgent(
    llm=llm,
    callbacks=[MyCustomHandler("MotivatorAgent")]
)

# Start Panel interface
chat_interface = pn.widgets.ChatInterface(
    name="Adaptive Math Tutor",
    intro_text="Welcome to the Adaptive Math Tutor!",
    width=800,
    height=600,
    send_text="Send",
    avatars=avatar
)

# Display the chat interface
pn.serve(chat_interface, start=True, show=True)

import autogen
from .base_agent import MyBaseAgent
from .conversable_agent import MyConversableAgent
from .student_agent import StudentAgent
from .knowledge_tracer_agent import KnowledgeTracerAgent
from .teacher_agent import TeacherAgent
from .tutor_agent import TutorAgent
from .problem_generator_agent import ProblemGeneratorAgent
from .solution_verifier_agent import SolutionVerifierAgent
from .programmer_agent import ProgrammerAgent
from .code_runner_agent import CodeRunnerAgent
from .learner_model_agent import LearnerModelAgent
from .level_adapter_agent import LevelAdapterAgent
from .motivator_agent import MotivatorAgent

from .group_chat_manager_agent import CustomGroupChatManager

from src.Models.llm_config import gpt3_config




# Agents
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



# agents_list = [student, knowledge_tracer, teacher, tutor, problem_generator, solution_verifier,
#               programmer, code_runner, learner_model, level_adapter, motivator]
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



 

       




import autogen
import os
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
from .gamification_agent import GamificationAgent
from .mastery_agent import MasteryAgent
from .career_growth_agent import CareerGrowthAgent  # ✅ Import the agent
from .certification_recommendation_agent import CertificationRecommendationAgent  # ✅ Import the agent
from .student_career_dashboard_agent import StudentCareerDashboardAgent

# Create an instance of StudentCareerDashboardAgent
student_career_dashboard = StudentCareerDashboardAgent()


from src.Models.llm_config import gpt3_config
from enum import Enum

os.environ["AUTOGEN_USE_DOCKER"] = "False"

class AgentKeys(Enum):
    TEACHER = 'teacher'
    TUTOR = 'tutor'
    STUDENT = 'student'
    KNOWLEDGE_TRACER = 'knowledge_tracer'
    PROBLEM_GENERATOR = 'problem_generator'
    SOLUTION_VERIFIER = 'solution_verifier'
    PROGRAMMER = 'programmer'
    CODE_RUNNER = 'code_runner'
    CODE_RUNNER_VERIFIER = 'code_runner_verifier'
    LEARNER_MODEL = 'learner_model'
    LEVEL_ADAPTER = 'level_adapter'
    MOTIVATOR = 'motivator'
    GAMIFICATION = 'gamification'
    MASTERY = 'mastery'  # Added MASTERY key
    JOB_FINDER = 'job_finder'
    CAREER_GROWTH = 'career_growth'  # ✅ Added Career Growth Agent
    CERTIFICATION_RECOMMENDATION = 'certification_recommendation'  # ✅ Added Certification Recommendation Agent
    STUDENT_CAREER_DASHBOARD = 'student_career_dashboard'

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
gamification = GamificationAgent(name="GamificationAgent")
mastery = MasteryAgent()  # Added MasteryAgent instance
career_growth = CareerGrowthAgent()  # ✅ Added Career Growth Agent instance
certification_recommendation = CertificationRecommendationAgent()  # ✅ Added Certification Recommendation Agent instance




agents_dict = {
    AgentKeys.STUDENT.value: student,
    AgentKeys.KNOWLEDGE_TRACER.value: knowledge_tracer,
    AgentKeys.TEACHER.value: teacher,
    AgentKeys.TUTOR.value: tutor,
    AgentKeys.PROBLEM_GENERATOR.value: problem_generator,
    AgentKeys.SOLUTION_VERIFIER.value: solution_verifier,
    AgentKeys.PROGRAMMER.value: programmer,
    AgentKeys.CODE_RUNNER.value: code_runner,
    AgentKeys.LEARNER_MODEL.value: learner_model,
    AgentKeys.LEVEL_ADAPTER.value: level_adapter,
    AgentKeys.MOTIVATOR.value: motivator,
    AgentKeys.GAMIFICATION.value: gamification,
    AgentKeys.MASTERY.value: mastery,  # Added MasteryAgent to agents_dict
    AgentKeys.STUDENT_CAREER_DASHBOARD.value: student_career_dashboard,
}

agents_dict_by_name = {
    "StudentAgent": student,
    "KnowledgeTracerAgent": knowledge_tracer,
    "TeacherAgent": teacher,
    "TutorAgent": tutor,
    "ProblemGeneratorAgent": problem_generator,
    "SolutionVerifierAgent": solution_verifier,
    "ProgrammerAgent": programmer,
    "CodeRunnerAgent": code_runner,
    "LearnerModelAgent": learner_model,
    "LevelAdapterAgent": level_adapter,
    "MotivatorAgent": motivator,
    "GamificationAgent": gamification,
    "MasteryAgent": mastery,  # Added MasteryAgent to agents_dict_by_name
}

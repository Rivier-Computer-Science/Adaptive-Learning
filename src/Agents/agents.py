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
from .career_growth_agent import CareerGrowthAgent
from .competency_extraction_agent import CompetencyExtractionAgent
from .gap_analysis_agent import GapAnalysisAgent
from .personalized_learning_plan_agent import PersonalizedLearningPlanAgent
from .resource_ranking_agent import ResourceRankingAgent
from .certification_recommendation_agent import CertificationRecommendationAgent  # ✅ Import the agent
from .student_career_dashboard_agent import StudentCareerDashboardAgent
from src.Models.llm_config import gpt3_config
from .user_preference_update_agent import UserPreferenceUpdateAgent
from .realtime_career_adjustment_agent import RealTimeCareerAdjustmentAgent
from .recommendation_testing_agent import RecommendationTestingAgent
from .ai_evaluation_agent import AIEvaluationAgent
from .scenario_simulation_agent import ScenarioSimulationAgent
from .dynamic_recommendation_testing_agent import DynamicRecommendationTestingAgent
from src.Models.llm_config import gpt4_config
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
    COMPETENCY_EXTRACTION = 'competency_extraction'
    GAP_ANALYSIS = 'gap_analysis'
    PERSONALIZED_PLAN = 'personalized_plan'
    RESOURCE_RANKING = 'resource_ranking'
    USER_PREF_UPDATE = 'user_pref_update'
    REALTIME_CAREER_ADJUSTMENT = 'realtime_career_adjustment'
    RECOMMENDATION_TESTING = 'recommendation_testing'
    STATE_DEFINITION = "StateDefinitionAgent"
    STATE_TRANSITION = "StateTransitionAgent"
    DATA_SYNC = "DataSynchronizationAgent"
    STATE_MACHINE_TESTING = "StateMachineTestingAgent"
    AI_EVALUATION = "AIEvaluationAgent"
    SCENARIO_SIMULATION = "ScenarioSimulationAgent"
    DYNAMIC_RECOMMENDATION_TESTING = "DynamicRecommendationTestingAgent"
    JOB_FINDER = 'job_finder'
    CAREER_GROWTH = 'career_growth'  # ✅ Added Career Growth Agent
    CERTIFICATION_RECOMMENDATION = 'certification_recommendation'  # ✅ Added Certification Recommendation Agent
    STUDENT_CAREER_DASHBOARD = 'student_career_dashboard'


# Agent


# Instantiate agents
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
competency_extraction = CompetencyExtractionAgent()
gap_analysis = GapAnalysisAgent()
personalized_plan = PersonalizedLearningPlanAgent()
resource_ranking = ResourceRankingAgent()
mastery = MasteryAgent()  # Added MasteryAgent instance
career_growth = CareerGrowthAgent()  # ✅ Added Career Growth Agent instance
certification_recommendation = CertificationRecommendationAgent()  # ✅ Added Certification Recommendation Agent instance
user_pref_update = UserPreferenceUpdateAgent()
career_adjustment = RealTimeCareerAdjustmentAgent()
recommendation_testing = RecommendationTestingAgent()
ai_evaluation = AIEvaluationAgent()
scenario_simulation = ScenarioSimulationAgent()
dynamic_testing = DynamicRecommendationTestingAgent()


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
    # Career-related
    AgentKeys.CAREER_GROWTH.value: career_growth,
    AgentKeys.CERTIFICATION_RECOMMENDATION.value: certification_recommendation,
    AgentKeys.COMPETENCY_EXTRACTION.value: competency_extraction,
    AgentKeys.GAP_ANALYSIS.value: gap_analysis,
    AgentKeys.PERSONALIZED_PLAN.value: personalized_plan,
    AgentKeys.RESOURCE_RANKING.value: resource_ranking,
    AgentKeys.USER_PREF_UPDATE.value: user_pref_update,
    AgentKeys.REALTIME_CAREER_ADJUSTMENT.value: career_adjustment,
    AgentKeys.RECOMMENDATION_TESTING.value: recommendation_testing,
    AgentKeys.AI_EVALUATION.value: ai_evaluation,
    AgentKeys.SCENARIO_SIMULATION.value: scenario_simulation,
    AgentKeys.DYNAMIC_RECOMMENDATION_TESTING.value: dynamic_testing
    
    
}


agents_dict_by_name = {
    agent.__class__.__name__: agent
    for agent in agents_dict.values()
}

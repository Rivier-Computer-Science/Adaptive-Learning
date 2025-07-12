from src.Agents.agents import (
    AgentKeys,
    StudentAgent, KnowledgeTracerAgent, TeacherAgent, TutorAgent,
    ProblemGeneratorAgent, SolutionVerifierAgent, ProgrammerAgent,
    CodeRunnerAgent, LearnerModelAgent, LevelAdapterAgent, MotivatorAgent,
    GamificationAgent, MasteryAgent, CareerGrowthAgent, CompetencyExtractionAgent,
    GapAnalysisAgent, PersonalizedLearningPlanAgent, ResourceRankingAgent,
    UserPreferenceUpdateAgent, RealTimeCareerAdjustmentAgent,
    RecommendationTestingAgent, AIEvaluationAgent, ScenarioSimulationAgent,
    DynamicRecommendationTestingAgent
)

def get_fresh_agents_dict():
    return {
        AgentKeys.STUDENT.value: StudentAgent(),
        AgentKeys.KNOWLEDGE_TRACER.value: KnowledgeTracerAgent(),
        AgentKeys.TEACHER.value: TeacherAgent(),
        AgentKeys.TUTOR.value: TutorAgent(),
        AgentKeys.PROBLEM_GENERATOR.value: ProblemGeneratorAgent(),
        AgentKeys.SOLUTION_VERIFIER.value: SolutionVerifierAgent(),
        AgentKeys.PROGRAMMER.value: ProgrammerAgent(),
        AgentKeys.CODE_RUNNER.value: CodeRunnerAgent(),
        AgentKeys.LEARNER_MODEL.value: LearnerModelAgent(),
        AgentKeys.LEVEL_ADAPTER.value: LevelAdapterAgent(),
        AgentKeys.MOTIVATOR.value: MotivatorAgent(),
        AgentKeys.GAMIFICATION.value: GamificationAgent(name="GamificationAgent"),
        AgentKeys.MASTERY.value: MasteryAgent(),
        AgentKeys.CAREER_GROWTH.value: CareerGrowthAgent(),
        AgentKeys.COMPETENCY_EXTRACTION.value: CompetencyExtractionAgent(),
        AgentKeys.GAP_ANALYSIS.value: GapAnalysisAgent(),
        AgentKeys.PERSONALIZED_PLAN.value: PersonalizedLearningPlanAgent(),
        AgentKeys.RESOURCE_RANKING.value: ResourceRankingAgent(),
        AgentKeys.USER_PREF_UPDATE.value: UserPreferenceUpdateAgent(),
        AgentKeys.REALTIME_CAREER_ADJUSTMENT.value: RealTimeCareerAdjustmentAgent(),
        AgentKeys.RECOMMENDATION_TESTING.value: RecommendationTestingAgent(),
        AgentKeys.AI_EVALUATION.value: AIEvaluationAgent(),
        AgentKeys.SCENARIO_SIMULATION.value: ScenarioSimulationAgent(),
        AgentKeys.DYNAMIC_RECOMMENDATION_TESTING.value: DynamicRecommendationTestingAgent()
    }


from .conversable_agent import MyConversableAgent

class PersonalizedLearningPlanAgent(MyConversableAgent):
    def __init__(self, llm_config=None):
        super().__init__(
            name="PersonalizedLearningPlanAgent",
            llm_config=llm_config,
            system_message=self._system_message(),
            description="Suggests personalized learning resources like courses, books, and exercises based on identified skill gaps and career goals."
        )

    def _system_message(self):
        return (
            "You are the PersonalizedLearningPlanAgent. Your job is to generate personalized study plans for students. "
            "Use known student capabilities and skill gaps to recommend concrete learning resources such as online courses, books, practice exercises, or tutorials. "
            "Be specific and organized: list recommendations by topic or skill. Always tailor to the student's current level and learning preferences if known."
        )

    def create_learning_plan(self, student_profile, skill_gaps):
        prompt = (
            f"Student Profile: {student_profile}\n"
            f"Skill Gaps: {skill_gaps}\n"
            f"Please generate a personalized learning plan with resource recommendations."
        )
        return self.generate_response(prompt)

    def generate_response(self, prompt: str):
        return self.llm_config['config_list'][0]['model'](prompt) if self.llm_config else "[LLM response placeholder]"

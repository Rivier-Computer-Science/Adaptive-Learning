from .conversable_agent import MyConversableAgent

class GapAnalysisAgent(MyConversableAgent):
    def __init__(self, llm_config=None, **kwargs):
        system_message = (
            "You are GapAnalysisAgent, an expert in educational diagnostics. "
            "Your job is to analyze the student's current capabilities and compare them against "
            "industry or career pathway requirements. Use the provided competency list and student skills "
            "to identify specific gaps. Suggest areas for improvement with detailed explanations."
        )

        description = (
            "Analyzes skill gaps by comparing student capabilities to career-specific competencies. "
            "Provides detailed gap reports for use in planning personalized learning paths."
        )

        super().__init__(
            name="GapAnalysisAgent",
            system_message=system_message,
            description=description,
            llm_config=llm_config,
            **kwargs
        )

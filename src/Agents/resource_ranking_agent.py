from src.Agents.conversable_agent import MyConversableAgent

class ResourceRankingAgent(MyConversableAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="ResourceRankingAgent",
            system_message=self.resource_ranking_system_message(),
            description="Ranks and prioritizes learning resources based on effectiveness, relevance, and student preferences.",
            **kwargs
        )

    def resource_ranking_system_message(self):
        return (
            "You are ResourceRankingAgent, an expert in evaluating and ranking learning resources such as courses, books, tutorials, and exercises.\n"
            "Your goal is to recommend the highest-quality and most effective resources that align with the student’s personalized learning plan, skills, and goals.\n"
            "Rank the resources based on relevance, comprehensiveness, user reviews, and alignment with the desired competencies."
        )

    async def a_rank_resources(self, topic: str, resources: list):
        prompt = f"Given the topic '{topic}', rank the following learning resources based on effectiveness and relevance:\n{resources}\n"
        await self.a_send(prompt, recipient=self, request_reply=True)

    def last_ranked_resources(self):
        return self.last_message(agent=self)["content"]

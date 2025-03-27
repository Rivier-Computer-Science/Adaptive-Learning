from src.Agents.conversable_agent import MyConversableAgent

class CareerGrowthAgent(MyConversableAgent):
    description = "Provides career advancement guidance for students."
    system_message = """
        You are a Career Growth Agent responsible for helping students plan professional growth.
        Provide step-by-step career pathways, important skills, and progression strategies in the field they are interested in.
    """

    def __init__(self, llm_config=None, **kwargs):
        super().__init__(
            name="CareerGrowthAgent",
            llm_config=llm_config,
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )

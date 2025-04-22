from autogen import ConversableAgent

class DynamicRecommendationTestingAgent(ConversableAgent):
    def __init__(self, name="DynamicRecommendationTestingAgent", llm_config=None):
        super().__init__(name=name, llm_config=llm_config)

from autogen import ConversableAgent

class AIEvaluationAgent(ConversableAgent):
    def __init__(self, name="AIEvaluationAgent", llm_config=None):
        super().__init__(name=name, llm_config=llm_config)

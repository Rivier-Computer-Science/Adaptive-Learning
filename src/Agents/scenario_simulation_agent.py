from autogen import ConversableAgent

class ScenarioSimulationAgent(ConversableAgent):
    def __init__(self, name="ScenarioSimulationAgent", llm_config=None):
        super().__init__(name=name, llm_config=llm_config)

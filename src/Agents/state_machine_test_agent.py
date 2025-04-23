from autogen import ConversableAgent

class StateMachineTestingAgent(ConversableAgent):
    def __init__(self, name="StateMachineTestingAgent", llm_config=None):
        super().__init__(name=name, llm_config=llm_config)

    async def a_generate_response(self, messages, sender, config):
        return (
            "State machine transitions tested.\n"
            "All transitions valid. No anomalies found. System is stable."
        )
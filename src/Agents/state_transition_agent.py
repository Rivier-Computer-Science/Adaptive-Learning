from autogen import ConversableAgent

class StateTransitionAgent(ConversableAgent):
    def __init__(self, name="StateTransitionAgent", llm_config=None):
        super().__init__(name=name, llm_config=llm_config)

    async def a_generate_response(self, messages, sender, config):
        return (
            "State transition triggered.\n"
            "Student moved from 'Intermediate' to 'Advanced' based on recent competency achievement."
        )
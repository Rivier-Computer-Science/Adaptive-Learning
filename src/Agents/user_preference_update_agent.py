from autogen import ConversableAgent

class UserPreferenceUpdateAgent(ConversableAgent):
    def __init__(self, name="UserPreferenceUpdateAgent", llm_config=None):
        super().__init__(name=name, llm_config=llm_config)

    async def a_run(self, message):
        # Logic for dynamically updating interests
        response = f"Student interests updated. Recommendations will be refreshed accordingly based on: {message}"
        return response

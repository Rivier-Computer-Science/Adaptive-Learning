from autogen import ConversableAgent

class DataSynchronizationAgent(ConversableAgent):
    def __init__(self, name="StateDefinitionAgent", llm_config=None):
        super().__init__(name=name, llm_config=llm_config)

    async def a_generate_response(self, messages, sender, config):
        return (
            "Career progression states defined successfully:\n"
            "1. Beginner\n2. Intermediate\n3. Advanced\n4. Expert\n"
            "Transitions enabled between levels based on skill milestones."
        )
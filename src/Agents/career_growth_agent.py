from .conversable_agent import MyConversableAgent

class CareerGrowthAgent(MyConversableAgent):
    """
    CareerGrowthAgent generates step-by-step career progression plans 
    based on a student's learning progress and industry standards.
    """

    system_message = """
    You are CareerGrowthAgent, an expert in guiding students through career progression.
    Based on their learning progress and industry standards, provide a structured 
    step-by-step career growth plan.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="CareerGrowthAgent",
            system_message=kwargs.pop("system_message", self.system_message),
            description="An AI agent that provides structured career growth plans.",
            human_input_mode="NEVER",
            **kwargs
        )

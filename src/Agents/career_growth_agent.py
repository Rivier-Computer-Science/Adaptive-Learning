
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

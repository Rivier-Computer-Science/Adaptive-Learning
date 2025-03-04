from .conversable_agent import MyConversableAgent

class CertificationRecommendationAgent(MyConversableAgent):
    """
    CertificationRecommendationAgent suggests relevant certifications 
    for career paths based on industry standards.
    """

    system_message = """
    You are CertificationRecommendationAgent, an expert in recommending 
    professional certifications aligned with industry standards. 
    Based on the student's career goals and progress, suggest the 
    most relevant certifications.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="CertificationRecommendationAgent",
            system_message=kwargs.pop("system_message", self.system_message),
            description="An AI agent that provides certification recommendations.",
            human_input_mode="NEVER",
            **kwargs
        )

##################### Job Finder #########################
from .conversable_agent import MyConversableAgent

class JobFinderAgent(MyConversableAgent):
    """
    JobFinderAgent interacts with ChatGPT to recommend job roles based on the StudentAgent's skills and capabilities.
    It dynamically queries an AI model to generate personalized job recommendations.
    """

    description = """
        JobFinderAgent is an AI-powered agent that finds job opportunities 
        based on the LearnerModelAgent's assessment of the StudentAgent.
        It queries ChatGPT to provide real-time, industry-aligned job suggestions.
    """

    system_message = """
        You are JobFinderAgent, an AI-powered assistant specializing in job recommendations.
        Based on the StudentAgent's capabilities and certifications, generate a prioritized list
        of job opportunities that align with industry requirements.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="JobFinderAgent",
            system_message=kwargs.pop("system_message", self.system_message),
            description=kwargs.pop("description", self.description),
            human_input_mode="NEVER",
            **kwargs
        )

    async def get_job_recommendations(self, student_capabilities):
        """
        Queries ChatGPT to get job recommendations based on student capabilities.
        """
        query = f"Suggest job roles for a student skilled in {student_capabilities}."
        
        await self.a_send(query, recipient=self, request_reply=True)
        response = self.last_message(agent=self)["content"]

        return response

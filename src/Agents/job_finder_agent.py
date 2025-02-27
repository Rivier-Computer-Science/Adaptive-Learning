##################### Job Finder #########################
from .conversable_agent import MyConversableAgent

class JobFinderAgent(MyConversableAgent):
    description = """
            JobFinderAgent is an expert in finding appropriate job descriptions based on the LearnerModelAgent's assessment of the Student's capabilities.
            JobFinderAgent provides a priotized list of the jobs most likely to use the StudentAgent's capabilities.            
            """
    
    system_message = """
            You are JobFinderAgent, an expert in finding appropriate job descriptions based on the LearnerModelAgent's assessment of the Student's capabilities.
            You provides a priotized list of the jobs most likely to use the StudentAgent's capabilities.  
            """
    def __init__(self, **kwargs):
        super().__init__(
            name="JobFinderAgent",
            system_message=kwargs.pop('system_message', self.system_message),
            description=kwargs.pop('description',self.description),
            human_input_mode="NEVER",
            **kwargs
         )
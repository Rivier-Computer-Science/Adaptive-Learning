###################### Student ########################
from .conversable_agent import MyConversableAgent

class StudentAgent(MyConversableAgent):  
    description = """ 
            StudentAgent is a reliable system proxy designed to facilitate communication and interaction between a human user and the educational system. 
            StudentAgent serves as an intermediary, efficiently relaying requests and responses to ensure smooth and effective academic support. 
            """
    
    system_message = """
            You are StudentAgent, a system proxy for a human user. 
            Your primary role is to facilitate communication between the human and the educational system. 
            When the human provides input or requests information, you will relay these to the appropriate agent. 
            Maintain clarity and accuracy in all communications to enhance the human's learning experience
            """
    def __init__(self, **kwargs):
        description = kwargs.pop('description', self.description)
        system_message = kwargs.pop('system_message', self.system_message)
        human_input_mode = kwargs.pop('human_input_mode', "ALWAYS")        
        super().__init__(
            name="StudentAgent",
            human_input_mode=human_input_mode,
            system_message=system_message,
            description=description,
            **kwargs
        )
            
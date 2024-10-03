##################### Knowledge Tracer #########################
from typing import Dict
from .conversable_agent import MyConversableAgent

class MasteryAgent(MyConversableAgent):
    description =   """
            MasteryAgent is a comprehensive and adaptive agent that tracks the students mastery of a subject.
                 """
    system_message = """
            You are MasteryAgent, a comprehensive and adaptive agent that tracks the students mastery of a subject. """
    def __init__(self, **kwargs):
        super().__init__(
                name="MasteryAgent",
                human_input_mode="NEVER",
                system_message=self.system_message,
                description=self.description,
                **kwargs
            )
    


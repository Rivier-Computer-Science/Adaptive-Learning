##################### Knowledge Tracer #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class KnowledgeTracerAgent(MyConversableAgent):
    description_agent = """Knowledge Tracer is an agent tasked with testing the student's knowledge,
                           presenting problems with the Problem Generator,
                           and maintaining the Learner Model to track the student's level.
                        """
    system_message_agent = """Knowledge Tracer's function is to test the student's knowledge,
                             present problems through the Problem Generator,
                             and maintain the Learner Model to track the student's level.
                          """
    
    def __init__(self):
        super().__init__(
            name="KnowledgeTracer",
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.system_message_agent,
            description=self.description_agent
        )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None

 


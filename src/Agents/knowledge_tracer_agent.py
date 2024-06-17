##################### Knowledge Tracer #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class KnowledgeTracerAgent(MyConversableAgent):
    description_i = """I am a Knowledge Tracer.
                       My role is to test the student on what they know,
                       present problems through the Problem Generator,
                       and maintain the Learner Model to track the student's level.
                    """
    system_message_i = """As a Knowledge Tracer, my role is to test your knowledge,
                         present problems through the Problem Generator,
                         and maintain the Learner Model to track your level.
                      """
    
    def __init__(self):
        super().__init__(
            name="KnowledgeTracer",
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.system_message_i,
            description=self.description_i
        )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None

 





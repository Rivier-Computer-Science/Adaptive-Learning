##################### Knowledge Tracer #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class KnowledgeTracerAgent(MyConversableAgent):
    description_you = """You are a Knowledge Tracer.
                         You test the student on what they know.
                         You work with the Problem Generator to present problems to the Student.
                         You work with the Learner Model to keep track of the Student's level.
                      """
    system_message_you = """As a Knowledge Tracer, I will help you test your knowledge,
                            present problems through the Problem Generator,
                            and track your progress with the Learner Model.
                         """
    
    def __init__(self):
        super().__init__(
            name="KnowledgeTracer",
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.system_message_you,
            description=self.description_you
        )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None




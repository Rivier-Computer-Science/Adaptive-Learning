##################### Knowledge Tracer #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class KnowledgeTracerAgent(MyConversableAgent):
    description =   """You work with the Learner Model to keep track of the Student's level."""
    def __init__(self):
        super().__init__(
                name="KnowledgeTracer",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None
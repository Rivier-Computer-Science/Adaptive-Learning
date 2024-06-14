##################### Knowledge Tracer #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class KnowledgeTracerAgent(MyConversableAgent):
    description = """You are a Knowledge Tracer.
                     You test the student on what they know.
                     You work with the Problem Generator to present problems to the Student.
                     You work with the Learner Model to keep track of the Student's level."""

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

    def respond(self, user_input):
        if "trace my algebra knowledge" in user_input.lower():
            return "As a Knowledge Tracer, I will trace your algebra knowledge."
        elif "trace my knowledge in factoring" in user_input.lower():
            return "As a Knowledge Tracer, I will trace your knowledge in factoring."
        elif "what is your role" in user_input.lower():
            return "As a Knowledge Tracer, my role is to test the student on what they know, work with the Problem Generator to present problems to the Student, and work with the Learner Model to keep track of the Student's level."
        elif "identify which algebra topics i am struggling with" in user_input.lower():
            return "As a Knowledge Tracer, I will identify which algebra topics you are struggling with."
        else:
            return "I don't understand your request."

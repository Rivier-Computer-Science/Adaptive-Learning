from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt4_config

class HistoryProblemGeneratorAgent(MyConversableAgent):
    def __init__(self, history_subject="Indian History", **kwargs):
        self.history_subject = history_subject

        description = f"""
            HistoryProblemGeneratorAgent is a versatile and responsive agent designed to create a
            wide range of questions to test a StudentAgent's knowledge and skills in {history_subject}.

            You only generate questions one at a time.

            You never ask for input.
        """

        system_message = f"""
            You are a HistoryProblemGeneratorAgent, a versatile and responsive agent designed to create a
            wide range of questions to test a StudentAgent's knowledge and skills in {history_subject}.

            You only generate questions one at a time.

            You never ask for input.
        """
        
        super().__init__(            
            name="HistoryProblemGeneratorAgent",
            human_input_mode="NEVER",
            llm_config=kwargs.pop('llm_config', gpt4_config),
            system_message=kwargs.pop('system_message', system_message),
            description=kwargs.pop('description', description),
            **kwargs
        )    

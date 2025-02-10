##################### Problem Generator #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt4_config

class IndianHistoryProblemGeneratorAgent(MyConversableAgent):
    description = """
            IndianHistoryProblemGeneratorAgent is a versatile and responsive agent designed to create a
                 wide range of questions to test a StudentAgent's knowledge and skills of Indian History.
             """
    
    system_message = """
            You are  IndianHistoryProblemGeneratorAgent is a versatile and responsive agent designed to create a
                 wide range of questions to test a StudentAgent's knowledge and skills of Indian History.
            """
    
    def __init__(self, **kwargs):        
        super().__init__(            
                name="IndianHistoryProblemGeneratorAgent",
                human_input_mode="NEVER",
                llm_config=kwargs.pop('llm_config', gpt4_config),
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description', self.description),
                **kwargs
            )    
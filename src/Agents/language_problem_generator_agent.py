from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt4_config

class ProblemGeneratorAgent(MyConversableAgent):
    description = """
            ProblemGeneratorAgent is a versatile and responsive agent designed to create a wide range of questions to test a StudentAgent's knowledge and skills of a specified language.
            ProblemGeneratorAgent provides a mix of translation questions both to and from English and the target language.
            ProblemGeneratorAgent generates one question at a time.
            ProblemGeneratorAgent asks the StudentAgent to solve the generated problem.
            ProblemGeneratorAgent collaborates closely with LevelAdapterAgent to dynamically adjust the complexity of the questions based on StudentAgent's performance.
            """
    
    system_message = """
            You are ProblemGeneratorAgent, an agent responsible for providing problems to test the StudentAgent's knowledge and skills of {language}. 
            ProblemGeneratorAgent never provides instruction, motivation, or any other response. 
            ProblemGeneratorAgent generates one question at a time.
            ProblemGeneratorAgent provides a mix of translation questions both to and from English and {language}.
            ProblemGeneratorAgent asks the StudentAgent to solve the generated problem.
            ProblemGeneratorAgent works closely with LevelAdapterAgent, which will monitor the StudentAgent's performance and instruct you when to adjust the difficulty of the questions.             
            """
    
    def __init__(self, language="Telugu", **kwargs):        
        self.language = language
        # Format the system message with the specified language
        formatted_system_message = self.system_message.format(language=self.language)
        super().__init__(            
                name="ProblemGeneratorAgent",
                human_input_mode="NEVER",
                llm_config=kwargs.pop('llm_config', gpt4_config),
                system_message=kwargs.pop('system_message', formatted_system_message),
                description=kwargs.pop('description', self.description),
                **kwargs
            )    
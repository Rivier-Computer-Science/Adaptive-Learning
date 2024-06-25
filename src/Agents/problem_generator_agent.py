##################### Problem Generator #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt4_config

class ProblemGeneratorAgent(MyConversableAgent):
    description = """
            ProblemGeneratorAgent is a versatile and responsive agent designed to create a wide range of problems to test a StudentAgent's knowledge and skills. 
            With the ability to generate questions across various subjects and difficulty levels, ProblemGeneratorAgent ensures that the StudentAgent receives 
                appropriately challenging problems to enhance their learning. 
            ProblemGeneratorAgent never provides instruction. Only TeacherAgent does.
            ProblemGeneratorAgent collaborates closely with LevelAdapterAgent to dynamically adjust the complexity of the questions based on StudentAgent's performance.
            """
    
    system_message = """
            You are ProblemGeneratorAgent, an agent responsible for providing problems to test the StudentAgent's knowledge and skills. 
            Create a diverse set of questions across different subjects and difficulty levels, ensuring that each problem is clear, 
                well-structured, and appropriately challenging. 
            Work closely with LevelAdapterAgent, which will monitor the StudentAgent's performance and instruct you when to adjust the difficulty of the questions. 
            ProblemGeneratorAgent never provides instruction. Only TeacherAgent does.
            Your goal is to provide a balanced mix of problems that help the StudentAgent learn and improve effectively, adapting to their skill level as needed.
            """
    def __init__(self, **kwargs):
        #kwargs['llm_config'] = gpt4_config  #override default
        super().__init__(            
                name="ProblemGeneratorAgent",
                human_input_mode="NEVER",
                system_message=self.system_message,
                description=self.description,
                **kwargs
            )    
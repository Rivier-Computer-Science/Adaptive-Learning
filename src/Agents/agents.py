import autogen
import os
import asyncio
import src.globals as globals
from UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {
        'model': "gpt-3.5-turbo",
    }
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}




####################################################################
#
# Base Agent (common methods)
#
##################################################################### 

class MyBaseAgent: 
    def find_agent_by_type(self, agent_type):
        for agent in self.groupchat.agents:
            if isinstance(agent, agent_type):
                return agent
        return None  # Return None if agent not found


####################################################################
#
# Conversable Agents
#
##################################################################### 

class MyConversableAgent(autogen.ConversableAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.response_event = asyncio.Event()  # Add an event object
        self.description = self.system_message

 
    def set_chat_interface(self, chat_interface):
        self.chat_interface = chat_interface


class LearnerAgent(MyConversableAgent):
    description = """You are a student learning math. You will ask questions, solve problems, and receive feedback from the Tutor."""
    def __init__(self):
        super().__init__(
            name="Learner",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message=self.description,
            description=self.description,
            code_execution_config=False,
            human_input_mode="ALWAYS",
            llm_config=gpt4_config
        )
    
    async def a_get_human_input(self, prompt: str) -> str:
            self.chat_interface.send(prompt, user="Tutor", respond=False) 

            if globals.input_future is None or globals.input_future.done():
                globals.input_future = asyncio.Future()

            await globals.input_future

            input_value = globals.input_future.result()
            globals.input_future = None
            return input_value




                

####################################################################
#
# Assisstant Agents
#
#####################################################################        

class MyAssisstantAgent(autogen.AssistantAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)    
        
     

class TutorAgent(MyAssisstantAgent):
    descriptioin = """You are a patient and helpful math tutor. 
                        Adapt your explanations and problem difficulty to the Learner's progress. 
                        Guide the Learner, provide hints, and assess their understanding. 
                        When necessary, you can ask the Problem Generator to create practice problems, 
                        the Solution Verifier to check the Learner's answers, 
                        or the Visualizer to generate visualizations of equations and concepts. 
                        Encourage the Learner with positive feedback from the Motivator."""
    def __init__(self):
        super().__init__(
                name="Tutor",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.descriptioin,
                description=self.descriptioin
            )
   
class ProblemGeneratorAgent(MyAssisstantAgent):
    descriptioin = """You generate math problems at the appropriate level for the Learner, 
                        based on the Tutor's request and the Learner's current skill level."""
    def __init__(self):
        super().__init__(
                name="Problem Generator",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.descriptioin,
                description=self.descriptioin
            )

class SolutionVerifierAgent(MyAssisstantAgent):
    descriptioin = """You check the Learner's solutions to math problems and provide feedback 
                        to the Tutor on whether the solution is correct and, if not, why."""
    def __init__(self):
        super().__init__(
                name="Solution Verifier",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.descriptioin,
                description=self.descriptioin
            )

class MotifatorAgent(MyAssisstantAgent):
    descriptioin = """You provide positive and encouraging feedback to the Learner to keep them motivated. 
                        Offer specific praise and acknowledge their effort and progress."""
    def __init__(self):
        super().__init__(
                name="Motivator",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.descriptioin,
                description=self.descriptioin
            )

class VisualizerAgent(MyAssisstantAgent):
    descriptioin = """You are skilled at creating generating Python code for visualizations of mathematical equations and concepts. 
                        You can generate code (e.g., Python with libraries like Matplotlib or Plotly) 
                        to produce graphs, plots, or interactive visualizations based on requests from the Tutor. 
                        You ask the Code Executor to execute the code. 
                        Do not ask for user input in the code"""
    def __init__(self):
        super().__init__(
                name="Visualizer",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.descriptioin,
                description=self.descriptioin
            )


####################################################################
#
# UserProxy Agents
#
#####################################################################        
       
class CodeExecutorAgent(autogen.UserProxyAgent):
    description = "Execute code and display the result."
    def __init__(self):
        super().__init__(
            name="CodeExecutor",
            code_execution_config={"last_n_messages": 2, "work_dir": "coding"}, 
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message=self.description,
            description=self.description
            )

import autogen
import os
import asyncio
from typing import Any, Dict, Optional
import re
import src.globals

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
# Conversable Agents
##################################################################### 

class MyConversableAgent(autogen.ConversableAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.response_event = asyncio.Event()  # Add an event object
        self.description = self.system_message
        self.chat_interface = None
 
    async def a_get_human_input(self, prompt: str) -> str:
                self.chat_interface.send(prompt, user="System", respond=False) 

                if globals.input_future is None or globals.input_future.done():
                    globals.input_future = asyncio.Future()

                await globals.input_future

                input_value = globals.input_future.result()
                globals.input_future = None
                return input_value

    @property
    def chat_interface(self):
        return self._chat_interface
    
    @chat_interface.setter
    def chat_interface(self, chat_interface):
        self._chat_interface = chat_interface

###################### Student ########################
class StudentAgent(MyConversableAgent):  
    description = """ You are a user proxy for a student who wants to learn mathematics.
                      You display messages received from other Agents that need human input.                      
                    """
    def __init__(self):
        super().__init__(
            name="Student",
            human_input_mode="ALWAYS",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            llm_config=gpt4_config,
            system_message=self.description,
            description=self.description
        )
            

####################################################################
# Assisstant Agents
#####################################################################        

class MyAssisstantAgent(autogen.AssistantAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)    
        
##################### Knowledge Tracer #########################
class KnowledgeTracerAgent(MyConversableAgent):
    description =   """You are a Knowledge Tracer.
                         You test the student on what they know.
                         You work with the Problem Generator to present problems to the Student.
                         You work with the Learner Model to keep track of the Student's level.
                    """
    def __init__(self):
        super().__init__(
                name="Teacher",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.description,
                description=self.description
            )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None


##################### Teacher #########################
class TeacherAgent(MyConversableAgent):
    description =   """You are a Teacher.
                         When asked by the Student to learn new material, you present lecture-type material.
                    """
    def __init__(self):
        super().__init__(
                name="Teacher",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.description,
                description=self.description
            )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None

##################### Tutor #########################
class TutorAgent(MyConversableAgent):
    description = """You are a patient and helpful math tutor. 
                        When the Student asks for help,              
                        You explain answers to questions.
                        You work with the Problem Generator to create new questions that the Student can master.
                        You check the Student's answer with the SolutionVerifier.
                        You guide the Learner and provide hints.  
                        You encourage the Learner with positive feedback from the Motivator."""
    def __init__(self):
        super().__init__(
                name="Tutor",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.description,
                description=self.description
            )
        self.last_plot_request = None  # Add an attribute to track plot requests
        self.groupchat = None


##################### Problem Generator #########################
class ProblemGeneratorAgent(MyConversableAgent):
    description = """You generate math problems at the appropriate level for the Student. 
                        You ask the Level Adapter for the level of difficulty and generate a question.
                """
    def __init__(self):
        super().__init__(
                name="ProblemGenerator",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.description,
                description=self.description
            )    


##################### Solution Verifier #########################
class SolutionVerifierAgent(MyConversableAgent):
    description = """You check the Students's solutions to math problems and provide feedback 
                        to the Tutor on whether the solution is correct and, if not, why.
                     You ask the Programmer to generate code to visualize the solution.
                    """
    def __init__(self):
        super().__init__(
                name="SolutionVerifier",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.description,
                description=self.description
            )

##################### Programmer #########################
class ProgrammerAgent(MyConversableAgent):
    description = """You write python/shell code to solve math problem. Wrap the code in a code block that specifies the script type. 
                    The user can't modify your code. So do not suggest incomplete code which requires others to modify. 
                    Don't use a code block if it's not intended to be executed by the Code Runner.
                    Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. 
                    Check the execution result returned by the Code Runner.
                    If the result indicates there is an error, fix the error and output the code again. 
                    Suggest the full code instead of partial code or code changes. 
                    If the error can't be fixed or if the task is not solved even after the code is executed successfully, 
                    analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
                """
    def __init__(self):
        super().__init__(
                name="Programmer",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.description,
                description=self.description
            )

##################### Code Runner #########################
class CodeRunnerAgent(MyConversableAgent):  
    description = "Execute code and display the result."
    def __init__(self):
        super().__init__(
            name="CodeRunner",
            code_execution_config={"last_n_messages": 2, "work_dir": "coding"},
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message=self.description,
            description=self.description
        )

##################### Learner Model #########################
class LearnerModelAgent(MyConversableAgent):
    description = """You are a model of the Student's learning level. 
                     You will keep track of the student's answers and help other agents generate results"""
    def __init__(self):
        super().__init__(
            name="LearnerModel",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message=self.description,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            llm_config=gpt4_config
        )


##################### Level Adapter #########################
class LevelAdapterAgent(MyConversableAgent):
    description = """You ask the Learner Model what the current level of the Student is.  
                     You provide input to the Problem Generator on the Student's level
                  """
    def __init__(self):
        super().__init__(
            name="LevelAdapter",
            system_message=self.description,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            llm_config=gpt4_config
        )

##################### Level Adapter #########################
class MotivatorAgent(MyConversableAgent):
    description = """ You provide positive and encouraging feedback to the Student to keep them motivated. 
                        Offer specific praise and acknowledge their effort and progress."""
    def __init__(self):
        super().__init__(
                name="Motivator",
                human_input_mode="NEVER",
                llm_config=gpt4_config,
                system_message=self.description,
                description=self.description
            )



 

       




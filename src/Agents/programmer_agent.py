##################### Programmer #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class ProgrammerAgent(MyConversableAgent):
    description = """You write python/shell code to solve math problem. Wrap the code in a code block that specifies the script type. 
                    The user can't modify your code. So do not suggest incomplete code which requires others to modify. 
                    Don't use a code block if it's not intended to be executed by the Code Runner.
                    Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. 
                    As the Code Runner to run the code. 
                    Check the execution result. 
                    If the result indicates there is an error, fix the error and output the code again. 
                    Suggest the full code instead of partial code or code changes. 
                    If the error can't be fixed or if the task is not solved even after the code is executed successfully, 
                    analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
                """
    def __init__(self):
        super().__init__(
                name="Programmer",
                human_input_mode="NEVER",
                llm_config=gpt3_config,
                system_message=self.description,
                description=self.description
            )

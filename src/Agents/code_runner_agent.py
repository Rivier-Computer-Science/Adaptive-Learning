##################### Code Runner #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class CodeRunnerAgent(MyConversableAgent):  
    description = "You serve as an integral part of the multi-agent system, executing code snippets from users and other agents. You provide immediate results, assisting in debugging and educational tasks. You help ensure that all code meets functional requirements by displaying comprehensive execution outputs."
    def __init__(self):
        super().__init__(
            name="CodeRunner",
            code_execution_config={"last_n_messages": 2, "work_dir": "coding"},
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.description,
            description=self.description
        )
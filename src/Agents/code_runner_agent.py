##################### Code Runner #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class CodeRunnerAgent(MyConversableAgent):  
    description = "You are a dedicated code execution assistant, working alongside other agents by running and verifying code snippets. You display outputs to help users and agents validate and understand code functionality."
    def __init__(self):
        super().__init__(
            name="CodeRunner",
            code_execution_config={"last_n_messages": 2, "work_dir": "coding"},
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.description,
            description=self.description
        )
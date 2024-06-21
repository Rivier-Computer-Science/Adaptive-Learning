##################### Code Runner #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class CodeRunnerAgent(MyConversableAgent):  
    description = "As a vital component of a collaborative agent framework, I specialize in executing and displaying code outputs. I interact seamlessly with educational and development agents, enhancing learning and programming experiences. By providing real-time feedback on code execution, I support users and other agents in refining and understanding complex code segments, contributing to a more robust and interactive learning environment."
    message = """Code Runner's function is to execute and display code outputs, providing real-time feedback. Code Runner interacts seamlessly with educational and development agents, enhancing learning and programming experiences. By refining and understanding complex code segments, Code Runner supports users and other agents, contributing to a more robust and interactive learning environment. """
    def __init__(self):
        super().__init__(
            name="CodeRunner",
            code_execution_config={"last_n_messages": 2, "work_dir": "coding"},
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.message,
            description=self.description
        )
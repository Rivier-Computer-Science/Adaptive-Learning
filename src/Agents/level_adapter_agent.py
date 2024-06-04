##################### Level Adapter #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LevelAdapterAgent(MyConversableAgent):
    description = """You ask the Learner Model what the current level of the Student is.  
                     You provide input to the Problem Generator on the Student's level.
                  """
    def __init__(self):
        super().__init__(
            name="LevelAdapter",
            system_message=self.description,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            llm_config=gpt3_config
        )
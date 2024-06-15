##################### Code Runner #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class CodeRunnerAgent(MyConversableAgent):  
    description = "Execute code and display the result."

    def __init__(self, name="CodeRunner", code_execution_config=None, llm_config=None):
        if code_execution_config is None:
            code_execution_config = {"last_n_messages": 2, "work_dir": "coding"}
        if llm_config is None:
            llm_config = gpt3_config
        
        super().__init__(
            name=name,
            code_execution_config=code_execution_config,
            human_input_mode="NEVER",
            llm_config=llm_config,
            system_message=self.description,
            description=self.description
        )

    def execute_code(self, code):
        """
        Executes the provided code and returns the result.

        Args:
            code (str): The code to be executed.

        Returns:
            str: The result of the code execution.
        """
        # Placeholder for actual code execution logic
        # Example: result = exec(code, globals())
        result = f"Executing: {code}"
        return result

    def display_result(self, result):
        """
        Displays the result of the code execution.

        Args:
            result (str): The result to display.

        Returns:
            None
        """
        print(f"Result: {result}")

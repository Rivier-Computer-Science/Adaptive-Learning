###################### Student ########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class StudentAgent(MyConversableAgent):
    description = """ 
                      You are a user proxy for a student who wants to learn mathematics.
                      You display messages received from other Agents that need human input.
                      You can request learning resources, ask for explanations, or seek help with problems.
                    """
    
    def __init__(self):
        super().__init__(
            name="Student",
            human_input_mode="ALWAYS",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            llm_config=gpt3_config,
            system_message=self.description,
            description=self.description
        )
    
    def request_learning_resources(self, topic):
        """
        Request learning resources on a specific topic.

        Args:
            topic (str): The topic for which learning resources are requested.

        Returns:
            str: Message confirming the request for learning resources.
        """
        return f"Requesting learning resources on {topic}"

    def ask_for_explanation(self, problem):
        """
        Ask for an explanation of a specific problem.

        Args:
            problem (str): The problem for which an explanation is requested.

        Returns:
            str: Message confirming the request for explanation.
        """
        return f"Asking for an explanation of: {problem}"

    def seek_help_with_problem(self, problem):
        """
        Seek help with solving a specific problem.

        Args:
            problem (str): The problem for which help is needed.

        Returns:
            str: Message confirming the request for help with the problem.
        """
        return f"Seeking help with problem: {problem}"

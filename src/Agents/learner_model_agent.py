##################### Learner Model #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LearnerModelAgent(MyConversableAgent):
    description = """You simulate the Student's learning level, tracking their progress and assisting other agents in generating results."""
    
    def __init__(self):
        super().__init__(
            name="LearnerModel",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message=self.description,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            llm_config=gpt3_config
        )

    def track_student_progress(self, student_answer):
        """
        Track the student's progress based on their answers.

        Args:
            student_answer (str): The answer provided by the student.

        Returns:
            str: Confirmation message for tracking the student's progress.
        """
        # Placeholder for tracking student's progress
        # Example: self.progress_tracker.update_progress(student_answer)
        return f"Tracking student's progress based on answer: {student_answer}"

    def assist_agents(self):
        """
        Assist other agents in generating results based on the student's learning level.

        Returns:
            str: Message confirming assistance to other agents.
        """
        # Placeholder for assisting other agents
        # Example: self.result_generator.generate_results()
        return "Assisting other agents in generating results"

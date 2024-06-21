##################### Level Adapter #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class LevelAdapterAgent(MyConversableAgent):
    description = """ 
                    You interact with the Learner Model to fetch information about the Student's learning progress.
                    You provide input to other agents or systems based on the Student's level.
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

    def get_student_level(self):
        """
        Retrieve the current level of the student from the Learner Model.

        Returns:
            str: The current level of the student.
        """
        # Placeholder for retrieving student's level from Learner Model
        # Example: student_level = self.learner_model.get_student_level()
        student_level = "Intermediate"  # Placeholder value
        return student_level

    def provide_input_to_problem_generator(self, problem_type):
        """
        Provide input to the Problem Generator based on the student's level and problem type.

        Args:
            problem_type (str): The type of problem for which input is provided.

        Returns:
            str: Confirmation message for providing input to Problem Generator.
        """
        # Placeholder for providing input to Problem Generator
        # Example: self.problem_generator.set_student_level_and_problem_type(student_level, problem_type)
        return f"Providing input to Problem Generator for problem type: {problem_type}"

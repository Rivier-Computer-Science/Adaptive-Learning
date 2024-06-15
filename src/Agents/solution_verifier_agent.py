##################### Solution Verifier #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class SolutionVerifierAgent(MyConversableAgent):
    description = """
        After the Student answers, you check the Student's solutions to math problems. 
        You interact with the Tutor, not the Student. 
        After the Student answers, you ask the Programmer to generate code to check and visualize the solution.
    """
    
    def __init__(self):
        super().__init__(
            name="SolutionVerifier",
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.description,
            description=self.description
        )

    def verify_solution(self, student_answer):
        """
        Verifies the student's solution. This is a stub method that should be implemented 
        to include logic for checking the solution.
        
        Args:
            student_answer (str): The student's answer to verify.
        
        Returns:
            bool: True if the solution is correct, False otherwise.
        """
        # Placeholder for actual verification logic
        # Example: result = self.check_solution_with_logic(student_answer)
        result = True  # Assuming the solution is correct for this stub
        return result

    def request_programmer_code(self, student_answer):
        """
        Interacts with the programmer to generate code for solution verification and visualization.
        
        Args:
            student_answer (str): The student's answer to generate code for.
        
        Returns:
            str: The generated code as a string.
        """
        # Placeholder for actual code generation logic
        generated_code = f"print('Checking solution for: {student_answer}')"
        return generated_code
    
    def check_solution_with_logic(self, student_answer):
        """
        An example method to represent the logic to check the student's solution.
        
        Args:
            student_answer (str): The student's answer.
        
        Returns:
            bool: True if the answer is correct, False otherwise.
        """
        # Example logic to check the answer
        # This is where you would include the actual verification logic
        return student_answer == "expected_answer"

    def visualize_solution(self, student_answer):
        """
        An example method to visualize the student's solution.
        
        Args:
            student_answer (str): The student's answer.
        
        Returns:
            None
        """
        # Example visualization logic
        print(f"Visualizing solution for: {student_answer}")


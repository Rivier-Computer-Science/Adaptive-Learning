##################### Knowledge Tracer #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt3_config

class KnowledgeTracerAgent(MyConversableAgent):
    description =   """You are a Knowledge Tracer.
                         You test the student on what they know.
                         You work with the Problem Generator to present problems to the Student.
                         You work with the Learner Model to keep track of the Student's level.
                    """
    def __init__(self):
        super().__init__(
            name="KnowledgeTracer",
            human_input_mode="NEVER",
            llm_config=gpt3_config,
            system_message=self.description,
            description=self.description
        )
        self.last_plot_request = None  
        self.groupchat = None
        
    def evaluate_answer(self, problem, answer):
        """
        Evaluate the student's answer to a given problem.
        
        Args:
        - problem (str): The math problem presented to the student.
        - answer (str): The student's answer to the problem.
        """
        
        equation = problem.split(":")[1].strip()
        # Extract the coefficients and constant from the equation
        left_side, right_side = equation.split("=")
        left_coefficient, left_constant = map(int, left_side.split("x + "))
        right_constant = int(right_side)
        # Solve the equation
        correct_answer = (right_constant - left_constant) / left_coefficient
        
        # Compare the student's answer with the correct answer
        if float(answer) == correct_answer:
            # If the answer is correct
            return f"Great job! Your answer is correct. Let's move on to the next problem."
        else:
            # If the answer is incorrect, provide feedback and show the correct solution
            feedback = f"The answer provided is incorrect. Let's work through the problem together:\n\n"
            feedback += f"Given equation: {equation}\n\n"
            feedback += f"Subtract {left_constant} from both sides:\n"
            feedback += f"{left_side} = {right_side} - {left_constant}\n"
            feedback += f"{left_side} = {right_constant - left_constant}\n\n"
            feedback += f"Divide by {left_coefficient} on both sides:\n"
            feedback += f"{left_side} / {left_coefficient} = {(right_constant - left_constant)} / {left_coefficient}\n"
            feedback += f"x = {(right_constant - left_constant) / left_coefficient}\n\n"
            feedback += f"Therefore, the correct answer is x = {correct_answer}. Great effort! Let's move on to the next problem."
            return feedback

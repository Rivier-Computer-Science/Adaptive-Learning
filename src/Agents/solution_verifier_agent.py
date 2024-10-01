##################### Solution Verifier #########################
from .conversable_agent import MyConversableAgent

class SolutionVerifierAgent(MyConversableAgent):
    description = """
            SolutionVerifierAgent is a diligent and precise agent designed to check a StudentAgent's answers to questions. 
            With a strong focus on accuracy, SolutionVerifierAgent compares the StudentAgent's answers. 
            This ensures that the StudentAgent's responses are correct and reliable, providing valuable feedback for their learning process.
            """
    
    system_message = """
            You are SolutionVerifierAgent, an agent responsible for checking a StudentAgent's answers to questions. 
            You verify the accuracy of each answer by comparing it to the correct solution. 
            """
    def __init__(self, **kwargs):
        super().__init__(
            name="SolutionVerifierAgent",
            human_input_mode="NEVER",
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )

    def verify_solution(self, question, student_answer, correct_answer):
        """Verify the student's answer against the correct answer."""
        prompt = f"""Question: {question}
                     Student's answer: {student_answer}
                     Correct answer: {correct_answer}
                     Is the student's answer correct? Provide a detailed explanation."""
        return self.generate_response(prompt)

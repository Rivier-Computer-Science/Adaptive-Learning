 from typing import Dict
from .conversable_agent import MyConversableAgent

class HintAgent(MyConversableAgent):
    description = """
            HintAgent is a key component in the math tutoring platform. It provides step-by-step hints for math problems, 
            helping students gradually progress toward the solution. The hints range from general guidance to detailed explanations,
            and they adapt to the learner's needs based on their current skill level.
            The HintAgent’s primary responsibility is to offer personalized hints when students are struggling with math problems, 
            ensuring a more engaging and supportive learning experience.
            """

    system_message = """
            You are HintAgent, a key guide within the math tutoring system. Your goal is to provide hints for solving math problems, 
            assisting students by offering structured and progressive help.
            You work with the ProblemGeneratorAgent to provide a variety of math problems and interact with the KnowledgeTracerAgent 
            to adjust hints based on the student’s current progress and skill level.
            Your aim is to generate hints that are clear, concise, and adaptive to the student’s needs, increasing in detail as necessary.
            """

    def __init__(self, **kwargs):
        super().__init__(
                name="HintAgent",
                human_input_mode="NEVER",  
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description', self.description),
                **kwargs
            )

    def generate_hint(self, problem: str, difficulty_level: int) -> str:
        """
        Generate a hint for the given math problem based on the difficulty level.
        """
        hints = {
            1: "Think about isolating the variable by performing inverse operations.",
            2: "Try to simplify the equation by subtracting 3 from both sides.",
            3: "Now you have 2x = 4. What is the next step to solve for x?",
            4: "To solve for x, divide both sides of the equation by 2."
        }
        
        return hints.get(difficulty_level, "Keep trying, you’re doing great! Let’s take it step by step.")

    def generate_adaptive_hint(self, problem: str, student_performance: Dict[str, float]) -> str:
        """
        Adjust the hint based on the student’s performance in similar problems.
        """
        student_skill = student_performance.get("math_skill", 0)
        
        # Provide more detailed hints for struggling students
        if student_skill < 50:
            return "Let’s break it down: Start by subtracting 3 from both sides to get 2x = 4."
        
        if student_skill < 80:
            return "Try isolating the variable by performing inverse operations. What happens if you subtract 3 from both sides?"
        
        # Provide minimal hints for advanced students
        return "Think about how you can isolate the variable to solve the equation."

    def handle_hint_request(self, problem: str, student_performance: Dict[str, float]) -> str:
        """
        Handles hint requests, and generates adaptive hints based on the student’s skill level.
        """
        # Start with a general hint based on the problem
        difficulty_level = 1  # This could be dynamic based on the problem
        hint = self.generate_hint(problem, difficulty_level)

        # Adapt the hint based on student performance
        adaptive_hint = self.generate_adaptive_hint(problem, student_performance)
        
        # Combine both hints for a richer experience
        return f"Here’s your hint: {hint} {adaptive_hint}"

    def request_hint(self, problem: str, student_performance: Dict[str, float]) -> str:
        """
        Function for generating and returning a hint when the student requests help.
        """
        return self.handle_hint_request(problem, student_performance)


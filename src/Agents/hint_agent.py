from src.Agents.conversable_agent import MyConversableAgent

class HintAgent(MyConversableAgent):
    description = """
        HintAgent is responsible for generating hints to assist StudentAgent in problem-solving.
        It provides step-by-step hints that gradually reveal more information, ensuring that 
        students are guided towards the solution without directly giving them the answer.
    """            
    
    system_message = """
        You are HintAgent, an assistant that provides hints to guide StudentAgent in solving problems.
        Your hints should be adaptive, starting with general guidance and progressively becoming more detailed if needed.
        Avoid giving the full solution immediately. Instead, break it into logical hints based on problem-solving steps.
    """            
    
    def __init__(self, **kwargs):
        super().__init__(
            name="HintAgent",
            human_input_mode="NEVER",
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )

    def generate_hint(self, problem_state):
        """
        Dynamically generate hints based on problem-solving progress.
        Hints become more detailed as the problem_state value increases.
        """
        hints = [
            "Think about breaking the problem into smaller parts.",
            "Consider what concepts or formulas might be useful here.",
            "Have you checked for any given values or conditions in the problem?",
            "Try applying a known strategy, like substitution or simplification.",
            "You're very close! Look at your last step carefully."
        ]
        
        return hints[min(problem_state, len(hints) - 1)]

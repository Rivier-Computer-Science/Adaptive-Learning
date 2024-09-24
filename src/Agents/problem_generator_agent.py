##################### Problem Generator #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt4_config

class ProblemGeneratorAgent(MyConversableAgent):
    description = """
            ProblemGeneratorAgent is a versatile and responsive agent designed to create a wide range of problems to test a StudentAgent's knowledge and skills. 
            With the ability to generate questions across various subjects and difficulty levels, ProblemGeneratorAgent ensures that the StudentAgent receives 
                appropriately challenging problems to enhance their learning. 
            ProblemGeneratorAgent never provides instruction, motivation, or any other response. 
            ProblemGeneratorAgent generates one question at a time.
            ProblemGeneratorAgent asks the StudentAgent to solve the generated problem.
            ProblemGeneratorAgent collaborates closely with LevelAdapterAgent to dynamically adjust the complexity of the questions based on StudentAgent's performance.
            """
    
    system_message = """
            You are ProblemGeneratorAgent, an agent responsible for providing problems to test the StudentAgent's knowledge and skills. 
            ProblemGeneratorAgent never provides instruction, motivation, or any other response. 
            ProblemGeneratorAgent generates one question at a time.
            Create a diverse set of questions across different subjects and difficulty levels, ensuring that each problem is clear, 
                well-structured, and appropriately challenging. 
            ProblemGeneratorAgent asks the StudentAgent to solve the generated problem.
            Work closely with LevelAdapterAgent, which will monitor the StudentAgent's performance and instruct you when to adjust the difficulty of the questions. 
            Your goal is to provide a balanced mix of problems that help the StudentAgent learn and improve effectively, adapting to their skill level as needed.
            """
    def __init__(self, **kwargs):
        kwargs['llm_config'] = gpt4_config  # override default
        super().__init__(
            name="ProblemGeneratorAgent",
            human_input_mode="NEVER",
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )
        
        # Initialize the question bank and difficulty levels
        self.question_bank = {}
        self.difficulty_levels = ['easy', 'medium', 'hard']

    # New method to generate adaptive questions
    def generate_adaptive_question(self, subject, difficulty):
        """
        Generate an adaptive question based on the given subject and difficulty.
        """
        # Use the LLM to generate a question
        prompt = f"Generate a {difficulty} {subject} question for a student."
        response = self.generate_response(prompt)
        
        # Store the generated question in the question bank
        if subject not in self.question_bank:
            self.question_bank[subject] = {}
        if difficulty not in self.question_bank[subject]:
            self.question_bank[subject][difficulty] = []
        self.question_bank[subject][difficulty].append(response)
        
        return response

    # New method to get a question from the bank or generate a new one
    def get_or_generate_question(self, subject, difficulty):
        """
        Retrieve a question from the bank or generate a new one if needed.
        """
        if subject in self.question_bank and difficulty in self.question_bank[subject] and self.question_bank[subject][difficulty]:
            # Retrieve a random question from the bank
            return random.choice(self.question_bank[subject][difficulty])
        else:
            # Generate a new question
            return self.generate_adaptive_question(subject, difficulty)

    # New method to adjust difficulty based on student performance
    def adjust_difficulty(self, current_difficulty, performance):
        """
        Adjust the difficulty level based on student performance.
        """
        current_index = self.difficulty_levels.index(current_difficulty)
        if performance == 'good' and current_index < len(self.difficulty_levels) - 1:
            return self.difficulty_levels[current_index + 1]
        elif performance == 'poor' and current_index > 0:
            return self.difficulty_levels[current_index - 1]
        else:
            return current_difficulty

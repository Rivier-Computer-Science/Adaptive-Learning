##################### Learner Model #########################
from .conversable_agent import MyConversableAgent

class LearnerModelAgent(MyConversableAgent):
    description = """
            LearnerModelAgent is an insightful and adaptive agent designed to monitor and assess the current capabilities of the StudentAgent. 
            By listening to the StudentAgent's answers and updating its internal model, LearnerModelAgent provides a comprehensive understanding of the StudentAgent's 
                knowledge and skill level. 
            When consulted by other agents such as ProblemGeneratorAgent, LearnerModelAgent offers guidelines on the type and difficulty of math questions 
                that should be generated to match the StudentAgent's proficiency.                     
            """
    
    system_message = """
            You are LearnerModelAgent, an agent responsible for assessing and understanding the current capabilities of the StudentAgent. 
            Your primary task is to listen to the StudentAgent's answers and continuously update your internal model to reflect their knowledge and skill level. 
            When other agents, such as ProblemGeneratorAgent, request information, you provide detailed guidelines on the type and difficulty of math questions that 
                should be generated based on your assessment. 
            Your goal is to ensure that the StudentAgent's learning experience is tailored to their current abilities, promoting effective and personalized learning.
            """
    def __init__(self, **kwargs):
        super().__init__(
            name="LearnerModelAgent",            
            system_message=self.system_message,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            **kwargs
        )
        # Initialize the learner model
        self.learner_model = {}

    # New method to update the learner model based on student performance
    def update_model(self, subject, difficulty, performance):
        """
        Update the learner model based on the student's performance on a question.
        """
        if subject not in self.learner_model:
            self.learner_model[subject] = {}
        
        if difficulty not in self.learner_model[subject]:
            self.learner_model[subject][difficulty] = {'correct': 0, 'total': 0}
        
        self.learner_model[subject][difficulty]['total'] += 1
        if performance == 'correct':
            self.learner_model[subject][difficulty]['correct'] += 1

    # New method to get the recommended difficulty for a subject
    def get_recommended_difficulty(self, subject):
        """
        Determine the recommended difficulty level for a subject based on the learner model.
        """
        if subject not in self.learner_model:
            return 'easy'  # Default to easy if no data available
        
        subject_data = self.learner_model[subject]
        for difficulty in ['hard', 'medium', 'easy']:
            if difficulty in subject_data:
                performance = subject_data[difficulty]['correct'] / subject_data[difficulty]['total']
                if performance >= 0.7:  # If correct 70% of the time or more, recommend this difficulty
                    return difficulty
        
        return 'easy'  # Default to easy if no suitable difficulty found

    # New method to provide feedback on student performance
    def provide_feedback(self, subject, difficulty, answer):
        """
        Analyze the student's answer and provide feedback on their performance.
        """
        # Use the LLM to analyze the answer and generate feedback
        prompt = f"Analyze the following {subject} answer to a {difficulty} question and provide feedback: {answer}"
        feedback = self.generate_response(prompt)
        
        # Update the learner model based on the feedback
        performance = 'correct' if 'correct' in feedback.lower() else 'incorrect'
        self.update_model(subject, difficulty, performance)
        
        return feedback

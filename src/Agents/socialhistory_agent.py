from typing import Dict
from .conversable_agent import MyConversableAgent

class HistoryTutorAgent(MyConversableAgent):
    description = """
            HistoryTutorAgent is a central figure in the Social Studies learning platform, focused on Indian history. 
            It interacts with the StudentAgent to provide personalized guidance, handles Q&A sessions, and ensures that the learner has a solid grasp of historical topics, including Ancient, Medieval, and Modern Indian history.
            The HistoryTutorAgent's responsibilities include helping students with specific queries, providing historical insights, and working with other agents to tailor the learning experience. 
            It collaborates with TeacherAgent for lesson delivery, ProblemGeneratorAgent for creating history-related exercises, and AnswerVerifierAgent to evaluate answers.
            """

    system_message = """
            You are HistoryTutorAgent, a central guide within the Social Studies learning system. Your goal is to support the StudentAgent's learning of Indian history by addressing queries, providing explanations, and guiding through interactive exercises. 
            Collaborate with TeacherAgent for presenting structured lessons, ProblemGeneratorAgent for creating quizzes and exercises, AnswerVerifierAgent for evaluating responses, and LevelAdapterAgent for adjusting lesson complexity.
            You also interact with LearnerModelAgent to track student progress and adjust learning paths for optimal growth.
            Your aim is to maintain a fluid and personalized learning experience, fostering deep understanding and retention of topics across Ancient, Medieval, and Modern Indian history.
            """

    def __init__(self, **kwargs):
        super().__init__(
                name="HistoryTutorAgent",
                human_input_mode="NEVER",  
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description', self.description),
                **kwargs
            )

    def request_recommendations(self, goal_name: str, completion_percentage: float) -> Dict[str, str]:
        # Personalized recommendations based on progress in learning Indian history
        if completion_percentage >= 80:
            return {"recommendation": "You are excelling in this area! Consider exploring more advanced topics, such as the Mughal Empire or India's independence movement."}
        elif completion_percentage >= 50:
            return {"recommendation": "Focus on refining your understanding of key events such as the Maurya Empire and the Gupta period."}
        else:
            return {"recommendation": "Review fundamental concepts from Ancient India, including the Vedic period and early kingdoms."}

    def handle_query(self, query: str, learner_progress: Dict[str, float]) -> str:
        """
        Handles the user query and maintains the conversation context.
        The Tutor will follow up with deeper questions, explanations, and exercises based on the learner's current level.
        """
        if query.lower() == "who was chandragupta maurya?":
            return self.answer_chandragupta_maurya()

        if "when did he rule?" in query.lower():
            return self.answer_chandragupta_maurya_rule()

        # Add more queries as needed for handling other historical topics.
        return "I'm happy to help with more details! Can you please clarify your query?"

    def answer_chandragupta_maurya(self) -> str:
        # Provide information about Chandragupta Maurya
        return "Chandragupta Maurya was the founder of the Maurya Empire in Ancient India. He ruled from 321 BCE until 297 BCE."

    def answer_chandragupta_maurya_rule(self) -> str:
        # Provide more specific details about the period when Chandragupta Maurya ruled
        return "Chandragupta Maurya ruled from 321 BCE to 297 BCE. His reign marked the establishment of the Maurya Empire, one of the largest empires in Indian history."

    def generate_history_exercise(self, current_topic: str) -> str:
        """
        Calls on the ProblemGeneratorAgent to generate a dynamic quiz based on the current topic.
        This can include questions related to Ancient, Medieval, or Modern Indian history.
        """
        if current_topic.lower() == "mughal empire":
            return self.request_problem("Mughal Empire", "timeline")  # Request a timeline exercise related to the Mughal Empire
        
        if current_topic.lower() == "independence movement":
            return self.request_problem("Indian Independence Movement", "fill-in-the-blank")  # Request a fill-in-the-blank exercise related to India's independence movement

        return "Please choose a specific topic you'd like to work on, such as the Mughal Empire or the Indian Independence Movement."

    def request_problem(self, topic: str, problem_type: str) -> str:
        # Interact with ProblemGeneratorAgent to generate a quiz or exercise
        return f"Requesting a {problem_type} exercise on {topic} from the ProblemGeneratorAgent."

    def evaluate_answer(self, answer: str, expected_answer: str) -> str:
        """
        Evaluates the user's answer with AnswerVerifierAgent and provides feedback.
        """
        if answer.lower() == expected_answer.lower():
            return "Correct! Well done."
        else:
            return f"That's incorrect. The correct answer is: {expected_answer}"

    def adapt_learning_level(self, learner_score: float) -> str:
        """
        Adjusts lesson complexity based on the learner's performance, using the LevelAdapterAgent.
        """
        if learner_score >= 85:
            return "You're doing great! I will increase the difficulty of upcoming lessons."
        elif learner_score >= 60:
            return "You're progressing well! Let's continue with the current level and review a few more topics."
        else:
            return "Let's focus on reinforcing some basic concepts before moving on to more advanced topics."

    def track_progress(self, learner_data: Dict[str, float]) -> str:
        """
        Keeps track of the learner's progress, interacts with LearnerModelAgent, and returns a progress update.
        """
        history_score = learner_data.get("IndianHistory", 0)
        return f"Your current mastery of Indian history is {history_score}%. Keep up the good work!"

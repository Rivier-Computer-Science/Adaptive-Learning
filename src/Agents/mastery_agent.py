from typing import Dict
from .conversable_agent import MyConversableAgent

class MasteryAgent(MyConversableAgent):
    description = """
    MasteryAgent is a comprehensive and adaptive agent that tracks the student's mastery of mathematical subjects.
    It implements core functionality to generate questions, determine mastery achievement, and manage topic transitions.
    """
    system_message = """
    You are MasteryAgent, a comprehensive and adaptive agent that tracks the student's mastery of mathematical subjects.
    Your role is to assess student knowledge, generate appropriate math questions, evaluate answers, and determine when mastery is achieved.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="MasteryAgent",
            human_input_mode="NEVER",
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )
        self.current_topic = None
        self.mastery_threshold = 0.8  # 80% correct answers to achieve mastery
        self.questions_asked = 0
        self.correct_answers = 0
        self.topics = [
            "Basic Arithmetic", 
            "Fractions and Decimals", 
            "Algebra Basics", 
            "Geometry Fundamentals",
            "Statistics and Probability"
        ]

    async def ask_question(self, topic):
        prompt = f"Generate a math question about {topic} suitable for a student learning this topic. Include the correct answer."
        response = await self.llm(prompt)
        self.questions_asked += 1
        return response

    async def evaluate_answer(self, question, student_answer, correct_answer):
        prompt = f"""
        Evaluate the following student answer to a math question:
        Question: {question}
        Student's Answer: {student_answer}
        Correct Answer: {correct_answer}

        Is the student's answer correct? If not, what is the error?
        Respond with 'Correct' if the answer is right, or explain the error if it's wrong.
        """
        evaluation = await self.llm(prompt)
        is_correct = evaluation.lower().startswith('correct')
        if is_correct:
            self.correct_answers += 1
        return is_correct, evaluation

    def check_mastery(self):
        if self.questions_asked > 0:
            mastery_score = self.correct_answers / self.questions_asked
            return mastery_score >= self.mastery_threshold
        return False

    def move_to_next_topic(self):
        if self.current_topic in self.topics:
            current_index = self.topics.index(self.current_topic)
            if current_index < len(self.topics) - 1:
                self.current_topic = self.topics[current_index + 1]
                return self.current_topic
        return None  # No more topics

    def reset_for_new_topic(self):
        self.questions_asked = 0
        self.correct_answers = 0

    def get_mastery_status(self):
        if self.questions_asked > 0:
            return f"Mastery for {self.current_topic}: {(self.correct_answers / self.questions_asked) * 100:.2f}%"
        return f"No questions asked for {self.current_topic} yet."

    async def conduct_mastery_test(self, topic, num_questions=5, get_student_answer_func=None):
        self.current_topic = topic
        self.reset_for_new_topic()
        results = []

        for _ in range(num_questions):
            question_and_answer = await self.ask_question(topic)
            question, correct_answer = question_and_answer.split('\n', 1)
            
            if get_student_answer_func:
                student_answer = await get_student_answer_func(question)
            else:
                student_answer = "No answer provided"
            
            is_correct, evaluation = await self.evaluate_answer(question, student_answer, correct_answer)
            results.append({
                'question': question,
                'student_answer': student_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'evaluation': evaluation
            })

        mastery_achieved = self.check_mastery()
        return results, mastery_achieved

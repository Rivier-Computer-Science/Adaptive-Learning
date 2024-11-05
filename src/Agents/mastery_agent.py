from typing import Dict
from .conversable_agent import MyConversableAgent
from src.KnowledgeGraphs.math_taxonomy import (
    topics_and_subtopics, 
    subsub_topics, 
    subsubsub_topics,
    topic_colors
)
import random
import logging

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
        self.mastery_threshold = 0.8
        self.questions_asked = 0
        self.correct_answers = 0
        self.topics = list(topics_and_subtopics.keys())
        self.subtopics = topics_and_subtopics
        self.subsubtopics = subsub_topics
        self.subsubsubtopics = subsubsub_topics
        self.performance_history = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def ask_question(self, topic):
        """Generate adaptive questions based on taxonomy level and student performance"""
        try:
            if topic in self.subtopics:
                subtopic = self._select_appropriate_subtopic(topic)
                if subtopic in self.subsubtopics:
                    subsubtopic = self._select_appropriate_subsubtopic(subtopic)
                    if subsubtopic in self.subsubsubtopics:
                        subsubsubtopic = random.choice(self.subsubsubtopics[subsubtopic])
                        prompt = f"Generate a math question about {subsubsubtopic} suitable for a student learning this topic. Include the correct answer."
                    else:
                        prompt = f"Generate a math question about {subsubtopic} suitable for a student learning this topic. Include the correct answer."
                else:
                    prompt = f"Generate a math question about {subtopic} suitable for a student learning this topic. Include the correct answer."
            else:
                prompt = f"Generate a math question about {topic} suitable for a student learning this topic. Include the correct answer."

            self.questions_asked += 1
            self.logger.info(f"Generating question for topic: {topic}")
            response = await self.llm(prompt)
            return response
        except Exception as e:
            self.logger.error(f"Error generating question: {str(e)}")
            raise

    def _select_appropriate_subtopic(self, topic):
        """Select subtopic based on performance history"""
        if topic in self.performance_history:
            weak_topics = [t for t, p in self.performance_history[topic].items() if p < 0.8]
            if weak_topics:
                return random.choice(weak_topics)
        return random.choice(self.subtopics[topic])

    def _select_appropriate_subsubtopic(self, subtopic):
        """Select subsubtopic based on difficulty level"""
        available_topics = self.subsubtopics.get(subtopic, [])
        if not available_topics:
            return None
        return random.choice(available_topics)

    async def evaluate_answer(self, question, student_answer, correct_answer):
        """Evaluate student answer and provide detailed feedback"""
        prompt = f"""
        Evaluate the following student answer to a math question:
        Question: {question}
        Student's Answer: {student_answer}
        Correct Answer: {correct_answer}

        Provide:
        1. Correctness assessment
        2. Detailed explanation of any errors
        3. Hints for improvement
        4. Related concepts to review
        """
        evaluation = await self.llm(prompt)
        is_correct = evaluation.lower().startswith('correct')
        if is_correct:
            self.correct_answers += 1
            self._update_performance_history(self.current_topic, True)
        else:
            self._update_performance_history(self.current_topic, False)
        
        return is_correct, evaluation

    def _update_performance_history(self, topic, is_correct):
        """Update performance history for adaptive question selection"""
        if topic not in self.performance_history:
            self.performance_history[topic] = {}
        current_performance = self.performance_history[topic].get(topic, 0.5)
        alpha = 0.3  # Learning rate
        new_performance = current_performance + alpha * (1 if is_correct else 0 - current_performance)
        self.performance_history[topic][topic] = new_performance
        self.logger.info(f"Updated performance for {topic}: {new_performance}")

    def check_mastery(self):
        """Check if mastery threshold has been achieved"""
        if self.questions_asked > 0:
            mastery_score = self.correct_answers / self.questions_asked
            return mastery_score >= self.mastery_threshold
        return False

    def get_mastery_status(self):
        """Get detailed mastery status including performance metrics"""
        if self.questions_asked > 0:
            return {
                'topic': self.current_topic,
                'mastery_percentage': (self.correct_answers / self.questions_asked) * 100,
                'questions_attempted': self.questions_asked,
                'correct_answers': self.correct_answers,
                'performance_history': self.performance_history.get(self.current_topic, {})
            }
        return f"No questions asked for {self.current_topic} yet."

    async def conduct_mastery_test(self, topic, num_questions=5, get_student_answer_func=None):
        """Conduct a complete mastery test with adaptive questioning"""
        self.current_topic = topic
        self.reset_for_new_topic()
        results = []

        try:
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
                    'evaluation': evaluation,
                    'topic': topic
                })

            mastery_achieved = self.check_mastery()
            self.logger.info(f"Mastery test completed for {topic}. Mastery achieved: {mastery_achieved}")
            return results, mastery_achieved
        except Exception as e:
            self.logger.error(f"Error during mastery test: {str(e)}")
            raise



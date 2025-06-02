# === mastery_agent.py ===

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
import asyncio

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
        self.results = []
        self.mastery_achieved = False
        self.current_question = None
        self.current_answer = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def reset_for_new_topic(self, topic):
        print(f"[INFO] MasteryAgent resetting state for topic: {topic}")
        self.questions_asked = 0
        self.correct_answers = 0
        self.current_topic = topic
        self.results.clear()
        self.mastery_achieved = False

    async def start_test(self, topic):
        await self.reset_for_new_topic(topic)
        return await self._next_question()

    async def _next_question(self):
        topic = self.current_topic
        try:
            if topic in self.subtopics:
                subtopic = random.choice(self.subtopics[topic])
                if subtopic in self.subsubtopics:
                    subsubtopic = random.choice(self.subsubtopics[subtopic])
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

            response = await self.a_initiate_chat(
                recipient=self,
                message=prompt
            )

            answer_text = response.chat_history[-1]["content"]
            question, correct_answer = answer_text.split("**Answer:**", 1)
            self.current_question = question.strip()
            self.current_answer = correct_answer.strip()
            return self.current_question

        except Exception as e:
            self.logger.error(f"Error generating question: {str(e)}")
            raise

    async def evaluate_next(self, student_answer):
        prompt = f"""
        Evaluate the following student answer to a math question:
        Question: {self.current_question}
        Student's Answer: {student_answer}
        Correct Answer: {self.current_answer}

        Provide:
        1. Correctness assessment
        2. Explanation of any errors
        3. Hints for improvement
        """
        evaluation = await self.a_initiate_chat(
            recipient=self,
            message=prompt
        )
        is_correct = evaluation.chat_history[-1]["content"].lower().startswith('correct')

        if is_correct:
            self.correct_answers += 1
            self._update_performance_history(self.current_topic, True)
        else:
            self._update_performance_history(self.current_topic, False)

        result_entry = {
            'question': self.current_question,
            'student_answer': student_answer,
            'correct_answer': self.current_answer,
            'is_correct': is_correct,
            'evaluation': evaluation.chat_history[-1]['content'],
            'topic': self.current_topic
        }
        self.results.append(result_entry)

        if self.questions_asked >= 5:
            self.mastery_achieved = self.check_mastery()
            return None
        else:
            return await self._next_question()

    def get_results(self):
        return self.results, self.mastery_achieved

    def check_mastery(self):
        if self.questions_asked > 0:
            mastery_score = self.correct_answers / self.questions_asked
            return mastery_score >= self.mastery_threshold
        return False

    def get_mastery_status(self):
        if self.questions_asked > 0:
            return {
                'topic': self.current_topic,
                'mastery_percentage': (self.correct_answers / self.questions_asked) * 100,
                'questions_attempted': self.questions_asked,
                'correct_answers': self.correct_answers,
                'performance_history': self.performance_history.get(self.current_topic, {})
            }
        return f"No questions asked for {self.current_topic} yet."

    def _update_performance_history(self, topic, is_correct):
        if topic not in self.performance_history:
            self.performance_history[topic] = {}
        current_performance = self.performance_history[topic].get(topic, 0.5)
        alpha = 0.3
        new_performance = current_performance + alpha * ((1 if is_correct else 0) - current_performance)
        self.performance_history[topic][topic] = new_performance
        self.logger.info(f"Updated performance for {topic}: {new_performance}")

    # === Added methods to support UI ===

    def get_subtopics_for_topic(self, topic: str):
        return self.subtopics.get(topic, [])

    def get_subsubtopics_for_subtopic(self, subtopic: str):
        return self.subsubtopics.get(subtopic, [])

    async def ask_question(self, topic: str, subtopic: str = None):
        await self.reset_for_new_topic(topic)
        return await self._generate_question_with_subtopic(subtopic or topic)

    async def evaluate_answer(self, question: str, student_answer: str, correct_answer: str):
        prompt = f"""
        Evaluate the following student answer to a math question:
        Question: {question}
        Student's Answer: {student_answer}
        Correct Answer: {correct_answer}

        Provide:
        1. Correctness assessment
        2. Explanation of any errors
        3. Hints for improvement
        """
        evaluation = await self.a_initiate_chat(recipient=self, message=prompt)
        content = evaluation.chat_history[-1]["content"]
        is_correct = content.lower().startswith("correct")
        return is_correct, content

    async def _generate_question_with_subtopic(self, topic):
        prompt = f"[Question] What is 7 + 8?\n[Answer] 15"  # Replace with real logic
        return prompt


from .conversable_agent import MyConversableAgent
from src.KnowledgeGraphs.math_taxonomy import (
    topics_and_subtopics,
    subsub_topics,
    subsubsub_topics,
    topic_colors
)
import logging
from openai import AsyncOpenAI

class MasteryAgent(MyConversableAgent):
    description = """
    MasteryAgent is a specialized AI tutor focused on mathematics education.
    It generates appropriate math questions, evaluates student responses,
    tracks mastery progress, and adapts difficulty based on performance.
    """

    system_message = """
    You are MasteryAgent, an advanced mathematics education agent.
    Your core responsibilities are:
    1. Generate clear, level-appropriate math questions when requested
    2. Provide detailed step-by-step solutions for each question
    3. Evaluate student answers with constructive feedback
    4. Track student progress and adapt difficulty accordingly
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop('name', "MasteryAgent"),
            human_input_mode=kwargs.pop('human_input_mode', "NEVER"),
            system_message=kwargs.pop('system_message', self.system_message),
            description=kwargs.pop('description', self.description),
            **kwargs
        )

        self._init_state()
        self._init_topic_hierarchy()
        self._setup_logging()
        self.client = AsyncOpenAI()

    def _init_state(self):
        self.current_topic = None
        self.current_subtopic = None
        self.questions_asked = 0
        self.correct_answers = 0
        self.mastery_threshold = 0.8
        self.performance_history = {}
        self.adaptive_difficulty = 1.0
        self.mastery_achieved = False
        self.results = []

    def _init_topic_hierarchy(self):
        self.topics = list(topics_and_subtopics.keys())
        self.topic_hierarchy = {
            'topics': topics_and_subtopics,
            'subtopics': subsub_topics,
            'subsubtopics': subsubsub_topics
        }
        self.subtopics = topics_and_subtopics
        self.subsubtopics = subsub_topics
        self.subsubsubtopics = subsubsub_topics

    def _setup_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _get_difficulty_level(self) -> str:
        if self.adaptive_difficulty < 0.8:
            return "basic"
        elif self.adaptive_difficulty < 1.2:
            return "intermediate"
        return "advanced"

    async def _get_completion(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error getting completion: {str(e)}")
            raise

    async def ask_question(self, topic: str, subtopic: str = None) -> str:
        try:
            self.current_topic = topic
            self.current_subtopic = subtopic
            self.questions_asked += 1

            difficulty = self._get_difficulty_level()
            prompt = f"""Generate a {difficulty} level math question about {topic}
            {f'focusing on {subtopic}' if subtopic else ''}.

            Format exactly as:
            [Question]
            (write a {difficulty} level question here)
            [Answer]
            (provide a detailed step-by-step solution)
            """

            completion = await self._get_completion(prompt)
            self.logger.info(f"Generated question for {topic}/{subtopic}")
            self.current_question = completion
            self.current_answer = self.extract_answer_from_text(completion)
            return completion

        except Exception as e:
            self.logger.error(f"Error generating question: {str(e)}")
            raise

    async def evaluate_answer(self, question: str, student_answer: str, correct_answer: str) -> tuple:
        try:
            prompt = f"""
            Evaluate this math answer:
            Question: {question}
            Student Answer: {student_answer}
            Correct Answer: {correct_answer}

            Follow these rules in your evaluation:
            1. Start with exactly "Correct!" or "Incorrect."
            2. Explain why the answer is right or wrong
            3. Provide specific learning points
            4. Suggest related concepts to review

            Keep the response clear and constructive.
            """

            evaluation = await self._get_completion(prompt)
            is_correct = evaluation.lower().startswith('correct')
            self._update_performance_tracking(is_correct)
            return is_correct, evaluation

        except Exception as e:
            self.logger.error(f"Error evaluating answer: {str(e)}")
            raise

    async def evaluate_next(self, student_answer: str) -> str:
        try:
            def normalize(text):
                return text.strip().lower().replace(" ", "").replace("=", "").replace("(", "").replace(")", "")

            if not hasattr(self, "current_question") or not hasattr(self, "current_answer"):
                return "⚠️ No active question to evaluate."

            question = self.current_question
            correct_answer = self.current_answer

            normalized_student_answer = normalize(student_answer)
            normalized_correct_answer = normalize(correct_answer)

            is_correct, evaluation = await self.evaluate_answer(
                question, normalized_student_answer, normalized_correct_answer
            )

            print(f"[DEBUG] Student: {student_answer}, Correct: {correct_answer}, Normalized: {normalized_student_answer} vs {normalized_correct_answer}")
            print(f"[DEBUG] is_correct: {is_correct}")

            self.results.append({
                "question": question,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "evaluation": evaluation,
                "is_correct": is_correct
            })

            next_question = await self.ask_question(self.current_topic, self.current_subtopic)
            return next_question

        except Exception as e:
            self.logger.error(f"[evaluate_next] Error: {str(e)}")
            return "⚠️ An error occurred while evaluating your answer."

    def extract_answer_from_text(self, text: str) -> str:
        if "[Answer]" in text:
            answer_section = text.split("[Answer]", 1)[1].strip()
            for line in answer_section.splitlines():
                line = line.strip()
                if line and "=" in line:
                    return line
            return answer_section.splitlines()[0]
        return ""

    def _update_performance_tracking(self, is_correct: bool):
        if is_correct:
            self.correct_answers += 1

        if self.current_topic not in self.performance_history:
            self.performance_history[self.current_topic] = {
                'attempts': 0,
                'correct': 0,
                'recent_scores': []
            }

        history = self.performance_history[self.current_topic]
        history['attempts'] += 1
        if is_correct:
            history['correct'] += 1

        history['recent_scores'].append(1 if is_correct else 0)
        if len(history['recent_scores']) > 5:
            history['recent_scores'].pop(0)

        self._adjust_difficulty(history['recent_scores'])

    def _adjust_difficulty(self, recent_scores: list):
        if len(recent_scores) >= 3:
            recent_performance = sum(recent_scores[-3:]) / 3
            if recent_performance > 0.8:
                self.adaptive_difficulty = min(1.5, self.adaptive_difficulty + 0.1)
            elif recent_performance < 0.6:
                self.adaptive_difficulty = max(0.5, self.adaptive_difficulty - 0.1)

    def get_subtopics_for_topic(self, topic: str) -> list:
        return self.topic_hierarchy['topics'].get(topic, [])

    def get_subsubtopics_for_subtopic(self, subtopic: str) -> list:
        return self.topic_hierarchy['subtopics'].get(subtopic, [])

    def get_mastery_status(self) -> dict:
        if self.questions_asked == 0:
            return {
                'status': 'No questions attempted',
                'mastery_achieved': False,
                'current_mastery': 0,
                'progress': 0
            }

        correct_ratio = self.correct_answers / self.questions_asked
        return {
            'topic': self.current_topic,
            'subtopic': self.current_subtopic,
            'questions_attempted': self.questions_asked,
            'correct_answers': self.correct_answers,
            'current_mastery': correct_ratio * 100,
            'mastery_achieved': correct_ratio >= self.mastery_threshold,
            'progress': (correct_ratio / self.mastery_threshold) * 100,
            'difficulty_level': self._get_difficulty_level()
        }

    def reset_for_new_topic(self):
        self.questions_asked = 0
        self.correct_answers = 0
        self.adaptive_difficulty = 1.0
        self.mastery_achieved = False

    async def start_test(self, topic):
        self.reset_for_new_topic()
        return await self.ask_question(topic)


from .conversable_agent import MyConversableAgent
from src.KnowledgeGraphs.math_taxonomy import (
    topics_and_subtopics,
    subsub_topics,
    subsubsub_topics,
    topic_colors
)
import logging
from openai import AsyncOpenAI  # Changed to AsyncOpenAI

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
        
        # Initialize state
        self._init_state()
        self._init_topic_hierarchy()
        self._setup_logging()
        
        # Initialize AsyncOpenAI client
        self.client = AsyncOpenAI()

    async def ask_question(self, topic: str, subtopic: str = None) -> str:
        """Generate a math question"""
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

            Requirements:
            1. Question should be clear and well-defined
            2. Solution should include all steps
            3. Include relevant formulas
            4. Match the {difficulty} difficulty level
            """
            
            completion = await self._get_completion(prompt)
            self.logger.info(f"Generated question for {topic}/{subtopic}")
            return completion
            
        except Exception as e:
            self.logger.error(f"Error generating question: {str(e)}")
            raise

    async def evaluate_answer(self, question: str, student_answer: str, correct_answer: str) -> tuple:
        """Evaluate student's answer"""
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

    async def _get_completion(self, prompt: str) -> str:
        """Get completion from OpenAI with proper async handling"""
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

    def _init_state(self):
        """Initialize agent state"""
        self.current_topic = None
        self.current_subtopic = None
        self.questions_asked = 0
        self.correct_answers = 0
        self.mastery_threshold = 0.8
        self.performance_history = {}
        self.adaptive_difficulty = 1.0

    def _init_topic_hierarchy(self):
        """Initialize topic hierarchy from taxonomy"""
        self.topics = list(topics_and_subtopics.keys())
        self.topic_hierarchy = {
            'topics': topics_and_subtopics,
            'subtopics': subsub_topics,
            'subsubtopics': subsubsub_topics
        }

    def _setup_logging(self):
        """Set up logging configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _get_difficulty_level(self) -> str:
        """Get current difficulty level description"""
        if self.adaptive_difficulty < 0.8:
            return "basic"
        elif self.adaptive_difficulty < 1.2:
            return "intermediate"
        return "advanced"

    def _update_performance_tracking(self, is_correct: bool):
        """Update performance tracking and adjust difficulty"""
        if is_correct:
            self.correct_answers += 1
        
        # Update performance history
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
            
        # Update recent scores
        history['recent_scores'].append(1 if is_correct else 0)
        if len(history['recent_scores']) > 5:
            history['recent_scores'].pop(0)
            
        # Adjust difficulty if needed
        self._adjust_difficulty(history['recent_scores'])

    def _adjust_difficulty(self, recent_scores: list):
        """Adjust question difficulty based on recent performance"""
        if len(recent_scores) >= 3:
            recent_performance = sum(recent_scores[-3:]) / 3
            
            if recent_performance > 0.8:  # Consistently good
                self.adaptive_difficulty = min(1.5, self.adaptive_difficulty + 0.1)
            elif recent_performance < 0.6:  # Consistently struggling
                self.adaptive_difficulty = max(0.5, self.adaptive_difficulty - 0.1)

    def get_subtopics_for_topic(self, topic: str) -> list:
        """Get available subtopics for a given topic"""
        return self.topic_hierarchy['topics'].get(topic, [])

    def get_subsubtopics_for_subtopic(self, subtopic: str) -> list:
        """Get available sub-subtopics for a given subtopic"""
        return self.topic_hierarchy['subtopics'].get(subtopic, [])

    def get_mastery_status(self) -> dict:
        """Get current mastery status"""
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
        """Reset state for a new topic"""
        self.questions_asked = 0
        self.correct_answers = 0
        self.adaptive_difficulty = 1.0

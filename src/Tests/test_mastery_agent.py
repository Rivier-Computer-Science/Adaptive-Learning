import unittest
import asyncio
from src.Agents.mastery_agent import MasteryAgent
from src.KnowledgeGraphs.math_taxonomy import topics_and_subtopics

class TestMasteryAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.mastery_agent = MasteryAgent()
        self.test_topic = list(topics_and_subtopics.keys())[0]

    def test_initialization(self):
        """Test proper initialization of MasteryAgent"""
        self.assertIsNotNone(self.mastery_agent)
        self.assertEqual(self.mastery_agent.mastery_threshold, 0.8)
        self.assertEqual(self.mastery_agent.questions_asked, 0)
        self.assertEqual(self.mastery_agent.correct_answers, 0)
        self.assertIsNotNone(self.mastery_agent.topics)

    def test_topic_structure(self):
        """Test proper loading of topic taxonomy"""
        self.assertGreater(len(self.mastery_agent.topics), 0)
        self.assertIn(self.test_topic, self.mastery_agent.topics)
        self.assertIsInstance(self.mastery_agent.subtopics, dict)

    def test_reset_for_new_topic(self):
        """Test resetting progress for new topic"""
        self.mastery_agent.questions_asked = 5
        self.mastery_agent.correct_answers = 3
        self.mastery_agent.reset_for_new_topic()
        self.assertEqual(self.mastery_agent.questions_asked, 0)
        self.assertEqual(self.mastery_agent.correct_answers, 0)

    async def test_ask_question(self):
        """Test question generation"""
        question = await self.mastery_agent.ask_question(self.test_topic)
        self.assertIsNotNone(question)
        self.assertIsInstance(question, str)
        self.assertGreater(len(question), 0)

    async def test_evaluate_answer(self):
        """Test answer evaluation"""
        question = "What is 2 + 2?"
        student_answer = "4"
        correct_answer = "4"
        is_correct, evaluation = await self.mastery_agent.evaluate_answer(
            question, student_answer, correct_answer
        )
        self.assertIsInstance(is_correct, bool)
        self.assertIsInstance(evaluation, str)

    def test_check_mastery(self):
        """Test mastery checking logic"""
        self.mastery_agent.questions_asked = 5
        self.mastery_agent.correct_answers = 4
        self.assertTrue(self.mastery_agent.check_mastery())
        
        self.mastery_agent.questions_asked = 5
        self.mastery_agent.correct_answers = 2
        self.assertFalse(self.mastery_agent.check_mastery())

    async def test_conduct_mastery_test(self):
        """Test full mastery test workflow"""
        async def mock_get_answer(question):
            return "4"  # Mock student answer

        results, mastery_achieved = await self.mastery_agent.conduct_mastery_test(
            self.test_topic,
            num_questions=2,
            get_student_answer_func=mock_get_answer
        )
        
        self.assertIsInstance(results, list)
        self.assertIsInstance(mastery_achieved, bool)
        self.assertEqual(len(results), 2)

    def test_performance_history(self):
        """Test performance history tracking"""
        self.mastery_agent._update_performance_history(self.test_topic, True)
        self.assertIn(self.test_topic, self.mastery_agent.performance_history)
        
def run_async_test(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

if __name__ == '__main__':
    unittest.main()

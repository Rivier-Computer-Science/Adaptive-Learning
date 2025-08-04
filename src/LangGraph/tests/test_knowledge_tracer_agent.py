# src/LangGraph/tests/test_knowledge_tracer_agent.py

import unittest
from src.Models.knowledge_tracer_models import KnowledgeTracerState, KnowledgeTracerOutput
from src.Models.langgraph_state import LangGraphState
from src.LangGraph.agents.knowledge_tracer_agent import run


class TestKnowledgeTracerAgent(unittest.TestCase):

    def test_mastered_level(self):
        state = LangGraphState(
            tracer_input=KnowledgeTracerState(
                correct_answers=9,
                total_questions=10,
                concept="Algebra"
            )
        )
        result = run(state)
        output: KnowledgeTracerOutput = result["tracer_output"]
        self.assertEqual(output.status, "mastered")
        self.assertAlmostEqual(output.mastery_level, 0.9)
        self.assertEqual(output.concept, "Algebra")

    def test_intermediate_level(self):
        state = LangGraphState(
            tracer_input=KnowledgeTracerState(
                correct_answers=5,
                total_questions=10,
                concept="Geometry"
            )
        )
        result = run(state)
        output: KnowledgeTracerOutput = result["tracer_output"]
        self.assertEqual(output.status, "intermediate")
        self.assertAlmostEqual(output.mastery_level, 0.5)
        self.assertEqual(output.concept, "Geometry")

    def test_beginner_level(self):
        state = LangGraphState(
            tracer_input=KnowledgeTracerState(
                correct_answers=3,
                total_questions=10,
                concept="Fractions"
            )
        )
        result = run(state)
        output: KnowledgeTracerOutput = result["tracer_output"]
        self.assertEqual(output.status, "beginner")
        self.assertAlmostEqual(output.mastery_level, 0.3)
        self.assertEqual(output.concept, "Fractions")

    def test_no_input(self):
        state = LangGraphState(tracer_input=None)
        result = run(state)
        self.assertIsNone(result["tracer_output"])


if __name__ == '__main__':
    unittest.main()

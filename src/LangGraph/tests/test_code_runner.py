# src/LangGraph/tests/test_code_runner_agent.py

import unittest
from src.Models.langgraph_state import LangGraphState
from src.LangGraph.agents.code_runner_agent import run


class TestCodeRunnerAgent(unittest.TestCase):

    def test_valid_code(self):
        state = LangGraphState(code_input="print('Hello')")
        result = run(state)
        self.assertTrue(result["code_output"].success)
        self.assertEqual(result["code_output"].stdout, "Hello")
        self.assertIsNone(result["code_output"].stderr)

    def test_invalid_code(self):
        state = LangGraphState(code_input="print(Hello)")  # invalid syntax
        result = run(state)
        self.assertFalse(result["code_output"].success)
        self.assertIsNotNone(result["code_output"].stderr)

    def test_timeout_code(self):
        state = LangGraphState(code_input="while True: pass")  # infinite loop
        result = run(state)
        self.assertFalse(result["code_output"].success)
        self.assertEqual(result["code_output"].stderr, "Execution timed out")


if __name__ == '__main__':
    unittest.main()

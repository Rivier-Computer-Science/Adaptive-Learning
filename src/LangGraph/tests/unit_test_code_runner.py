import unittest
from src.LangGraph.agents.code_runner_agent import run, CodeExecutionState

class TestCodeRunnerAgent(unittest.TestCase):

    def test_successful_code_execution(self):
        input_data = CodeExecutionState(code="print('Hello World')")
        result = run(input_data)
        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "Hello World")
        self.assertIsNone(result["stderr"])

    def test_failing_code_execution(self):
        input_data = CodeExecutionState(code="print(Hello World)")
        result = run(input_data)
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["stderr"])
        self.assertIsNone(result["stdout"])

    def test_timeout_code_execution(self):
        input_data = CodeExecutionState(code="while True: pass")
        result = run(input_data)
        self.assertFalse(result["success"])
        self.assertEqual(result["stderr"], "Execution timed out")
        self.assertIsNone(result["stdout"])

    def test_empty_code_validation(self):
        with self.assertRaises(ValueError):
            CodeExecutionState(code="   ")

if __name__ == "__main__":
    unittest.main()

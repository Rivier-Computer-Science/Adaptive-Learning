import unittest
from src.Agents.scenario_input_agent import run as scenario_input, ScenarioInput
from langgraph.graph import StateGraph

class TestScenarioInputAgent(unittest.TestCase):

    def setUp(self):
        # Set up the LangGraph with ScenarioInputAgent node
        builder = StateGraph(ScenarioInput)
        builder.add_node("ScenarioInputAgent", scenario_input)
        builder.set_entry_point("ScenarioInputAgent")
        self.graph = builder.compile()

    def test_valid_input(self):
        # Prepare mock input
        test_input = {"scenario": "What happens if difficulty increases?"}
        
        # Run the LangGraph pipeline
        result = self.graph.invoke(test_input)

        # Assert the output contains the scenario key and matches the input
        self.assertIn("scenario", result)
        self.assertEqual(result["scenario"], test_input["scenario"])

    def test_empty_input(self):
        # Prepare empty scenario input
        test_input = {"scenario": ""}
        result = self.graph.invoke(test_input)

        # You can update this check based on how you handle empty inputs
        self.assertIn("scenario", result)
        self.assertEqual(result["scenario"], "")

if __name__ == '__main__':
    unittest.main()

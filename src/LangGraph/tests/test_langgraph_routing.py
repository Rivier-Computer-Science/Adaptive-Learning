import unittest
from src.LangGraph.workflow.langgraph_main import graph

class TestLangGraphRouting(unittest.TestCase):

    def test_successful_routing(self):
        input_data = {
            "student_input": {
                "goal_name": "Learn Python",
                "description": "Basics",
                "target_date": "2024-12-01T00:00:00",
                "priority": "High",
                "category": "Programming"
            },
            "code_input": "print('Success Path')"
        }
        result = graph.invoke(input_data)
        self.assertIn("tracer_output", result)
        self.assertEqual(result["tracer_output"].status, "mastered")

    def test_fallback_due_to_missing_goal(self):
        input_data = {
            "student_input": {
                "goal_name": "",
                "description": "No goal name",
                "target_date": "2024-12-01T00:00:00",
                "priority": "Medium",
                "category": "Science"
            },
            "code_input": "print('Hello')"
        }
        result = graph.invoke(input_data)
        self.assertIsNone(result["tracer_output"])  
        self.assertFalse(result["tracer_output"])   

    def test_fallback_due_to_code_error(self):
        input_data = {
            "student_input": {
                "goal_name": "Break Code",
                "description": "Trigger failure",
                "target_date": "2024-12-01T00:00:00",
                "priority": "Low",
                "category": "Programming"
            },
            "code_input": "print(Invalid)"  # invalid Python
        }
        result = graph.invoke(input_data)
        self.assertIsNone(result["tracer_output"])  
        self.assertFalse(result["tracer_output"]) 

if __name__ == '__main__':
    unittest.main()

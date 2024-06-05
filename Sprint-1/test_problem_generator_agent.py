import unittest
from unittest.mock import patch
from agents import ProblemGeneratorAgent
 
class TestProblemGeneratorAgent(unittest.TestCase):
 
    @patch('agents.gpt4_config', {'model': "gpt-3.5-turbo"})
    def test_initialization(self):
        agent = ProblemGeneratorAgent()
        
        self.assertEqual(agent.name, "Problem Generator")
        self.assertEqual(agent.human_input_mode, "NEVER")
        self.assertEqual(agent.llm_config, {'model': "gpt-3.5-turbo"})
        self.assertEqual(agent.system_message, agent.descriptioin)
        self.assertEqual(agent.description, agent.descriptioin)
 
if __name__ == '__main__':
    unittest.main()
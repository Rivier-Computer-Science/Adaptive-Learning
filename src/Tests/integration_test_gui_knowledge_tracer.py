import unittest
from unittest.mock import Mock, patch
import panel as pn
from src.Agents.gui_knowledge_tracer_fsms import FSMGraphTracerConsole
from src.Agents.group_chat_manager_agent import CustomGroupChat, CustomGroupChatManager
from src.Agents.agents import MyConversableAgent

class TestGUIKnowledgeTracerIntegration(unittest.TestCase):
    def setUp(self):
        # Mock the agents
        self.mock_student = Mock()
        self.mock_knowledge_tracer = Mock()
        self.mock_problem_generator = Mock()
        self.mock_solution_verifier = Mock()
        
        # Agent dictionary
        self.agents_dict = {
            "student": self.mock_student,
            "knowledge_tracer": self.mock_knowledge_tracer,
            "problem_generator": self.mock_problem_generator,
            "solution_verifier": self.mock_solution_verifier
        }
        
        # Mock the groupchat
        self.mock_groupchat = Mock(spec=CustomGroupChat)
        
        # Initialize FSM and GroupChatManager
        self.fsm = FSMGraphTracerConsole(self.agents_dict)
        self.manager = CustomGroupChatManager(groupchat=self.mock_groupchat, filename="test_progress.json")
        self.fsm.register_groupchat_manager(self.manager)

if __name__ == '__main__':
    unittest.main()

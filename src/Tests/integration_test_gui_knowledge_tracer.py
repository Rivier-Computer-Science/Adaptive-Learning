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

    @patch('src.UI.gui_knowledge_tracer.pn.serve')
    def test_gui_initialization(self, mock_serve):
        from src.UI.gui_knowledge_tracer import create_app
        app = create_app()
        self.assertIsInstance(app, pn.viewable.Viewable)
        mock_serve.assert_called_with(app, callback_exception='verbose')

    def test_groupchat_manager_initialization(self):
        self.manager.get_chat_history_and_initialize_chat(filename="test_progress.json", chat_interface=Mock())
        self.mock_groupchat.get_messages.assert_called_once()

    def test_integration_with_agents(self):
        # Ensure that agents' methods like groupchat_manager assignment are being called
        for agent in self.agents_dict.values():
            self.assertEqual(agent.groupchat_manager, self.manager)

if __name__ == '__main__':
    unittest.main()

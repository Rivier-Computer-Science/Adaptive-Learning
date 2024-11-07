import unittest
import panel as pn
from src.UI.panel_gui_tabs import MathMasteryInterface
from src.Agents.agents import agents_dict, AgentKeys

class TestMasteryIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.mastery_agent = agents_dict[AgentKeys.MASTERY.value]
        self.interface = MathMasteryInterface(self.mastery_agent)

    def test_interface_initialization(self):
        """Test proper initialization of interface components"""
        self.assertIsNotNone(self.interface.topic_selector)
        self.assertIsNotNone(self.interface.question_display)
        self.assertIsNotNone(self.interface.answer_input)
        self.assertIsNotNone(self.interface.progress_bar)

    def test_topic_selection(self):
        """Test topic selection functionality"""
        initial_topic = self.interface.topic_selector.value
        self.assertIn(initial_topic, self.mastery_agent.topics)

    def test_progress_tracking(self):
        """Test progress tracking integration"""
        self.interface.progress_bar.value = 50
        self.assertEqual(self.interface.progress_bar.value, 50)

    def test_layout_creation(self):
        """Test UI layout creation"""
        layout = self.interface.create_layout()
        self.assertIsInstance(layout, pn.Column)

if __name__ == '__main__':
    unittest.main()
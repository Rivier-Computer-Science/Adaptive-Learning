import unittest
from unittest.mock import Mock, MagicMock
from src.Agents import gui_knowledge_tracer_fsms as fsm

class TestFSMGraphTracerConsole(unittest.TestCase):
    def setUp(self):
        # Mock the agents: student, knowledge_tracer, problem_generator, solution_verifier
        self.mock_student = Mock()
        self.mock_knowledge_tracer = Mock()
        self.mock_problem_generator = Mock()
        self.mock_solution_verifier = Mock()
        
        # Create the agent dictionary
        self.agents_dict = {
            "student": self.mock_student,
            "knowledge_tracer": self.mock_knowledge_tracer,
            "problem_generator": self.mock_problem_generator,
            "solution_verifier": self.mock_solution_verifier
        }
        
        # Initialize FSMGraphTracerConsole with mock agents
        self.fsm = fsm.FSMGraphTracerConsole(self.agents_dict)
        self.fsm.kg = {0: "Addition", 1: "Subtraction", 2: "Multiplication", 3: "Division"}

    def test_initial_state(self):
        self.assertEqual(self.fsm.current_state, "Initial")

    def test_generate_first_question(self):
        # Simulate user choosing a concept
        with unittest.mock.patch('builtins.input', return_value='1'):  # Selects "Addition"
            next_agent = self.fsm.next_speaker_selector()
            self.assertEqual(self.fsm.current_state, "GenerateFirstQuestion")
            self.assertEqual(self.fsm.skill_level, 0)  # Addition is index 0
            self.assertEqual(next_agent, self.fsm.knowledge_tracer)

    def test_question_generated(self):
        # Move FSM to "GenerateFirstQuestion" state
        self.fsm.current_state = "GenerateFirstQuestion"
        self.fsm.skill_level = 0
        
        # Mock ProblemGenerator response
        self.mock_problem_generator.last_message.return_value = {"content": "What is 2 + 2?"}
        
        next_agent = self.fsm.next_speaker_selector()
        
        self.assertEqual(self.fsm.pg_response, "What is 2 + 2?")
        self.assertEqual(self.fsm.current_state, "AwaitStudentAnswer")
        self.assertEqual(next_agent, self.fsm.problem_generator)

    def test_verify_solution(self):
        # Move FSM to "VerifySolution" state
        self.fsm.current_state = "VerifySolution"
        self.fsm.pg_response = "What is 2 + 2?"
        self.fsm.student_response = "4"
        
        # Mock groupchat and verifier response
        self.fsm.groupchat_manager = Mock()
        self.fsm.groupchat_manager.groupchat.get_messages.return_value = [{'content': 'Yes, the answer is correct.'}]
        
        next_agent = self.fsm.next_speaker_selector()
        
        self.assertEqual(self.fsm.current_state, "AdaptLevel")
        self.assertTrue(self.fsm.was_correct)
        self.assertEqual(next_agent, self.fsm.knowledge_tracer)

if __name__ == '__main__':
    unittest.main()

import logging
from transitions import Machine
from transitions.core import MachineError
from enum import Enum

# Set up logging configuration
#logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class FSMStates(Enum):
    AWAITING_TOPIC = 'awaiting_topic'
    PRESENTING_LESSON = 'presenting_lesson'
    AWAITING_PROBLEM = 'awaiting_problem'
    AWAITING_ANSWER = 'awaiting_answer'
    VERIFYING_ANSWER = 'verifying_answer'
    WRITING_PROGRAM = 'writing_program'
    RUNNING_CODE = 'running_code'
    VERIFYING_CODE = 'verifying_code'  # New state
    UPDATING_MODEL = 'updating_model'
    ADAPTING_LEVEL = 'adapting_level'
    MOTIVATING = 'motivating'

class AgentKeys(Enum):
    TEACHER = 'teacher'
    TUTOR = 'tutor'
    STUDENT = 'student'
    KNOWLEDGE_TRACER = 'knowledge_tracer'
    PROBLEM_GENERATOR = 'problem_generator'
    SOLUTION_VERIFIER = 'solution_verifier'
    PROGRAMMER = 'programmer'
    CODE_RUNNER = 'code_runner'
    CODE_RUNNER_VERIFIER = 'code_runner_verifier'  # New agent
    LEARNER_MODEL = 'learner_model'
    LEVEL_ADAPTER = 'level_adapter'
    MOTIVATOR = 'motivator'
    GAMIFICATION = 'gamification'

class TeachMeFSM:
    def __init__(self, agents):
        self.agents = agents
        self.last_speaker = None
        self.next_agent = None
        self.run_attempts = 0  # Counter for code running attempts
        self.current_state_enum = FSMStates.AWAITING_TOPIC
        self.previous_state_enum = None

        # Define states
        states = [state.value for state in FSMStates]

        # Initialize the state machine
        self.machine = Machine(
            model=self,
            states=states,
            initial=FSMStates.AWAITING_TOPIC.value
        )

        # Define transitions
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.AWAITING_TOPIC.value,
            dest=FSMStates.PRESENTING_LESSON.value,
            after='set_teacher'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.PRESENTING_LESSON.value,
            dest=FSMStates.AWAITING_PROBLEM.value,
            after='set_tutor'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.AWAITING_PROBLEM.value,
            dest=FSMStates.AWAITING_ANSWER.value,
            after='set_problem_generator'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.AWAITING_ANSWER.value,
            dest=FSMStates.VERIFYING_ANSWER.value,
            after='set_student'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.VERIFYING_ANSWER.value,
            dest=FSMStates.WRITING_PROGRAM.value,
            after='set_solution_verifier'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.WRITING_PROGRAM.value,
            dest=FSMStates.RUNNING_CODE.value,
            after='set_programmer'
        )

        # Transition from RUNNING_CODE to VERIFYING_CODE
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.RUNNING_CODE.value,
            dest=FSMStates.VERIFYING_CODE.value,
            after='set_code_runner_verifier'
        )

        # Transition from VERIFYING_CODE to UPDATING_MODEL if code is correct
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.VERIFYING_CODE.value,
            dest=FSMStates.UPDATING_MODEL.value,
            conditions='code_is_correct',
            after='set_learner_model'
        )

        # Transition from VERIFYING_CODE to WRITING_PROGRAM if code is incorrect
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.VERIFYING_CODE.value,
            dest=FSMStates.WRITING_PROGRAM.value,
            unless='code_is_correct',
            after='increment_attempts'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.UPDATING_MODEL.value,
            dest=FSMStates.ADAPTING_LEVEL.value,
            after='set_learner_model'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.ADAPTING_LEVEL.value,
            dest=FSMStates.MOTIVATING.value,
            after='set_level_adapter'
        )

        # Transitions from 'motivating' state with conditions
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.MOTIVATING.value,
            dest=FSMStates.PRESENTING_LESSON.value,
            conditions='adapter_agent_says_increase_difficulty',
            after='set_teacher'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.MOTIVATING.value,
            dest=FSMStates.AWAITING_PROBLEM.value,
            unless='adapter_agent_says_increase_difficulty',
            after='set_tutor'
        )

    # State entry method
    def on_enter_state(self):
        self.previous_state_enum = self.current_state_enum
        self.current_state_enum = FSMStates(self.state)
        if self.previous_state_enum:
            logging.info(f"Transitioned from '{self.previous_state_enum.name}' to '{self.current_state_enum.name}'")
        else:
            logging.info(f"Entered initial state '{self.current_state_enum.name}'")

    # Action methods
    def set_teacher(self):
        self.next_agent = self.agents[AgentKeys.TEACHER.value]
        logging.info(f"Next agent set to 'teacher'")
        self.on_enter_state()

    def set_tutor(self):
        self.next_agent = self.agents[AgentKeys.TUTOR.value]
        logging.info(f"Next agent set to 'tutor'")
        self.on_enter_state()

    def set_problem_generator(self):
        self.next_agent = self.agents[AgentKeys.PROBLEM_GENERATOR.value]
        logging.info(f"Next agent set to 'problem_generator'")
        self.on_enter_state()

    def set_student(self):
        self.next_agent = self.agents[AgentKeys.STUDENT.value]
        logging.info(f"Next agent set to 'student'")
        self.on_enter_state()

    def set_solution_verifier(self):
        self.next_agent = self.agents[AgentKeys.SOLUTION_VERIFIER.value]
        logging.info(f"Next agent set to 'solution_verifier'")
        self.on_enter_state()

    def set_programmer(self):
        self.next_agent = self.agents[AgentKeys.PROGRAMMER.value]
        logging.info(f"Next agent set to 'programmer'")
        self.on_enter_state()

    def set_code_runner(self):
        self.next_agent = self.agents[AgentKeys.CODE_RUNNER.value]
        logging.info(f"Next agent set to 'code_runner'")
        self.on_enter_state()

    def set_code_runner_verifier(self):
        self.next_agent = self.agents[AgentKeys.CODE_RUNNER_VERIFIER.value]
        logging.info(f"Next agent set to 'code_runner_verifier'")
        self.on_enter_state()

    def set_learner_model(self):
        self.next_agent = self.agents[AgentKeys.LEARNER_MODEL.value]
        logging.info(f"Next agent set to 'learner_model'")
        self.on_enter_state()

    def set_level_adapter(self):
        self.next_agent = self.agents[AgentKeys.LEVEL_ADAPTER.value]
        logging.info(f"Next agent set to 'level_adapter'")
        self.on_enter_state()

    # Outputs for managing attempts
    def increment_attempts(self):
        self.run_attempts += 1
        logging.info(f"Run attempts incremented to {self.run_attempts}")

    def reset_attempts(self):
        self.run_attempts = 0
        logging.info("Run attempts reset to 0")

    # Conditions
    def code_is_correct(self):
        """
        Check if the code run was successful by analyzing the groupchat_manager messages.
        """
        # Get all message history from the groupchat manager
        all_messages = self.groupchat_manager.groupchat.get_messages()
        
        # Get the latest message from the groupchat manager to ensure accuracy
        if all_messages:
            last_message = all_messages[-1]
            logging.info(f"Evaluating message from sender '{last_message['name']}': {last_message['content']}")
            if last_message['name'] == 'CodeRunnerAgent' and 'exitcode: 0' in last_message['content']:
                logging.info("Code run succeeded with exit code 0.")
                return True

        # If no successful message is found, return False
        logging.info("Code run did not succeed.")
        return False

 
    def code_is_not_correct(self):
        return not self.code_is_correct()
 
    def adapter_agent_says_increase_difficulty(self):
        from random import choice
        decision = choice([True, False])
        logging.info(f"Adapter agent suggests increasing difficulty: {decision}")
        return decision

    # Handle invalid transitions within next_speaker_selector
    def next_speaker_selector(self, last_speaker, groupchat):
        self.last_speaker = last_speaker

        # Try to advance the state machine
        try:
            logging.info('advance called')
            self.advance()
        except MachineError as e:
            # Handle invalid transitions
            logging.warning(f"Invalid transition attempted: {e}")
            # Default to tutor agent
            self.next_agent = self.agents[AgentKeys.TUTOR.value]
            logging.info("Next agent set to 'tutor'")
            self.on_enter_state()

        return self.next_agent

    def register_groupchat_manager(self, groupchat_manager):
        self.groupchat_manager = groupchat_manager
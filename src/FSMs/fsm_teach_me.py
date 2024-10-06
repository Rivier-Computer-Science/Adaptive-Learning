import logging
from transitions import Machine
from transitions.core import MachineError
from enum import Enum
from src.Agents.agents import AgentKeys

# Set up logging configuration
#logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


#######################################################
# STATES
########################################################
class FSMStates(Enum):
    AWAITING_TOPIC = 'awaiting_topic'
    PRESENTING_LESSON = 'presenting_lesson'
    AWAITING_PROBLEM = 'awaiting_problem'
    AWAITING_ANSWER = 'awaiting_answer'
    VERIFYING_ANSWER = 'verifying_answer'
    WRITING_PROGRAM = 'writing_program'
    RUNNING_CODE = 'running_code'
    VERIFYING_CODE = 'verifying_code'  
    UPDATING_MODEL = 'updating_model'
    ADAPTING_LEVEL = 'adapting_level'
    MOTIVATING = 'motivating'




def on_enter_updating_model():
    logging.info("Entering state UPDATING_MODEL")
    # Add any specific initialization logic here


entry_callbacks = {
    FSMStates.UPDATING_MODEL: on_enter_updating_model,
    # Add other states if needed...
}


def on_exit_verifying_code():
    logging.info("Exiting state VERIFYING_CODE")

exit_callbacks = {
    FSMStates.VERIFYING_CODE: on_exit_verifying_code,
     # Add mappings for the rest of the states...
}

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

        self.machine = Machine(model=self, states=states, initial=FSMStates.AWAITING_TOPIC.value)

        # Add states with entry and exit callbacks
        # Add states with entry and exit callbacks
        for state in FSMStates:
            # Prepare the state configuration
            state_name = state.value  # Get the state name
            
            # Add the state with entry and exit callbacks if they exist
            self.machine.add_state(state_name, 
                                   on_enter=entry_callbacks.get(state, None), 
                                   on_exit=exit_callbacks.get(state, None))


        #####################################################
        # TRANSITIONS
        #####################################################
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
            after='set_problem_generator'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.AWAITING_PROBLEM.value,
            dest=FSMStates.AWAITING_ANSWER.value,
            after='set_student'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.AWAITING_ANSWER.value,
            dest=FSMStates.VERIFYING_ANSWER.value,
            after='set_solution_verifier'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.VERIFYING_ANSWER.value,
            dest=FSMStates.WRITING_PROGRAM.value,
            after='set_programmer'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.WRITING_PROGRAM.value,
            dest=FSMStates.RUNNING_CODE.value,
            after='set_code_runner'
        )

        # Transition from RUNNING_CODE to VERIFYING_CODE
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.RUNNING_CODE.value,
            dest=FSMStates.VERIFYING_CODE.value,
            after='set_code_runner_verifier'
        )

 
        # Transition from VERIFYING_CODE to WRITING_PROGRAM if code is incorrect
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.VERIFYING_CODE.value,
            dest=FSMStates.WRITING_PROGRAM.value,  
            unless='code_is_correct',
            after='increment_attempts'
        )

 
        # Transition from VERIFYING_CODE to UPDATING_MODEL if code is correct
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.VERIFYING_CODE.value,
            dest=FSMStates.UPDATING_MODEL.value,
            conditions='code_is_correct',
            after='set_learner_model'
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
        logging.info(f"Transitioning to state '{self.current_state_enum.name}'")
        if self.previous_state_enum:
            logging.info(f"Transitioned from '{self.previous_state_enum.name}' to '{self.current_state_enum.name}'")
        else:
            logging.info(f"Entered initial state '{self.current_state_enum.name}'")


    # Action methods

    def set_teacher(self):
        try:
            self.next_agent = self.agents[AgentKeys.TEACHER.value]
            logging.info(f"set_teacher(): Next agent set to 'teacher'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_tutor(self):
        try:
            self.next_agent = self.agents[AgentKeys.TUTOR.value]
            logging.info(f"set_tutor(): Next agent set to 'tutor'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_problem_generator(self):
        try:
            self.next_agent = self.agents[AgentKeys.PROBLEM_GENERATOR.value]
            logging.info(f"set_problem_generator(): Next agent set to 'problem_generator'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_student(self):
        try:
            self.next_agent = self.agents[AgentKeys.STUDENT.value]
            logging.info(f"set_student(): Next agent set to 'student'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_solution_verifier(self):
        try:
            self.next_agent = self.agents[AgentKeys.SOLUTION_VERIFIER.value]
            logging.info(f"set_solution_verifier(): Next agent set to 'solution_verifier'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_programmer(self):
        try:
            self.next_agent = self.agents[AgentKeys.PROGRAMMER.value]
            logging.info(f"set_programmer(): Next agent set to 'programmer'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_code_runner(self):
        try:
            self.next_agent = self.agents[AgentKeys.CODE_RUNNER.value]
            logging.info(f"set_code_runner(): Next agent set to 'code_runner'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_code_runner_verifier(self):
        try:
            self.next_agent = self.agents[AgentKeys.CODE_RUNNER_VERIFIER.value]
            logging.info(f"set_code_runner_verifier(): Next agent set to 'code_runner_verifier'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
            self.next_agent = None   # DEBUG
        self.on_enter_state()

    def set_learner_model(self):
        try:
            self.next_agent = self.agents[AgentKeys.LEARNER_MODEL.value]
            logging.info(f"set_learner_model(): Next agent set to 'learner_model'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
            self.next_agent = None   # DEBUG
        self.on_enter_state()

    def set_level_adapter(self):
        try:
            self.next_agent = self.agents[AgentKeys.LEVEL_ADAPTER.value]
            logging.info(f"set_level_adapter(): Next agent set to 'level_adapter'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()


    # Outputs for managing attempts
    def increment_attempts(self):
        self.run_attempts += 1
        logging.info(f"increment_attempts(): Run attempts incremented to {self.run_attempts}")

    def reset_attempts(self):
        self.run_attempts = 0
        logging.info("reset_attempts(): Run attempts reset to 0")

    # Conditions
    # def code_is_correct(self):
    #     """
    #     Check if the code run was successful by analyzing the groupchat_manager messages.
    #     """
    #     # Get all message history from the groupchat manager
    #     all_messages = self.groupchat_manager.groupchat.get_messages()
        
    #     # Get the latest message from the groupchat manager to ensure accuracy
    #     if all_messages:
    #         last_message = all_messages[-1]
    #         logging.info(f"Evaluating message from sender '{last_message['name']}': {last_message['content']}")
    #         if last_message['name'] == 'CodeRunnerAgent' and 'exitcode: 0' in last_message['content']:
    #             logging.info("Code run succeeded with exit code 0.")
    #             return True

    #     # If no successful message is found, return False
    #     logging.info("Code run did not succeed.")
    #     return False
    
    def code_is_correct(self):
        """
        Check if the code run was successful by analyzing the groupchat_manager messages.
        """
        if not hasattr(self, 'groupchat_manager') or not self.groupchat_manager:
            logging.error("Groupchat manager not registered or is None.")
            
        # Get all message history from the groupchat manager
        all_messages = self.groupchat_manager.groupchat.get_messages()
        
        # Get the latest message from the groupchat manager to ensure accuracy
        if all_messages:
            last_message = all_messages[-1]
            logging.info(f"Evaluating message from sender '{last_message['name']}': {last_message['content']}")
            if ( "code executed successfully" in last_message['content']):
                logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!Code run succeeded with exit code 0.")
                return True

        # If no successful message is found, return False
        logging.info("!!!!!!!!!!!!!!!!!!!!! Code run did not succeed.")
        return False
 
    def code_is_not_correct(self):
        return not self.code_is_correct()
 
    def adapter_agent_says_increase_difficulty(self):
        from random import choice
        decision = choice([True, False])
        logging.info(f"adapter_agent_says_increase_difficulty(): Adapter agent suggests increasing difficulty: {decision}")
        return decision

    # Handle invalid transitions within next_speaker_selector
    def next_speaker_selector(self, last_speaker, groupchat):
        logging.info(f"################################ next_speaker_selector(): last_speaker={last_speaker}")
        self.last_speaker = last_speaker

        # Try to advance the state machine
        try:
            logging.info(f"next_speaker_selector(): advance called. last_speaker= '{self.last_speaker}'")
            self.advance()
            logging.info(f"next_speaker_selector(): advance FINISHED. next_speaker= '{self.next_agent}'")
        except MachineError as e:
            # Handle invalid transitions
            logging.warning(f"Invalid transition attempted: {e}")
            # Default to tutor agent
            try:
                self.next_agent = self.agents[AgentKeys.TUTOR.value]
                logging.info("Next agent set to 'tutor'")
            except KeyError as e:
                logging.error(f"Agent not found when defaulting to tutor: {e}")
                self.next_agent = None
            self.on_enter_state()

        # Ensure next_agent is valid before returning
        if not self.next_agent:
            logging.error("No valid next agent was found. Setting to 'tutor' as fallback.")
            try:
                self.next_agent = self.agents[AgentKeys.TUTOR.value]
            except KeyError as e:
                logging.error(f"Fallback agent also not found: {e}")
                self.next_agent = None

        return self.next_agent


    def register_groupchat_manager(self, groupchat_manager):
        self.groupchat_manager = groupchat_manager
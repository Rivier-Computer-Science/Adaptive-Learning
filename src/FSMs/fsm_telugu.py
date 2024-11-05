import logging
from transitions import Machine
from transitions.core import MachineError
from enum import Enum
import src.Agents.telugu_agents as agents


#######################################################
# STATES
########################################################
class FSMStates(Enum):
    AWAITING_TOPIC = 'awaiting_topic'
    PRESENTING_LESSON = 'presenting_lesson'
    AWAITING_PROBLEM = 'awaiting_problem'
    AWAITING_ANSWER = 'awaiting_answer'
    VERIFYING_ANSWER = 'verifying_answer'
    UPDATING_MODEL = 'updating_model'
    ADAPTING_LEVEL = 'adapting_level'
    MOTIVATING = 'motivating'




def on_enter_updating_model():
    logging.debug("Entering state UPDATING_MODEL")
    # Add any specific initialization logic here


entry_callbacks = {
    FSMStates.UPDATING_MODEL: on_enter_updating_model,
    # Add other states if needed...
}


def on_exit_verifying_answer():
    logging.debug("Exiting state VERIFYING_ANSWER")

exit_callbacks = {
    FSMStates.VERIFYING_ANSWER: on_exit_verifying_answer,
     # Add mappings for the rest of the states...
}

class TeachMeFSM:
    def __init__(self, agents, AgentKeys=agents.AgentKeys):
        logging.debug("Initializing Telugu TeachMeFSM")
        self.agents = agents
        self.AgentKeys = AgentKeys
        self.last_speaker = None
        self.next_agent = None
        self.current_state_enum = FSMStates.AWAITING_TOPIC
        self.previous_state_enum = None

        # Define states
        states = [state.value for state in FSMStates]
        logging.debug("TeachMeFSM: states defined")

        self.machine = Machine(model=self, states=states, initial=FSMStates.AWAITING_TOPIC.value)
        logging.debug("TeachMeFSM: Machine() created")

        # Add states with entry and exit callbacks
        # Add states with entry and exit callbacks
        for state in FSMStates:
            # Prepare the state configuration
            state_name = state.value  # Get the state name
            
            # Add the state with entry and exit callbacks if they exist
            self.machine.add_state(state_name, 
                                   on_enter=entry_callbacks.get(state, None), 
                                   on_exit=exit_callbacks.get(state, None))

            logging.debug(f"TeachMeFSM: state {state_name} defined")   
       

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
            dest=FSMStates.UPDATING_MODEL.value,
            after='set_learner_model'
        )

 
        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.UPDATING_MODEL.value,
            dest=FSMStates.ADAPTING_LEVEL.value,
            after='set_level_adapter'
        )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.ADAPTING_LEVEL.value,
            dest=FSMStates.MOTIVATING.value,
            after='set_motivator'
        )

        # Transitions from 'motivating' state with conditions
        # TODO: Consider whether to only go to the teacher if level increases
        # self.machine.add_transition(
        #     trigger='advance',
        #     source=FSMStates.MOTIVATING.value,
        #     dest=FSMStates.AWAITING_PROBLEM.value,
        #     unless='adapter_agent_says_increase_difficulty',
        #     after='set_problem_generator'
        # )

        self.machine.add_transition(
            trigger='advance',
            source=FSMStates.MOTIVATING.value,
            dest=FSMStates.PRESENTING_LESSON.value,
            #conditions='adapter_agent_says_increase_difficulty',
            after='set_teacher'
        )

        logging.debug("TeachMeFSM: transitions added")
        logging.info("TeachMeFSM initialized")


    # State entry method
    def on_enter_state(self):
        self.previous_state_enum = self.current_state_enum
        self.current_state_enum = FSMStates(self.state)
        logging.debug(f"Transitioning to state '{self.current_state_enum.name}'")
        if self.previous_state_enum:
            logging.info(f"Transitioned from '{self.previous_state_enum.name}' to '{self.current_state_enum.name}'")
        else:
            logging.info(f"Entered initial state '{self.current_state_enum.name}'")


    # Action methods

    def set_teacher(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.TEACHER.value]
            logging.debug(f"set_teacher(): Next agent set to 'teacher'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_tutor(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.TUTOR.value]
            logging.debug(f"set_tutor(): Next agent set to 'tutor'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_problem_generator(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.PROBLEM_GENERATOR.value]            
            logging.debug(f"set_problem_generator(): Next agent set to 'problem_generator'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_student(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.STUDENT.value]
            logging.debug(f"set_student(): Next agent set to 'student'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_solution_verifier(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.SOLUTION_VERIFIER.value]
            logging.debug(f"set_solution_verifier(): Next agent set to 'solution_verifier'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_learner_model(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.LEARNER_MODEL.value]
            logging.debug(f"set_learner_model(): Next agent set to 'learner_model'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
            self.next_agent = None   # DEBUG
        self.on_enter_state()

    def set_level_adapter(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.LEVEL_ADAPTER.value]
            logging.debug(f"set_level_adapter(): Next agent set to 'level_adapter'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()

    def set_motivator(self):
        try:
            self.next_agent = self.agents[self.AgentKeys.MOTIVATOR.value]
            logging.debug(f"set_motivator(): Next agent set to 'motivator'")
        except KeyError as e:
            logging.error(f"Agent not found: {e}")
        self.on_enter_state()
   
 
    def adapter_agent_says_increase_difficulty(self):
        last_level_adapter_message = None
        # Iterate through the messages backwards
        messages = self.groupchat_manager.groupchat.get_messages()
        for message in reversed(messages):
            if message['name'] == 'LevelAdapterAgent':
                last_level_adapter_message = message
                break  # Stop once the first match is found

        # Check if a message was found and print it
        if last_level_adapter_message:
            logging.info(f"Last level_adapter message:  {last_level_adapter_message}")
            if "increasing the difficulty" in last_level_adapter_message["content"]:
                return True
        
        logging.info("No messages from level_adapter found.")
        print("\n\n messages \n\n", messages)
        
        return False

    # Handle invalid transitions within next_speaker_selector
    def next_speaker_selector(self, last_speaker, groupchat):
        self.last_speaker = last_speaker

        # Try to advance the state machine
        try:
            self.advance()
            logging.info(f"next_speaker_selector(): advance FINISHED. last_speaker= {self.last_speaker.name}. next_speaker= {self.next_agent.name}")
        except MachineError as e:
            # Handle invalid transitions
            logging.warning(f"Invalid transition attempted: {e}")
            # Default to tutor agent
            try:
                self.next_agent = self.agents[self.AgentKeys.TUTOR.value]
                logging.warning("Next agent set to 'tutor'")
            except KeyError as e:
                logging.error(f"Agent not found when defaulting to tutor: {e}")
                self.next_agent = None
            self.on_enter_state()

        # Ensure next_agent is valid before returning
        if not self.next_agent:
            logging.error("No valid next agent was found. Setting to 'tutor' as fallback.")
            try:
                self.next_agent = self.agents[self.AgentKeys.TUTOR.value]
            except KeyError as e:
                logging.error(f"Fallback agent also not found: {e}")
                self.next_agent = None

        return self.next_agent


    def register_groupchat_manager(self, groupchat_manager):
        self.groupchat_manager = groupchat_manager
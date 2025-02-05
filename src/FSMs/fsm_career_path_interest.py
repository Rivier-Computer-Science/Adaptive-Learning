import os
import json
import autogen
from transitions import Machine
from src.Agents.group_chat_manager_agent import CustomGroupChatManager
from src.UI.reactive_chat import ReactiveChat
import src.UI.avatar as avatar
import logging

# Define the script directory and progress file path for chat persistence
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, "../../progress.json")

avatars = {
    "SurveyGenerationAgent": "📜",
    "AdaptiveQuestioningAgent": "🔍",
    "AICareerMatchingAgent": "🎯",
    "AutogenDataRetrievalAgent": "📊",
    "PerformanceTrendAnalysisAgent": "📈",
    "AutogenCareerGenerationAgent": "🛠️",
    "AIVisualizationAgent": "🎨",
}

# Define the base Autogen Agent class
class MyConversableAgent(autogen.ConversableAgent):
    def __init__(self, name):
        super().__init__(name=name)
        self.groupchat_manager = None  # Ensure it is initialized
        self.reactive_chat_career = None  # Initialize reactive chat reference

    def process(self, input_text):
        raise NotImplementedError("Subclasses must implement this method.")

    def autogen_reply_func(self, input_text):
        """Handles agent response logic."""
        if self.groupchat_manager is None:
            raise RuntimeError(f"{self.name} has no groupchat manager assigned.")
        return f"{self.name} received: {input_text}"

# Define AI Agent Classes
class SurveyGenerationAgent(MyConversableAgent):
    def __init__(self):
        super().__init__(name="SurveyGenerationAgent")

class AdaptiveQuestioningAgent(MyConversableAgent):
    def __init__(self):
        super().__init__(name="AdaptiveQuestioningAgent")

class AICareerMatchingAgent(MyConversableAgent):
    def __init__(self):
        super().__init__(name="AICareerMatchingAgent")

class AutogenDataRetrievalAgent(MyConversableAgent):
    def __init__(self):
        super().__init__(name="AutogenDataRetrievalAgent")

class PerformanceTrendAnalysisAgent(MyConversableAgent):
    def __init__(self):
        super().__init__(name="PerformanceTrendAnalysisAgent")

class AutogenCareerGenerationAgent(MyConversableAgent):
    def __init__(self):
        super().__init__(name="AutogenCareerGenerationAgent")

class AIVisualizationAgent(MyConversableAgent):
    def __init__(self):
        super().__init__(name="AIVisualizationAgent")

# Instantiate AI Agents
agents_dict = {
    "SurveyGenerationAgent": SurveyGenerationAgent(),
    "AdaptiveQuestioningAgent": AdaptiveQuestioningAgent(),
    "AICareerMatchingAgent": AICareerMatchingAgent(),
    "AutogenDataRetrievalAgent": AutogenDataRetrievalAgent(),
    "PerformanceTrendAnalysisAgent": PerformanceTrendAnalysisAgent(),
    "AutogenCareerGenerationAgent": AutogenCareerGenerationAgent(),
    "AIVisualizationAgent": AIVisualizationAgent(),
}

# Finite State Machine (FSM) for managing career path transitions
class CareerFSM:
    states = ["start", "survey", "data_retrieval", "analysis", "career_matching", 
              "refinement", "visualization", "final"]

    def __init__(self, agents_dict):
        self.machine = Machine(model=self, states=CareerFSM.states, initial="start")

        # Define transitions
        self.machine.add_transition("begin_survey", "start", "survey")
        self.machine.add_transition("retrieve_data", "survey", "data_retrieval")
        self.machine.add_transition("analyze", "data_retrieval", "analysis")
        self.machine.add_transition("match_careers", "analysis", "career_matching")
        self.machine.add_transition("refine", "career_matching", "refinement")
        self.machine.add_transition("visualize", "refinement", "visualization")
        self.machine.add_transition("complete", "visualization", "final")

        self.agents_dict = agents_dict
        self.current_speaker_index = 0
        self.agent_names = list(agents_dict.keys())

    def next_speaker_selector(self):
        """Selects the next agent in the conversation cycle."""
        next_speaker = self.agent_names[self.current_speaker_index]
        self.current_speaker_index = (self.current_speaker_index + 1) % len(self.agent_names)
        return self.agents_dict[next_speaker]

# Initialize FSM
fsm = CareerFSM(agents_dict)




class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, groupchat, filename="chat_history.json", *args, **kwargs):
        super().__init__(groupchat=groupchat, *args, **kwargs)
        self.filename = filename  # Fix: Store filename correctly
        self.chat_interface = None  # UI panel reference

    def get_messages_from_json(self):
        """Load previous chat messages from a JSON file."""
        filename = self.filename  # Fix: Use `self.filename` inside the method
        try:
            print(f"Loading JSON file: {filename}")
            with open(filename, "r") as f:
                messages = json.load(f)
                if messages:
                    # Remove termination message if it exists
                    if messages[-1].get("content", "") == globals.IS_TERMINATION_MSG:
                        messages.pop()
                    # Append messages to the group chat
                    for msg in messages:
                        self.groupchat.append(message=msg, speaker=agents_dict_by_name[msg['name']])
                return messages
        except FileNotFoundError:
            print("No previous chat history found. Starting fresh.")
            return []

    def save_messages_to_json(self):
        """Save current chat messages to a JSON file."""
        filename = self.filename  # Fix: Move `self.filename` inside the method

        if not self.groupchat.messages:
            print("No messages to save. Skipping chat history update.")
            return

        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted existing chat history file: {filename}")

        chat_history = self.groupchat.messages
        with open(filename, "w") as f:
            json.dump(chat_history, f, indent=4)
        print(f"Chat history saved to: {filename}")

    def get_chat_history_and_initialize_chat(self, chat_interface=None):
        """Retrieve and display chat history in the UI."""
        chat_history_messages = self.get_messages_from_json()

        if chat_interface:
            if chat_history_messages:
                for message in chat_history_messages:
                    if globals.IS_TERMINATION_MSG not in message:
                        chat_interface.send(
                            message["content"],
                            user=message["role"],
                            avatar=avatars.get(message["role"], None),
                            respond=False
                        )
                chat_interface.send("Chat history restored!", user="System", respond=False)
            else:
                chat_interface.send("Welcome! Ready to assist with career guidance.", user="System", respond=False)

class CustomGroupChat(autogen.GroupChat):
    def __init__(self, agents, messages, max_round, send_introductions, speaker_selection_method):
        super().__init__(
            agents=agents, 
            messages=messages, 
            max_round=max_round,
            send_introductions=send_introductions,
            speaker_selection_method=speaker_selection_method
        )

    def get_messages(self):
        """Return stored messages for chat history."""
        return self.messages  # Fix: Return built-in stored messages

# Initialize Group Chat
groupchat = CustomGroupChat(
    agents=list(agents_dict.values()), 
    messages=[],
    max_round=10,  # Customize max conversation rounds
    send_introductions=True,
    speaker_selection_method=fsm.next_speaker_selector
)

# Initialize Group Chat Manager with history support
manager = CustomGroupChatManager(
    groupchat=groupchat,  
    filename=progress_file_path,
    is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0
)

# Initialize the `reactive_chat_career` UI for career-related discussions
reactive_chat_career = ReactiveChat(groupchat_manager=manager)

# Assign group chat manager and reactive chat UI to agents
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat_career = reactive_chat_career
    agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

# Load and display chat history at startup
manager.get_chat_history_and_initialize_chat(chat_interface=reactive_chat_career.learn_tab_interface)

# Update the UI dashboard
reactive_chat_career.update_dashboard()


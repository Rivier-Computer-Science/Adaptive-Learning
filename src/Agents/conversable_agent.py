import autogen
import asyncio
import json
import os
from datetime import datetime
from src import globals
from src.Models.llm_config import gpt3_config

llm = gpt3_config

try:
    from .base_agent import MyBaseAgent
except ImportError:
    class MyBaseAgent:
        pass  # Define the base class or add necessary methods/attributes

class MyConversableAgent(autogen.ConversableAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        llm_config = kwargs.get('llm_config', None)
        if llm_config is None:
            kwargs['llm_config'] = llm

        is_termination_msg = kwargs.get('is_termination_msg', None)
        human_input_mode = kwargs.get('human_input_mode', None)
        if is_termination_msg is None and human_input_mode == 'ALWAYS':
            kwargs['is_termination_msg'] = lambda x: x.get("content", "").rstrip().endswith("exit")

        code_execution_config = kwargs.get('code_execution_config', None)
        if code_execution_config is None:
            kwargs['code_execution_config'] = False

        super().__init__(**kwargs)

        self._chat_interface = None  # Initialize the private variable
        self._chat_messages = {}

    async def a_get_human_input(self, prompt: str) -> str:
        self.chat_interface.send(prompt, user="System", respond=False)

        if globals.input_future is None or globals.input_future.done():
            globals.input_future = asyncio.Future()

        await globals.input_future

        input_value = globals.input_future.result()
        globals.input_future = None

        if input_value.rstrip().endswith("exit"):
            print("Exit message detected. Saving progress...")
            self.save_progress()

        return input_value

    def save_progress(self):
        print("Saving chat history to progress.json...")
        serializable_chat_messages = []

        # Only extract the message content and metadata for saving
        for messages in self._chat_messages.values():
            for message in messages:
                message['timestamp'] = datetime.now().isoformat()  # Add timestamp
                serializable_chat_messages.append(message)

        print(f"Serializable chat messages: {serializable_chat_messages}")  # Debug: Print the messages to be saved

        progress_file_path = os.path.join(os.path.dirname(__file__), '../../progress.json')

        try:
            with open(progress_file_path, 'r') as f:
                existing_messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_messages = []

        existing_message_contents = {msg['content'] for msg in existing_messages}
        new_messages = [msg for msg in serializable_chat_messages if msg['content'] not in existing_message_contents]

        combined_messages = existing_messages + new_messages

        with open(progress_file_path, 'w') as f:
            json.dump(combined_messages, f)

        print(f"Progress saved. Total messages in file: {len(combined_messages)}")

    def get_progress(self):
        print("Loading chat history from progress.json...")
        progress_file_path = os.path.join(os.path.dirname(__file__), '../../progress.json')
        try:
            with open(progress_file_path, 'r') as f:
                loaded_messages = json.load(f)
                self._chat_messages = {self: loaded_messages}
        except FileNotFoundError:
            print("progress.json not found. Starting new session.")
            self._chat_messages = {self: []}
        except json.JSONDecodeError:
            print("Error decoding JSON from progress.json. Starting new session.")
            self._chat_messages = {self: []}

    @property
    def chat_interface(self):
        return self._chat_interface
    
    @chat_interface.setter
    def chat_interface(self, chat_interface):
        self._chat_interface = chat_interface
        self.get_progress()  # Ensure progress is loaded when chat interface is set

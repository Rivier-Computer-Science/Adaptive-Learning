####################################################################
# Conversable Agents
##################################################################### 
import autogen
import asyncio
from src import globals
from src.Models.llm_config import gpt3_config, gpt4_config

from .base_agent import MyBaseAgent

llm = gpt3_config

class MyConversableAgent(autogen.ConversableAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        llm_config = kwargs.get('llm_config', None)
        if llm_config is None:
             kwargs['llm_config'] = llm

        is_termination_msg = kwargs.get('is_termination_msg', None)
        human_input_mode = kwargs.get('human_input_mode', None)
        if is_termination_msg is None and human_input_mode == 'ALWAYS':
             kwargs['is_termination_msg'] = self.check_exit_message

        code_execution_config = kwargs.get('code_execution_config', None)
        if code_execution_config is None:
             kwargs['code_execution_config'] = False

        super().__init__(**kwargs)

        self.chat_interface = None
    
    def check_exit_message(self, message):
        if message.get("content", "").rstrip().endswith("exit"):
            self.save_progress()
            return True
        return False

    def save_progress(self, filename='progress.json'):
        with open(filename, 'w') as f:
            json.dump(self.chat_messages, f)
    
    def get_progress(self, filename='progress.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.chat_messages = json.load(f)

    async def a_get_human_input(self, prompt: str) -> str:
        self.chat_interface.send(prompt, user="System", respond=False) 

        if globals.input_future is None or globals.input_future.done():
            globals.input_future = asyncio.Future()

        await globals.input_future

        input_value = globals.input_future.result()
        globals.input_future = None
        return input_value

    @property
    def chat_interface(self):
        return self._chat_interface
    
    @chat_interface.setter
    def chat_interface(self, chat_interface):
        self._chat_interface = chat_interface
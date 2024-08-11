####################################################################
# Conversable Agents
##################################################################### 
import autogen
import asyncio
from src import globals
from src.Models.llm_config import gpt3_config, gpt4_config

from .base_agent import MyBaseAgent

llm = gpt4_config

class MyConversableAgent(autogen.ConversableAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        llm_config = kwargs.get('llm_config', None)
        if llm_config is None:
             kwargs['llm_config'] = llm

        #is_termination_msg = kwargs.get('is_termination_msg', None)
        # human_input_mode = kwargs.get('human_input_mode', None)
        # if is_termination_msg is None and human_input_mode == 'ALWAYS':
        #      kwargs['is_termination_msg'] = is_termination_msg=lambda x: x.get("content", "").strip() == globals.IS_TERMINATION_MSG

        code_execution_config = kwargs.get('code_execution_config', None)
        if code_execution_config is None:
             kwargs['code_execution_config'] = False

        super().__init__(**kwargs)

        #self.response_event = asyncio.Event()  # Add an event object
        self.chat_interface = None
        self.group_chat_manager = None
 
    async def a_get_human_input(self, prompt: str) -> str:
                self.chat_interface.send(prompt, user="System", respond=False) 

                if globals.input_future is None or globals.input_future.done():
                    globals.input_future = asyncio.Future()

                await globals.input_future

                input_value = globals.input_future.result()
                globals.input_future = None
                return input_value

    async def a_receive(self, message, sender=None, request_reply=True, silent=False):
        # Process the incoming message
        await super().a_receive(message, sender, request_reply, silent)

        # Check for the termination string
        print("************* message *************** Receiver: ", self.name, '  ', message)
        if isinstance(message, str):
            message = {"content": message}
            if message.get("content", "").strip() == "TERMINATE":
                self.handle_termination()

    def handle_termination(self):
        if self.group_chat_manager:
            # Notify the GroupChatManager to save the chat history
            self.group_chat_manager.save_chat_history()
            print("Termination detected. Chat history saved.")
        else:
            print("GroupChatManager not available to save chat history.")



    @property
    def chat_interface(self):
        return self._chat_interface
    
    @chat_interface.setter
    def chat_interface(self, chat_interface):
        self._chat_interface = chat_interface

    @property
    def group_chat_manager(self):
        return self._group_chat_manager
    
    @chat_interface.setter
    def group_chat_manager(self, group_chat_manager):
        self._group_chat_manager = group_chat_manager
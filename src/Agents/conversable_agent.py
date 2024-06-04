####################################################################
# Conversable Agents
##################################################################### 
import autogen
import asyncio
from src import globals

from .base_agent import MyBaseAgent

class MyConversableAgent(autogen.ConversableAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.response_event = asyncio.Event()  # Add an event object
        self.description = self.system_message
        self.chat_interface = None
 
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
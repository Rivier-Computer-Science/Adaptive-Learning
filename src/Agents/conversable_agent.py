import autogen
import asyncio
import json
import os
from datetime import datetime
from src import globals
from src.Models.llm_config import gpt3_config
from src.Agents.base_agent import MyBaseAgent

llm = gpt3_config


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

        # if input_value.rstrip().endswith("exit"):
        #     print("Exit message detected. Saving progress...")
        #     self.save_progress()

        return input_value

    @property
    def chat_interface(self):
        return self._chat_interface
    
    @chat_interface.setter
    def chat_interface(self, chat_interface):
        self._chat_interface = chat_interface
 
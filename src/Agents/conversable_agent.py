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
         #is_termination_msg = kwargs.get('is_termination_msg', None)
        # human_input_mode = kwargs.get('human_input_mode', None)
        # if is_termination_msg is None and human_input_mode == 'ALWAYS':
        #      kwargs['is_termination_msg'] = is_termination_msg=lambda x: x.get("content", "").strip() == globals.IS_TERMINATION_MSG
       
        super().__init__(
            llm_config=kwargs.pop('llm_config', llm),
            code_execution_config = kwargs.pop('code_execution_config', False),
            **kwargs)

        self.groupchat_manager = None
        self.reactive_chat = None
 
    async def a_get_human_input(self, prompt: str) -> str:
        self.groupchat_manager.chat_interface.send(prompt, user="System", respond=False) 

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
        #print("************* message *************** Receiver: ", self.name, '  ', message)
        if isinstance(message, str):
            message = {"content": message}
            if message.get("content", "").strip() == "TERMINATE":
                self.handle_termination()

    def handle_termination(self):
        if self.groupchat_manager:
            # Notify the GroupChatManager to save the chat history
            self.groupchat_manager.save_chat_history()
            print("Termination detected. Chat history saved.")
        else:
            print("GroupChatManager not available to save chat history.")

    def autogen_reply_func(self, recipient, messages, sender, config):
        print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

        last_content = messages[-1]['content']        

        ###############################
        # Update panel tabs
        #############################
        self.reactive_chat.update_learn_tab(recipient=recipient, messages=messages, sender=sender, config=config)
        self.reactive_chat.update_dashboard()                          
        self.reactive_chat.update_progress(contents=last_content,user=recipient.name)        
        #Note: do not call update_model_tab. The button takes care of that.

                
        return False, None

    @property
    def groupchat_manager(self):
        return self._group_chat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, group_chat_manager):
        self._group_chat_manager = group_chat_manager



     
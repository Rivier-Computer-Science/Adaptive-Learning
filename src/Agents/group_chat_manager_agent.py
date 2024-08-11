import autogen
import asyncio
import json
import os
from typing import Optional, List, Dict
from src import globals



class CustomGroupChat(autogen.GroupChat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)


class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, groupchat, filename="chat_history.json", *args, **kwargs):
        super().__init__(groupchat=groupchat, *args, **kwargs)
        
        # Re-register the reply to use the overridden method.
        # Autogen register GroupChatManager.a_run_chat
        self.register_reply(
            autogen.Agent,
            self.a_run_chat,  # Use self.a_run_chat to refer to the overridden method
            config=self._groupchat,
            reset_config=autogen.GroupChat.reset,
            ignore_async_in_sync_chat=True,
        )

        self.filename = filename

    async def a_run_chat(self, *args, **kwargs):
        try: 
            await super().a_run_chat(**kwargs)
            self.save_messages_to_json(self.filename)
        except Exception as e:
            print(f"Exception occurred: {e}") 

        return True, None
            

    def get_messages_from_json(self, filename=None):
        if filename is None:
            filename = self.filename
        try:
            print('Getting JSON file:', filename)
            with open(filename, "r") as f:
                return self.messages_from_string(f.read())
        except FileNotFoundError:
            print("No previous chat history found. Starting a new conversation.")
            return []  # Return an empty list

    
    def save_messages_to_json(self, filename=None):
        if filename is None:
            filename = self.filename
        
        # Get previous history
        old_messages = self.get_messages_from_json(filename)
        
        # Check if the file exists and delete it
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted existing file: {filename}")

        # Save the chat history to the file
        chat_history = old_messages + self.groupchat.messages  # merge the lists
        with open(filename, 'w') as f:
            json.dump(chat_history, f, indent=4)
        print(f"Chat history saved to: {filename}")


 
    async def delayed_initiate_chat(self, agent, recipient, message):
        globals.initiate_chat_task_created = True
        await asyncio.sleep(1) 
        await agent.a_initiate_chat(recipient, message=message)
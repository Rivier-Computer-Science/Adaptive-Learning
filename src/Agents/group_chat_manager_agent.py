import autogen
import asyncio
import json
from src import globals


class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, termination_string="exit", filename="chat_history.json", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.termination_string = termination_string
        self.filename = filename
    

    def get_messages_from_json(self):
        try:
            with open(self.filename, "r") as f:
                chat_history_string = f.read()
                return self.messages_from_string(chat_history_string)
                # self.resume(chat_history_string)  # Resume the chat using the saved history
                # print("Resuming chat from previous session...")
        except FileNotFoundError:
            print("No previous chat history found. Starting a new conversation.")


    def on_new_message(self, messages):
        latest_message = messages[-1]['content']  
        if self.termination_string in latest_message:
            chat_history_string = self.messages_to_string(messages)  
            self._save_chat_to_file(chat_history_string) 

    def _save_chat_to_file(self, chat_string):
        with open(self.filename, "w") as f:
            json.dump(chat_string, f, indent=4)

    def run(self, *args, **kwargs):
        try:
            super().run(*args, **kwargs)  # Call the original run method
        except Exception as e:
            print(f"Exception occurred: {e}") 
            # Log the error, send a message to users, etc.

    async def delayed_initiate_chat(self, agent, recipient, message):
        globals.initiate_chat_task_created = True
        await asyncio.sleep(1) 
        await agent.a_initiate_chat(recipient, message=message)
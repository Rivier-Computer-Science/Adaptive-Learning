import autogen
import asyncio
import json
from typing import List, Dict
from src import globals

class CustomGroupChat(autogen.GroupChat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, filename="chat_history.json", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    async def a_run_chat(self, *args, **kwargs):
        try: 
            print('******************** Entering run_chat *************')
            messages = kwargs.get('messages', None)
            if messages:
                latest_message = messages[-1]['content']
                if 'save progress' in latest_message.lower():
                    print("saving json file")
                    with open(self.filename, "w") as f:
                        json.dump(self.messages_to_string(messages), f, indent=4)
            super().run_chat(*args, **kwargs)  
        except Exception as e:
            print(f"Exception occurred: {e}")

    def get_messages_from_json(self):
        try:
            print('getting json file: ', self.filename)
            with open(self.filename, "r") as f:
                return self.messages_from_string(f.read())
        except FileNotFoundError:
            print("No previous chat history found. Starting a new conversation.")
            return []

    def messages_from_string(self, data: str) -> List[Dict]:
        """
        Convert JSON string to a list of messages.
        """
        try:
            messages = json.loads(data)
            # Assuming messages are in the format [{'content': 'message content', 'role': 'user/agent'}]
            return messages
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []

    def resume(self, messages: List[Dict], end_marker: str):
        """
        Resume the chat history based on the provided messages.
        """
        for message in messages:
            if message.get('content') == end_marker:
                break
            # This example assumes you have a method to send or handle the messages
            print(f"Resuming message: {message['content']}")

    async def delayed_initiate_chat(self, agent, recipient, message):
        globals.initiate_chat_task_created = True
        await asyncio.sleep(1) 
        await agent.a_initiate_chat(recipient, message=message)

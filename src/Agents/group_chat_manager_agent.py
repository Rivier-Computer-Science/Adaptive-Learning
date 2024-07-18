import autogen
import asyncio
import json
from src import globals



class CustomGroupChat(autogen.GroupChat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)


class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, filename="chat_history.json", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    async def a_run_chat(self, *args, **kwargs):
        # FIXME - once super is called, no messages will be passed.
        try: 
            print('******************** Entering run_chat *************')
            messages = kwargs.get('messages', None)
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
        except FileNotFoundError: #FIXME
            print("No previous chat history found. Starting a new conversation.")

 
    async def delayed_initiate_chat(self, agent, recipient, message):
        globals.initiate_chat_task_created = True
        await asyncio.sleep(1) 
        await agent.a_initiate_chat(recipient, message=message)
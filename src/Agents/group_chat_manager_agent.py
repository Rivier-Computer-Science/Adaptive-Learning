import autogen
import asyncio
from src import globals


class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  

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
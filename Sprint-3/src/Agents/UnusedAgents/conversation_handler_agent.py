from autogen import Agent, Task, ProtobufModel
from typing import List

class ConversationHistory(ProtobufModel):
    messages: List[str] = []
 
class ConversationHandlerAgent(Agent):
    def __init__(self, gpt_agent, message_queue):
        self.gpt_agent = gpt_agent
        self.message_queue = message_queue
        self.convo_history = ConversationHistory()
        self.latest_response = None

    @Task
    async def handle_user_input(self, new_message: str):
        self.convo_history.messages.append(new_message)
        gpt_prompt = '\n'.join(self.convo_history.messages)
        gpt_response = await self.gpt_agent.generate_response(gpt_prompt)
        self.convo_history.messages.append(gpt_response)
        return gpt_response  # Update UI with the response


    @Task
    async def listen_for_messages(self):
        while True:
            new_message = self.message_queue.get()  # Wait for new messages 
            response = await self.handle_user_input(new_message)
            self.latest_response = response
           
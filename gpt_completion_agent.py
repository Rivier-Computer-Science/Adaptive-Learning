import os
from autogen import Agent

from abc import ABC, abstractmethod

class LLMAgent(Agent, ABC):
    @abstractmethod
    async def generate_response(self, prompt: str):
        pass    



class GPT3Agent(LLMAgent):
    def __init__(self, api_key,):
         self.openai_client = os.environ.get("OPENAI_API_KEY")
         self.chat_completion = None

    async def generate_response(self, prompt: str):
        self.chat_completion = self.openai_client.chat.completions.create(
            messages=[
            {
                "role": "user",
                "content": prompt,
            }
            ],
            model="gpt-3.5-turbo",
        )
        return self.chat_completion.choices[0].message.content
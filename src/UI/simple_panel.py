import autogen
import os
import asyncio
import panel as pn

os.environ["AUTOGEN_USE_DOCKER"] = "False"


config_list = [
    {
        'model': "gpt-3.5-turbo",
    }
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}

class TutorAgent(autogen.ConversableAgent):
    def __init__(self, chat_interface):
        self.chat_interface=chat_interface
        super().__init__(
            name="Tutor",
            system_message="You are an algebra tutor. Your goal is to help the student learn algebra concepts and solve problems step-by-step.",
            llm_config=gpt4_config
        )

class StudentAgent(autogen.UserProxyAgent):
    def __init__(self):
        super().__init__(
            name="Student",
            system_message="You are a student learning algebra. You will ask the tutor questions and work through problems with their help."
        )

# Callback function (Send user message to manager's group chat)
async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    await manager.groupchat.a_send(
        {"role": "user", "content": contents}, 
        sender=student
    )
    return False, None


# Create agents
chat_interface = pn.chat.ChatInterface(callback=callback)
tutor = TutorAgent(chat_interface=chat_interface)
student = StudentAgent()

# Create the GroupChat with agents and a manager
groupchat = autogen.GroupChat(agents=[tutor, student], messages=[])
manager = autogen.GroupChatManager(groupchat=groupchat)

# Register the reply functions for each agent
tutor.register_reply([autogen.Agent, None], reply_func=lambda recipient, messages, sender, config: recipient.chat_interface.send(
            messages[-1]["content"], user=sender.name
        ))


# Start the chat interface
chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()  # Show the GUI

# Create the initial chat task
asyncio.create_task(student.initiate_chat(tutor, message="Hi, can you help me with solving equations?"))


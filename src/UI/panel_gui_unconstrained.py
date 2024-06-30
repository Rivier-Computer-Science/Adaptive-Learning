import autogen
import panel as pn
import openai
import os
import time
import asyncio
from typing import List, Dict
import logging
import json
from src import globals
from src.Agents.agents import *
from src.UI.avatar import avatar

# Determine the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Define the path to the progress.json file relative to the script location
progress_file_path = os.path.join(script_dir, '../../progress.json')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

globals.input_future = None

agents = list(agents_dict.values())  # All agents

groupchat = autogen.GroupChat(agents=agents,
                              messages=[],
                              max_round=40,
                              send_introductions=True,
                              )

manager = CustomGroupChatManager(groupchat=groupchat)

# Load chat history from progress.json if it exists
if os.path.exists(progress_file_path):
    try:
        with open(progress_file_path, 'r') as f:
            chat_history = json.load(f)
        print(f"Loaded chat history from {progress_file_path}")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {progress_file_path}: {e}")
        chat_history = []
else:
    print(f"File '{progress_file_path}' not found.")
    chat_history = []

def create_app():
    pn.extension(design="material")

    async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
        if not globals.initiate_chat_task_created:
            asyncio.create_task(manager.delayed_initiate_chat(tutor, manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")

    chat_interface = pn.chat.ChatInterface(callback=callback)

    def print_messages(recipient, messages, sender, config):
        print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

        content = messages[-1]['content']

        if all(key in messages[-1] for key in ['name']):
            chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)

        return False, None  # required to ensure the agent communication flow continues

    # Register chat interface with ConversableAgent
    for agent in groupchat.agents:
        agent.chat_interface = chat_interface
        agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

    # Create the Panel app object with the chat interface
    app = pn.template.BootstrapTemplate(title=globals.APP_NAME)
    app.main.append(
        pn.Column(
            chat_interface
        )
    )
    chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="System", respond=False)

    # Send previous chat history
    for message in chat_history:
        if 'name' in message and 'role' in message:
            chat_interface.send(message['content'], user=message['name'], avatar=avatar[message['name']], respond=False)
        else:
            chat_interface.send(message['content'], user="System", respond=False)

    return app

if __name__ == "__main__":
    app = create_app()
    pn.serve(app)

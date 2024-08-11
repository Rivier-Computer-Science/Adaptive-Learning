import autogen
import panel as pn
import openai
import os
import time
import asyncio
from typing import List, Dict
import logging
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.avatar import avatar

# logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

globals.input_future = None
    
fsm = FSM(agents_dict)

# Create the GroupChat with agents and a manager
groupchat = CustomGroupChat(agents=list(agents_dict.values()), 
                              messages=[],
                              max_round=50,
                              send_introductions=True,
                              speaker_selection_method=fsm.next_speaker_selector
                              )


# default is_termination_msg is autogen is TERMINATE
# is_termination_msg=lambda x: x.get("content", "").strip() == globals.IS_TERMINATION_MSG
manager = CustomGroupChatManager(groupchat=groupchat,
                                filename=progress_file_path)    


# --- Panel Interface ---
def create_app():
    # --- Panel Interface ---
    pn.extension(design="material")


    async def panel_callback(contents: str, user: str, instance: pn.chat.ChatInterface):
        if not globals.initiate_chat_task_created:
            asyncio.create_task(manager.delayed_initiate_chat(tutor, manager, contents))  
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")


    chat_interface = pn.chat.ChatInterface(callback=panel_callback)

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
        agent.group_chat_manager = manager
        agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

    # Create the Panel app object with the chat interface
    app = pn.template.BootstrapTemplate(title=globals.APP_NAME)
    app.main.append(
        pn.Column(
            chat_interface
        )
    )

    #Load chat history on startup and echo it to the panel screen
    chat_history_messages = manager.get_messages_from_json()
    if chat_history_messages:
        manager.resume(chat_history_messages, globals.IS_TERMINATION_MSG)
        for message in chat_history_messages:
            if globals.IS_TERMINATION_MSG not in message:
                chat_interface.send(
                    message["content"],
                    user=message["role"], 
                    avatar=avatar.get(message["role"], None),  
                    respond=False
                )
        chat_interface.send("Time to continue your studies!", user="System", respond=False)
    else:
        chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="System", respond=False)

    
    return app


if __name__ == "__main__":
    app = create_app()
    #pn.serve(app, debug=True)
    pn.serve(app)
 
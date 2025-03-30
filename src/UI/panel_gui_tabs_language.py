from dotenv import load_dotenv
load_dotenv()

import autogen
import panel as pn
import openai
import os
import time
import asyncio
from typing import List, Dict
import logging
from src import globals as globals
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.avatar import avatar

# Language specific
from src.Agents.language_agents import create_agents
from src.UI.reactive_chat24_language import ReactiveChat
from src.FSMs.fsm_language import TeachMeFSM

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(module)s - %(filename)s - %(funcName)s - line %(lineno)d - %(asctime)s - %(name)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

##############################################
# Main Adaptive Learning Application
############################################## 
globals.input_future = None
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

# Function to prompt the user for the desired language
def get_user_language():
    # In a real application, this could be a GUI input or command-line prompt
    # For now, we'll simulate it with a simple input (you can modify this as needed)
    print("Please enter the language you want to learn (e.g., Telugu, Spanish, French):")
    language = input().strip().capitalize()
    return language if language else "Telugu"  # Default to Telugu if no input

# Get the user's desired language
language = get_user_language()

# Create agents for the specified language
agents_dict, avatars = create_agents(language)

fsm = TeachMeFSM(agents_dict)

groupchat = CustomGroupChat(agents=list(agents_dict.values()), 
                            messages=[],
                            max_round=globals.MAX_ROUNDS,
                            send_introductions=True,
                            speaker_selection_method=fsm.next_speaker_selector)

manager = CustomGroupChatManager(groupchat=groupchat,
                                 filename=progress_file_path)

# Allow the fsm to get the groupchat history
fsm.register_groupchat_manager(manager)
logging.debug("panel_gui_tabs_language: fsm registered groupchat_manager")

# Begin GUI components
reactive_chat = ReactiveChat(agents_dict=agents_dict, avatars=avatars, 
                             groupchat_manager=manager)

# Register groupchat_manager and reactive_chat gui interface with ConversableAgents
# Register autogen reply function
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

# Load chat history on startup
manager.get_chat_history_and_initialize_chat(
    initial_message=f"Welcome to the {language} Teacher! How can I help you today?",
    avatars=avatars,
    filename=progress_file_path, 
    chat_interface=reactive_chat.learn_tab_interface) 

logging.info("panel_gui_tabs_language: manager.get_chat_history_and_initialize_chat completed")

reactive_chat.update_dashboard()    # Call after history loaded
logging.info("panel_gui_tabs_language: reactive_chat.update_dashboard() completed")

# --- Panel Interface ---
def create_app():    
    return reactive_chat.draw_view()

if __name__ == "__main__":    
    app = create_app()
    try:
        pn.serve(app, callback_exception='verbose')
    except Exception as e:
        logging.exception(f"EXCEPTION in main {e}")
        raise
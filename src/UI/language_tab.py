
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

pn.extension()
os.environ["AUTOGEN_USE_DOCKER"] = "False"

##############################################
# Main Adaptive Learning Application
############################################## 
globals.input_future = None
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

# Supported languages
supported_languages = ["Telugu", "Spanish", "French", "German", "Hindi", "Tamil", "Arabic", "Japanese", "Korean", "Italian", "Chinese"]

# Panel dropdown widget for language selection
language_input = pn.widgets.Select(
    name="Select Language",
    options=supported_languages,
    value="Telugu"
)

submit_button = pn.widgets.Button(name="Start Learning", button_type="primary")
chat_panel = pn.Column()

def start_language_learning(event):
    language = language_input.value.strip().capitalize() or "Telugu"

    agents_dict, avatars = create_agents(language)
    fsm = TeachMeFSM(agents_dict)

    groupchat = CustomGroupChat(
        agents=list(agents_dict.values()), 
        messages=[],
        max_round=globals.MAX_ROUNDS,
        send_introductions=True,
        speaker_selection_method=fsm.next_speaker_selector
    )

    manager = CustomGroupChatManager(
        groupchat=groupchat,
        filename=progress_file_path
    )

    fsm.register_groupchat_manager(manager)

    reactive_chat = ReactiveChat(agents_dict=agents_dict, avatars=avatars, groupchat_manager=manager)

    for agent in groupchat.agents:
        agent.groupchat_manager = manager
        agent.reactive_chat = reactive_chat
        agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

    manager.get_chat_history_and_initialize_chat(
        initial_message=f"Welcome to the {language} Teacher! How can I help you today?",
        avatars=avatars,
        filename=progress_file_path, 
        chat_interface=reactive_chat.learn_tab_interface
    )

    reactive_chat.update_dashboard()

    chat_panel.clear()
    chat_panel.append(reactive_chat.draw_view())

submit_button.on_click(start_language_learning)

# --- Panel Interface ---
def create_app():
    return pn.Column(
        pn.pane.Markdown("## 🌐 Language Learning"),
        language_input,
        submit_button,
        chat_panel
    )

if __name__ == "__main__":    
    app = create_app()
    try:
        pn.serve(app, callback_exception='verbose')
    except Exception as e:
        logging.exception(f"EXCEPTION in main {e}")
        raise


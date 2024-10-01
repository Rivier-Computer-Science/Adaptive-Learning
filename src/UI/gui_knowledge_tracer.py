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
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.Agents import gui_knowledge_tracer_fsms as fsm
from src.UI.reactive_chat import ReactiveChat
from src.UI.avatar import avatar
# Disable Docker for AutoGen
os.environ["AUTOGEN_USE_DOCKER"] = "False"
# Set up file paths
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../graph.json')
globals.input_future = None
# Define the agent dictionary
agents_dict = {
    "student": student,
    "knowledge_tracer": knowledge_tracer,
    "problem_generator": problem_generator,
    "solution_verifier": solution_verifier,
}
# Create FSM for managing agent conversations
fsm = fsm.FSMGraphTracerConsole(agents_dict)
# Create GroupChat for agents
groupchat = CustomGroupChat(
    agents=list(agents_dict.values()), 
    messages=[],
    max_round=globals.MAX_ROUNDS,
    send_introductions=True,
    speaker_selection_method=fsm.next_speaker_selector
)
# Create GroupChatManager for managing chat history and interactions
manager = CustomGroupChatManager(
    groupchat=groupchat,
    filename=progress_file_path, 
    is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0
)
# Begin GUI components (Reactive Chat)
reactive_chat = ReactiveChat(groupchat_manager=manager)
# Register groupchat_manager and reactive_chat GUI interface with ConversableAgents
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})
# Load chat history on startup
manager.get_chat_history_and_initialize_chat(
    filename=progress_file_path, 
    chat_interface=reactive_chat.learn_tab_interface
)
reactive_chat.update_dashboard()  # Call after history is loaded
# Function to create and serve the GUI application
def create_app():
    return reactive_chat.draw_view()
if __name__ == "__main__":
    # Serve the application with the GUI components
    app = create_app()
    pn.serve(app, callback_exception='verbose')
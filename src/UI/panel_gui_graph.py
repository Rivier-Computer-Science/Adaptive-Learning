import autogen
import panel as pn
import openai
import os
import time
import asyncio
from typing import List, Dict
import logging
from src import globals
import src.Agents.agents as agents
#from src.Agents.agents import *
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.Agents import chat_manager_fsms as fsm
from src.UI.reactive_graph_chat import ReactiveGraphChat
from src.UI.avatar import avatar

# logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../graph.json')

globals.input_future = None
    

graph_agents_dict = {
    "student": agents.student,
    "knowledge_tracer": agents.knowledge_tracer,
    "problem_generator": agents.problem_generator,
    "solution_verifier": agents.solution_verifier,
 }


fsm = fsm.FSMGraphTracerGUI(graph_agents_dict)

groupchat = CustomGroupChat(agents=list(graph_agents_dict.values()), 
                              messages=[],
                              max_round=globals.MAX_ROUNDS,
                              send_introductions=True,
                              speaker_selection_method=fsm.next_speaker_selector
                              )

groupchat_manager = CustomGroupChatManager(groupchat)

reactive_chat = ReactiveGraphChat(groupchat_manager)

# FIXME: This needs to be fixed generically so the UI 
#        Doesn't affect autogen agent callbacks

def autogen_graph_reply_func(recipient, messages, sender, config):
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    last_content = messages[-1]['content']        
    reactive_chat.update_graph_tab(recipient=recipient, messages=messages, sender=sender, config=config)            
    return False, None

for agent in groupchat.agents:
    agent.groupchat_manager = groupchat_manager
    agent.reactive_chat = reactive_chat
    agent.register_reply([autogen.Agent, None], reply_func=autogen_graph_reply_func, config={"callback": None})

fsm.groupchat_manager = groupchat_manager
fsm.reactive_chat = reactive_chat
reactive_chat.graph_tab_interface.send("Time to find out what you know!", user="System", respond=False)

# --- Panel Interface ---
def create_app():    
    return reactive_chat.draw_view()

if __name__ == "__main__":    
    app = create_app()
    #pn.serve(app, debug=True)
    pn.serve(app, callback_exception='verbose')
 
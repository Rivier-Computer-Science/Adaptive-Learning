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
from src.Agents import chat_manager_fsms as fsm
from src.UI.avatar import avatar

# logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../graph.json')

globals.input_future = None
    

agents_dict = {
    "student": student,
    "knowledge_tracer": knowledge_tracer,
    "problem_generator": problem_generator,
    "solution_verifier": solution_verifier,
 }

fsm = fsm.FSMGraphTracerConsole(agents_dict)



if __name__ == "__main__":

#    manager.initiate_chat(student)

    while True:        
        next_agent = fsm.next_speaker_selector()
        if next_agent is None:
            break
 
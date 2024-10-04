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
class KnowledgeTracerAgent(MyConversableAgent):
    description = """
        KnowledgeTracerAgent is a comprehensive and adaptive agent designed to assess and trace the capabilities of a StudentAgent by interacting 
        with various agents within the learning system. 
        KnowledgeTracerAgent gathers data from agents such as ProblemGeneratorAgent, SolutionVerifierAgent, and LearnerModelAgent to build a detailed understanding 
        of the StudentAgent's knowledge and progress. 
        KnowledgeTracerAgent ensures a holistic view of the StudentAgent's capabilities, facilitating informed decisions about their learning path.
    """
    system_message = """
        You are KnowledgeTracerAgent, an agent responsible for assessing and tracing the capabilities of a StudentAgent by interacting with 
        other agents in the learning system. 
        Gather data from ProblemGeneratorAgent, SolutionVerifierAgent, and LearnerModelAgent, and any other relevant agents to build a comprehensive 
        understanding of the StudentAgent's knowledge and progress. 
        Use this information to provide insights into the StudentAgent's strengths and areas for improvement. 
        Your goal is to ensure a holistic view of the StudentAgent's capabilities, supporting informed and personalized learning decisions.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="KnowledgeTracerAgent",
            human_input_mode="NEVER",
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )
# Define the agent dictionary
agents_dict = {
    "student": student,
    "knowledge_tracer": KnowledgeTracerAgent(),
    "problem_generator": problem_generator,
    "solution_verifier": solution_verifier,
}
fsm = fsm.FSMGraphTracerConsole(agents_dict)
# Create GroupChat for agents
groupchat = CustomGroupChat(
    agents=list(agents_dict.values()), 
    messages=[],
    max_round=globals.MAX_ROUNDS,
    send_introductions=True
)
# Create GroupChatManager for managing chat history and interactions
manager = CustomGroupChatManager(
    groupchat=groupchat,
    filename=progress_file_path, 
    is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0
)
fsm.register_groupchat_manager(manager)
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
# panel_gui_state_machine_user_story_12.py
import panel as pn
import pyautogen as autogen  # Ensure this is up-to-date
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

os.environ["AUTOGEN_USE_DOCKER"] = "False"

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

globals.input_future = None

fsm = FSM(agents_dict)

groupchat = CustomGroupChat(agents=list(agents_dict.values()), 
                             messages=[],
                             max_round=30,
                             send_introductions=True,
                             speaker_selection_method=fsm.next_speaker_selector
                             )

manager = CustomGroupChatManager(groupchat=groupchat,
                                 filename=progress_file_path, 
                                 is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0 )    

def create_app():
    # --- Panel Interface Components ---
    
    # Create a text input widget for setting educational targets
    targets_input = pn.widgets.TextInput(name='Set Educational Target', placeholder='Enter your target here...')
    
    # Create a markdown pane to display progress
    progress_display = pn.pane.Markdown("**Progress will be displayed here**")
    
    # Create a button to submit the target
    submit_button = pn.widgets.Button(name='Submit Target', button_type='primary')

    # Define a callback function to update progress display
    def update_progress(event):
        target = targets_input.value
        if target:
            # Placeholder logic to demonstrate progress update
            progress_display.object = f"Tracking progress towards target: '{target}'"
        else:
            progress_display.object = "Please set a target first."

    # Link the button to the callback function
    submit_button.on_click(update_progress)
    
    # Create the main Panel app layout
    app = pn.template.BootstrapTemplate(title="Adaptive Learning System")
    app.main.append(
        pn.Column(
            targets_input,
            submit_button,
            progress_display
        )
    )
    
    return app

# Run the app if this script is executed directly
if __name__ == "__main__":
    app = create_app()
    pn.serve(app)

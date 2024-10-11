import autogen
import panel as pn
import openai
import os
import asyncio
import speech_recognition as sr
from typing import List, Dict
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat16 import ReactiveChat
from src.UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Function to capture and recognize speech
def recognize_speech_from_mic():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        print("Listening for speech...")
        audio = recognizer.listen(source)  # Capture the audio
        
        try:
            print("Recognizing speech...")
            # Using Google Web Speech API (No API key required)
            transcript = recognizer.recognize_google(audio)
            print(f"Transcribed: {transcript}")
            return transcript
        except sr.UnknownValueError:
            print("Google Web Speech could not understand the audio")
            return "Sorry, I didn't catch that."
        except sr.RequestError as e:
            print(f"Error with the Google Web Speech service; {e}")
            return "Error occurred while processing audio."

##############################################
# Main Adaptive Learning Application
##############################################
globals.input_future = None
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

fsm = FSM(agents_dict)

groupchat = CustomGroupChat(agents=list(agents_dict.values()), 
                              messages=[],
                              max_round=globals.MAX_ROUNDS,
                              send_introductions=True,
                              speaker_selection_method=fsm.next_speaker_selector
                              )

manager = CustomGroupChatManager(groupchat=groupchat,
                                filename=progress_file_path, 
                                is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0 )    

# Begin GUI components
reactive_chat = ReactiveChat(groupchat_manager=manager)

# Register groupchat_manager and reactive_chat GUI interface with ConversableAgents
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

# Load chat history on startup
manager.get_chat_history_and_initialize_chat(filename=progress_file_path, chat_interface=reactive_chat.learn_tab_interface)
reactive_chat.update_dashboard()    # Call after history loaded

# --- Speech Capture and Processing ---
def handle_audio_submission(event):
    transcript = recognize_speech_from_mic()
    # Display the transcribed text in the chat interface
    reactive_chat.learn_tab_interface.send(transcript, user="User", avatar="🎤")

# Create app with speech recognition button
def create_app():    
    record_button = pn.widgets.Button(name="Record Audio", button_type="primary")
    record_button.on_click(handle_audio_submission)  # Call when button is clicked
    return pn.Column(
        reactive_chat.draw_view(),
        pn.Row(record_button)  # Add record button to GUI
    )

if __name__ == "__main__":    
    app = create_app()
    pn.serve(app, callback_exception='verbose')

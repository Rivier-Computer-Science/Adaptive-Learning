import autogen
import panel as pn
import openai
import os
import speech_recognition as sr
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat import ReactiveChat
from src.UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Initialize the speech recognizer
recognizer = sr.Recognizer()
audio_data = None

# Initialize status indicator text
status_text = pn.widgets.StaticText(name="Speech Recognition Status", value="Idle")

# Function to capture and recognize speech for a fixed duration
def recognize_speech_from_mic():
    global audio_data
    status_text.value = "Listening..."
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        print("Listening for 7 seconds...")
        try:
            # Listen for a fixed duration of 7 seconds
            audio_data = recognizer.listen(source, timeout=7, phrase_time_limit=7)
            status_text.value = "Processing..."
            transcript = recognizer.recognize_google(audio_data)
            print(f"Transcribed: {transcript}")
            status_text.value = "Idle"
            return transcript
        except sr.WaitTimeoutError:
            status_text.value = "Timeout: No speech detected"
            print("Timeout: No speech detected")
            return None
        except sr.UnknownValueError:
            status_text.value = "Error: Could not understand audio"
            print("Error: Could not understand audio")
            return None
        except sr.RequestError as e:
            status_text.value = f"Error: {e}"
            print(f"Error: {e}")
            return None

# Function to start listening for 7 seconds
def start_listening():
    status_text.value = "Listening for 7 seconds..."
    transcript = recognize_speech_from_mic()  # Automatically stop listening after 7 seconds
    if transcript:
        reactive_chat.learn_tab_interface.send(transcript, user="User", avatar="🎤")
    reset_recognizer()  # Reinitialize the speech recognizer for the next recording

# Function to reinitialize the recognizer and status
def reset_recognizer():
    global recognizer, audio_data
    recognizer = sr.Recognizer()  # Reinitialize recognizer
    audio_data = None
    status_text.value = "Idle"
    print("Recognizer reset, ready for next session.")

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
    start_listening()  # Call to start listening for 7 seconds

# Create app with speech recognition buttons and status indicator
def create_app():    
    record_button = pn.widgets.Button(name="Record Audio", button_type="primary")
    record_button.on_click(handle_audio_submission)  # Call when Record button is clicked

    return pn.Column(
        reactive_chat.draw_view(),
        pn.Row(record_button, status_text)  # Add record button and status indicator to GUI
    )

if __name__ == "__main__":    
    app = create_app()
    pn.serve(app, callback_exception='verbose')

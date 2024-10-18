import autogen
import panel as pn
import openai
import os
import asyncio
import speech_recognition as sr
from typing import List, Dict
from src import globals
from src.Agents.agents import agents_dict, AgentKeys
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat16 import ReactiveChat
from src.UI.avatar import avatar
from src.UI.user_interface import UserInterface
from src.Tools.progress_tracker import ProgressTracker
from src.Agents.mastery_agent import MasteryAgent

os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Function to capture and recognize speech
def recognize_speech_from_mic():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech...")
        audio = recognizer.listen(source)
        
        try:
            print("Recognizing speech...")
            transcript = recognizer.recognize_google(audio)
            print(f"Transcribed: {transcript}")
            return transcript
        except sr.UnknownValueError:
            print("Google Web Speech could not understand the audio")
            return "Sorry, I didn't catch that."
        except sr.RequestError as e:
            print(f"Error with the Google Web Speech service; {e}")
            return "Error occurred while processing audio."

class MathMasteryInterface:
    def __init__(self, mastery_agent):
        self.mastery_agent = mastery_agent
        self.topic_selector = pn.widgets.Select(name='Select Topic', options=self.mastery_agent.topics)
        self.start_test_button = pn.widgets.Button(name='Start Mastery Test', button_type='primary')
        self.question_display = pn.pane.Markdown("Click 'Start Mastery Test' to begin.")
        self.answer_input = pn.widgets.TextInput(name='Your Answer')
        self.submit_answer_button = pn.widgets.Button(name='Submit Answer', button_type='success')
        self.feedback_display = pn.pane.Markdown("")
        self.progress_display = pn.pane.Markdown("")
        
        self.start_test_button.on_click(self.start_mastery_test)
        self.submit_answer_button.on_click(self.submit_answer)
        
        self.current_question = None
        self.test_results = []
        
    async def start_mastery_test(self, event):
        topic = self.topic_selector.value
        self.test_results, mastery_achieved = await self.mastery_agent.conduct_mastery_test(
            topic, 
            num_questions=globals.MIN_QUESTIONS_PER_TOPIC,
            get_student_answer_func=self.get_student_answer
        )
        self.display_results(mastery_achieved)
        
    async def get_student_answer(self, question):
        self.current_question = question
        self.question_display.object = f"Question: {question}"
        self.answer_input.value = ""
        self.feedback_display.object = ""
        
        answer_future = asyncio.Future()
        self.submit_answer_button.on_click(lambda event: answer_future.set_result(self.answer_input.value))
        
        return await answer_future
        
    def submit_answer(self, event):
        # This method is called when the submit button is clicked
        # The actual answer processing is handled in get_student_answer
        pass
        
    def display_results(self, mastery_achieved):
        result_text = "# Mastery Test Results\n\n"
        for i, result in enumerate(self.test_results, 1):
            result_text += f"**Question {i}:** {result['question']}\n"
            result_text += f"Your answer: {result['student_answer']}\n"
            result_text += f"Correct answer: {result['correct_answer']}\n"
            result_text += f"Evaluation: {result['evaluation']}\n\n"
        
        result_text += f"\n**Overall Result:** {'Mastery Achieved!' if mastery_achieved else 'Keep practicing!'}"
        self.feedback_display.object = result_text
        
        progress = self.mastery_agent.get_mastery_status()
        self.progress_display.object = f"**Progress:** {progress}"
        
    def create_layout(self):
        return pn.Column(
            self.topic_selector,
            self.start_test_button,
            self.question_display,
            self.answer_input,
            self.submit_answer_button,
            self.feedback_display,
            self.progress_display
        )
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
                            speaker_selection_method=fsm.next_speaker_selector)

manager = CustomGroupChatManager(groupchat=groupchat,
                                 filename=progress_file_path, 
                                 is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0)

# Initialize UserInterface and ProgressTracker
user_interface = UserInterface()
progress_tracker = ProgressTracker(progress_file_path)

# Begin GUI components
reactive_chat = ReactiveChat(groupchat_manager=manager)
reactive_chat.set_user_interface(user_interface)
reactive_chat.set_progress_tracker(progress_tracker)

# Initialize MathMasteryInterface
math_mastery_interface = MathMasteryInterface(agents_dict[AgentKeys.MASTERY.value])

# Register groupchat_manager and reactive_chat GUI interface with ConversableAgents
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

# Load chat history on startup
manager.get_chat_history_and_initialize_chat(filename=progress_file_path, chat_interface=reactive_chat.learn_tab_interface)
reactive_chat.update_dashboard()

# --- Speech Capture and Processing ---
def handle_audio_submission(event):
    transcript = recognize_speech_from_mic()
    reactive_chat.learn_tab_interface.send(transcript, user="User", avatar="🎤")

# Create app with speech recognition button
def create_app():    
    record_button = pn.widgets.Button(name="Record Audio", button_type="primary")
    record_button.on_click(handle_audio_submission)
    
    reactive_chat_tabs = pn.Tabs(
        ("Learn", pn.Column(reactive_chat.learn_tab_interface)),
        ("Dashboard", pn.Column(reactive_chat.dashboard_view)),
        ("Leaderboard", reactive_chat.leaderboard.draw_view()),
        ("Progress", pn.Column(
                reactive_chat.progress_text,
                pn.Row(                        
                    reactive_chat.progress_bar,
                    reactive_chat.progress_info))),
        ("Model", pn.Column(
                  pn.Row(reactive_chat.button_update_learner_model),
                  pn.Row(reactive_chat.model_tab_interface)))
    )
    
    main_tabs = pn.Tabs(
        ("Adaptive Learning", pn.Column(reactive_chat_tabs, pn.Row(record_button))),
        ("Math Mastery", math_mastery_interface.create_layout())
    )
    
    return main_tabs

if __name__ == "__main__":    
    app = create_app()
    pn.serve(app, callback_exception='verbose')

import asyncio
import os
from typing import Dict, List

import asyncio
import os
from typing import Dict, List
import autogen
import openai
import openai
import panel as pn
import speech_recognition as sr
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM

from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat16 import ReactiveChat
from src.UI.avatar import avatar
from src.KnowledgeGraphs.math_taxonomy import topic_colors
import pandas as pd


os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Initialize the speech recognizer
recognizer = sr.Recognizer()

class MathMasteryInterface:
    def __init__(self, mastery_agent):
        self.mastery_agent = mastery_agent
        
        # Topic Selection
        self.topic_selector = pn.widgets.Select(
            name='Select Topic', 
            options=self.mastery_agent.topics,
            styles={'background': f'rgb({topic_colors.get(self.mastery_agent.topics[0], "97,130,100")}'}
        )
        
        # Test Controls
        self.start_test_button = pn.widgets.Button(
            name='Start Mastery Test', 
            button_type='primary',
            styles={'width': '200px'}
        )
        
        # Question Display
        self.question_display = pn.pane.Markdown(
            "Click 'Start Mastery Test' to begin.",
            styles={'font-size': '16px', 'padding': '10px'}
        )
        
        # Answer Input
        self.answer_input = pn.widgets.TextAreaInput(
            name='Your Answer',
            placeholder='Enter your answer here...',
            height=100
        )
        
        # Submit Button
        self.submit_answer_button = pn.widgets.Button(
            name='Submit Answer',
            button_type='success',
            disabled=True
        )
        
        # Progress Display
        self.progress_bar = pn.indicators.Progress(
            name='Topic Progress',
            value=0,
            max=100,
            width=400
        )
        
        # Feedback Display
        self.feedback_display = pn.pane.Markdown(
            "",
            styles={'background': '#f8f9fa', 'padding': '10px'}
        )
        
        # Progress History
        self.progress_history = pn.widgets.DataFrame(
            name="Progress History",
            width=800
        )
        
        # Event Handlers
        self.start_test_button.on_click(self.start_mastery_test)
        self.submit_answer_button.on_click(self.submit_answer)
        self.topic_selector.param.watch(self.update_topic_color, 'value')
        
        # Initialize
        self.current_question = None
        self.test_results = []
        self.test_in_progress = False

    def update_topic_color(self, event):
        """Update color based on selected topic"""
        color = topic_colors.get(event.new, "97,130,100")
        self.topic_selector.styles = {'background': f'rgb({color})'}

    async def start_mastery_test(self, event):
        """Start a new mastery test"""
        self.test_in_progress = True
        self.submit_answer_button.disabled = False
        topic = self.topic_selector.value
        
        try:
            self.test_results, mastery_achieved = await self.mastery_agent.conduct_mastery_test(
                topic,
                get_student_answer_func=self.get_student_answer
            )
            self.display_results(mastery_achieved)
            self.update_progress_history()
        except Exception as e:
            self.feedback_display.object = f"Error during test: {str(e)}"
        finally:
            self.test_in_progress = False
            self.submit_answer_button.disabled = True

    async def get_student_answer(self, question):
        """Get student's answer for a question"""
        self.current_question = question
        self.question_display.object = f"Question: {question}"
        self.answer_input.value = ""
        self.feedback_display.object = "Thinking..."
        
        answer_future = asyncio.Future()
        self.submit_answer_button.on_click(
            lambda event: answer_future.set_result(self.answer_input.value)
        )
        
        return await answer_future

    def display_results(self, mastery_achieved):
        """Display test results and feedback"""
        result_text = "# Mastery Test Results\n\n"
        
        for i, result in enumerate(self.test_results, 1):
            result_text += (
                f"**Question {i}:** {result['question']}\n\n"
                f"Your answer: {result['student_answer']}\n\n"
                f"Correct answer: {result['correct_answer']}\n\n"
                f"Evaluation: {result['evaluation']}\n\n"
                f"---\n\n"
            )
        
        status = "🎉 Mastery Achieved!" if mastery_achieved else "📚 Keep practicing!"
        result_text += f"\n**Overall Result:** {status}"
        
        self.feedback_display.object = result_text
        self.update_progress()

    def update_progress(self):
        """Update progress indicators"""
        status = self.mastery_agent.get_mastery_status()
        if isinstance(status, dict):
            self.progress_bar.value = status['mastery_percentage']

    def update_progress_history(self):
        """Update progress history display"""
        if hasattr(self.mastery_agent, 'performance_history'):
            history_data = []
            for topic, performances in self.mastery_agent.performance_history.items():
                for subtopic, score in performances.items():
                    history_data.append({
                        'Topic': topic,
                        'Subtopic': subtopic,
                        'Performance': f"{score*100:.1f}%"
                    })
            self.progress_history.value = pd.DataFrame(history_data)

    
    def create_layout(self):
        return pn.Column(
            pn.Row(
                pn.Column(
                    "# Math Mastery Testing",
                    self.topic_selector,
                    self.start_test_button,
                    width=300
                ),
                pn.Column(
                    self.progress_bar,
                    self.progress_history,
                    width=500
                )
            ),
            pn.Row(
                pn.Column(
                    self.question_display,
                    self.answer_input,
                    self.submit_answer_button,
                    width=400
                ),
                pn.Column(
                    self.feedback_display,
                    width=600
                )
            )
        )

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

##############################################
# Main Adaptive Learning Application
##############################################
globals.input_future = None
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

fsm = FSM(agents_dict)

groupchat = CustomGroupChat(
    agents=list(agents_dict.values()), 
    messages=[],
    max_round=globals.MAX_ROUNDS,
    send_introductions=True,
    speaker_selection_method=fsm.next_speaker_selector
)

manager = CustomGroupChatManager(
    groupchat=groupchat,
    filename=progress_file_path, 
    is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0
)    

# Begin GUI components
reactive_chat = ReactiveChat(groupchat_manager=manager)

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

def handle_audio_submission(event):
    transcript = recognize_speech_from_mic()
    reactive_chat.learn_tab_interface.send(transcript, user="User", avatar="🎤")

def create_app():    
    record_button = pn.widgets.Button(name="Record Audio", button_type="primary")
    record_button.on_click(handle_audio_submission)
    
    # Create tabs for different interfaces
    tabs = pn.Tabs(
        ("Learning Assistant", pn.Column(reactive_chat.draw_view())),
        ("Math Mastery", math_mastery_interface.create_layout()),
    )
    
    return pn.Column(
        tabs,
        pn.Row(record_button)
    )

if __name__ == "__main__":    
    app = create_app()
    pn.serve(app, callback_exception='verbose')

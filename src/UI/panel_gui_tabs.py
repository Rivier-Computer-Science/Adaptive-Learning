
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import asyncio
import panel as pn
import speech_recognition as sr
import pandas as pd
import autogen
import openai
import traceback
import logging

from dotenv import load_dotenv
load_dotenv()

from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat16 import ReactiveChat
from src.UI.reactive_chat24_language import ReactiveChat as LanguageChat
from src.Agents.language_agents import create_agents
from src.FSMs.fsm_language import TeachMeFSM
from src.UI.avatar import avatar
from src.KnowledgeGraphs.math_taxonomy import topic_colors
from src.UI.panel_gui_tabs_vt import career_tab

pn.extension()
os.environ["AUTOGEN_USE_DOCKER"] = "False"
recognizer = sr.Recognizer()

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

#========== Math Mastery ==========#

class MathMasteryInterface:
    def __init__(self, mastery_agent):
        self.mastery_agent = mastery_agent
        self.topic_selector = pn.widgets.Select(name='Select Topic', options=self.mastery_agent.topics, value=self.mastery_agent.topics[0])
        self.start_test_button = pn.widgets.Button(name='Start Mastery Test', button_type='primary', width=200)
        self.question_display = pn.pane.Markdown("Click 'Start Mastery Test' to begin.", styles={'font-size': '16px'})
        self.answer_input = pn.widgets.TextAreaInput(name='Your Answer', placeholder='Enter your answer here...', height=100)
        self.submit_answer_button = pn.widgets.Button(name='Submit Answer', button_type='success', disabled=True)
        self.progress_bar = pn.indicators.Progress(name='Topic Progress', value=0, max=100, width=400)
        self.feedback_display = pn.pane.Markdown("", styles={'background': '#f8f9fa', 'padding': '10px'})
        self.progress_history = pn.widgets.DataFrame(name="Progress History", width=800)
        self.score_display = pn.pane.Markdown("", styles={'color': 'green'})

        self.start_test_button.on_click(self.start_mastery_test)
        self.submit_answer_button.on_click(self.submit_answer)
        self.topic_selector.param.watch(self.update_topic_color, 'value')

        self.current_question = None
        self.test_results = []
        self.question_count = 0
        self.max_questions = 10

    def update_topic_color(self, event):
        color = topic_colors.get(event.new, "97,130,100")
        self.topic_selector.styles = {'background': f'rgb({color})'}

    def start_mastery_test(self, event):
        self.question_count = 0
        asyncio.create_task(self.async_start_test())

    async def async_start_test(self):
        topic = self.topic_selector.value
        question_text = await self.mastery_agent.start_test(topic)
        if not question_text or question_text.strip() == "":
            self.question_display.object = "⚠️ No question was generated."
            self.question_display.param.trigger('object')
            return
        self.question_display.object = f"**Question:** {question_text}"
        self.question_display.param.trigger('object')
        self.answer_input.value = ""
        self.answer_input.disabled = False
        self.submit_answer_button.disabled = False

    def submit_answer(self, event):
        asyncio.create_task(self.async_submit_answer())

    async def async_submit_answer(self):
        try:
            student_answer = self.answer_input.value.strip()
            if not student_answer:
                self.feedback_display.object = "⚠️ Please enter an answer before submitting."
                return

            next_q = await self.mastery_agent.evaluate_next(student_answer)
            self.update_progress()

            if next_q and self.question_count < self.max_questions:
                for line in next_q.splitlines():
                    line = line.strip()
                    if line and not line.lower().startswith("answer") and not line.startswith("**"):
                        extracted = line
                        break
                else:
                    extracted = "❓ Couldn't extract next question."

                self.question_display.object = f"**Question:** {extracted}"
                self.question_display.param.trigger('object')
                self.answer_input.value = ""
                self.question_count += 1
            else:
                results, achieved = self.mastery_agent.get_results()
                self.display_results(results, achieved)
                self.submit_answer_button.disabled = True
                self.answer_input.disabled = True

        except Exception as e:
            print(f"[ERROR] async_submit_answer(): {e}")

    def display_results(self, results, mastery_achieved):
        result_text = "# Mastery Test Results\n\n"
        for i, result in enumerate(results, 1):
            result_text += (
                f"**Q{i}:** {result['question']}\n\n"
                f"Your answer: {result['student_answer']}\n\n"
                f"Correct answer: {result['correct_answer']}\n\n"
                f"Evaluation: {result['evaluation']}\n\n---\n\n"
            )
        status = "🎉 Mastery Achieved!" if mastery_achieved else "📚 Keep practicing!"
        result_text += f"\n**Overall Result:** {status}"
        self.feedback_display.object = result_text

    def update_progress(self):
        status = self.mastery_agent.get_mastery_status()
        if isinstance(status, dict):
            self.progress_bar.value = status['mastery_percentage']
            self.score_display.object = f"**Progress:** {status['correct_answers']} / {status['questions_attempted']} correct"

    def update_progress_history(self):
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
            pn.pane.Markdown("## 🧠 Math Mastery Testing", styles={'font-size': '22px', 'color': '#9900cc'}),
            pn.Row(self.topic_selector, self.start_test_button, sizing_mode='stretch_width'),
            pn.Spacer(height=10),
            pn.Row(self.progress_bar, self.score_display, sizing_mode='stretch_width'),
            pn.Spacer(height=10),
            self.progress_history,
            pn.Spacer(height=20),
            pn.pane.Markdown("### 📋 Question", styles={'font-size': '16px', 'color': '#333'}),
            self.question_display,
            pn.Spacer(height=10),
            pn.pane.Markdown("### ✍️ Your Answer", styles={'font-size': '16px'}),
            self.answer_input,
            self.submit_answer_button,
            pn.Spacer(height=20),
            self.feedback_display
        )

#========== Language Tab ==========#

def create_language_tab():
    language_selector = pn.widgets.Select(name="Choose a Language", options=["Telugu", "Spanish", "French"], value="Telugu")
    status_pane = pn.pane.Markdown("### 👇 Select your language and click Start")
    content_area = pn.Column()
    def on_start(event):
        selected_language = language_selector.value
        status_pane.object = f"### ✅ Starting Language Chat in **{selected_language}**..."

        agents_dict, avatars = create_agents(selected_language)
        fsm = TeachMeFSM(agents_dict)

        groupchat = CustomGroupChat(
            agents=list(agents_dict.values()),
            messages=[],
            max_round=globals.MAX_ROUNDS,
            send_introductions=True,
            speaker_selection_method=fsm.next_speaker_selector
        )

        manager = CustomGroupChatManager(groupchat=groupchat, filename=progress_file_path)
        fsm.register_groupchat_manager(manager)

        reactive_chat = LanguageChat(agents_dict=agents_dict, avatars=avatars, groupchat_manager=manager)

        for agent in groupchat.agents:
            agent.groupchat_manager = manager
            agent.reactive_chat = reactive_chat
            agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

        manager.get_chat_history_and_initialize_chat(
            initial_message=f"Welcome to the {selected_language} Teacher! How can I help you today?",
            avatars=avatars,
            filename=progress_file_path,
            chat_interface=reactive_chat.learn_tab_interface
        )

        reactive_chat.update_dashboard()
        content_area.objects = [reactive_chat.draw_view()]

    start_button = pn.widgets.Button(name="Start", button_type="primary")
    start_button.on_click(on_start)

    return pn.Column(pn.Row(language_selector, start_button), status_pane, content_area)

#========== Main Application ==========#

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
    filename=os.path.join(os.path.dirname(__file__), '../../progress.json'),
    is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0
)

reactive_chat = ReactiveChat(groupchat_manager=manager)
math_mastery_interface = MathMasteryInterface(agents_dict[AgentKeys.MASTERY.value])

for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    if hasattr(agent, 'autogen_reply_func'):
        agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

manager.get_chat_history_and_initialize_chat(filename=manager.filename, chat_interface=reactive_chat.learn_tab_interface)
reactive_chat.update_dashboard()

template = pn.template.BootstrapTemplate(
    title="Adaptive Learning - Unified App",
    main=[
        pn.Tabs(
            ("Learning Assistant", reactive_chat.draw_view()),
            ("Math Mastery", math_mastery_interface.create_layout()),
            career_tab,
            ("Language", create_language_tab())  # ✅ Language tab is fully embedded here
        )
    ]
)

if __name__ == "__main__":
    pn.serve(template, show=True, autoreload=True)


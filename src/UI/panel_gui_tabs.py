import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import asyncio
import panel as pn
import speech_recognition as sr
import pandas as pd

pn.extension()

import autogen
import openai

from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat16 import ReactiveChat
from src.UI.avatar import avatar
from src.KnowledgeGraphs.math_taxonomy import topic_colors

os.environ["AUTOGEN_USE_DOCKER"] = "False"
recognizer = sr.Recognizer()

class MathMasteryInterface:
    def __init__(self, mastery_agent):
        self.mastery_agent = mastery_agent

        self.topic_selector = pn.widgets.Select(
            name='Select Topic',
            options=self.mastery_agent.topics,
            value=self.mastery_agent.topics[0],
        )
        self.update_topic_color(type('Event', (object,), {'new': self.mastery_agent.topics[0]})())

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

    def update_topic_color(self, event):
        color = topic_colors.get(event.new, "97,130,100")
        self.topic_selector.styles = {'background': f'rgb({color})'}

    def start_mastery_test(self, event):
        print("[UI] Start Mastery Test button clicked")
        asyncio.create_task(self.async_start_test())

    async def async_start_test(self):
        topic = self.topic_selector.value
        print(f"[UI] Starting test for topic: {topic}")
        question_block = await self.mastery_agent.start_test(topic)
        print(f"[UI] Full question block:\n{question_block}")

        if not question_block or question_block.strip() == "":
            self.question_display.object = "⚠️ No question was generated. Please try a different topic or check the backend."
            self.question_display.param.trigger('object')
            return

        for line in question_block.splitlines():
            line = line.strip()
            if line and not line.lower().startswith("answer") and not line.startswith("**"):
                extracted = line
                break
        else:
            extracted = "❓ Couldn't extract question. Check formatting."

        print(f"[UI] Extracted question: {extracted}")
        self.question_display.object = f"**Question:** {extracted}"
        self.question_display.param.trigger('object')
        self.answer_input.value = ""
        self.answer_input.disabled = False
        self.submit_answer_button.disabled = False

    def submit_answer(self, event):
        print("[UI] Submit Answer button clicked")
        asyncio.create_task(self.async_submit_answer())

    async def async_submit_answer(self):
        student_answer = self.answer_input.value
        print(f"[UI] Submitted answer: {student_answer}")
        next_q = await self.mastery_agent.evaluate_next(student_answer)
        print(f"[UI] Next question:\n{next_q}")
        self.update_progress()
        if next_q:
            for line in next_q.splitlines():
                line = line.strip()
                if line and not line.lower().startswith("answer") and not line.startswith("**"):
                    extracted = line
                    break
            else:
                extracted = "❓ Couldn't extract question. Check formatting."

            self.question_display.object = f"**Question:** {extracted}"
            self.question_display.param.trigger('object')
            self.answer_input.value = ""
        else:
            results, achieved = self.mastery_agent.get_results()
            self.display_results(results, achieved)
            self.submit_answer_button.disabled = True

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
            pn.Row(
                self.topic_selector,
                self.start_test_button,
                sizing_mode='stretch_width'
            ),
            pn.Spacer(height=10),
            pn.Row(self.progress_bar, self.score_display, sizing_mode='stretch_width'),
            pn.Spacer(height=10),
            self.progress_history,
            pn.Spacer(height=20),
            pn.pane.Markdown("### 📋 Question", styles={'font-size': '16px', 'color': '#333'}),
            pn.Row(
                pn.Column(
                    self.question_display,
                    width=600,
                    height=100,
                    styles={
                        'background': '#f0f0f0',
                        'padding': '10px',
                        'border': '1px solid #ddd'
                    },
                    sizing_mode='stretch_width'
                )
            ),
            pn.Spacer(height=10),
            pn.pane.Markdown("### ✍️ Your Answer", styles={'font-size': '16px'}),
            self.answer_input,
            self.submit_answer_button,
            pn.Spacer(height=20),
            self.feedback_display
        )


# ========== APP SETUP ==========

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

reactive_chat = ReactiveChat(groupchat_manager=manager)
math_mastery_interface = MathMasteryInterface(agents_dict[AgentKeys.MASTERY.value])

for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    if hasattr(agent, 'autogen_reply_func'):
        agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

manager.get_chat_history_and_initialize_chat(filename=progress_file_path, chat_interface=reactive_chat.learn_tab_interface)
reactive_chat.update_dashboard()

template = pn.template.BootstrapTemplate(
    title="Adaptive Learning - Math Mastery",
    main=[
        pn.Tabs(
            ("Learning Assistant", reactive_chat.draw_view()),
            ("Math Mastery", math_mastery_interface.create_layout())
        )
    ]
)

if __name__ == "__main__":
    import panel as pn
    pn.extension()
    pn.serve(template, show=True, autoreload=True)
    
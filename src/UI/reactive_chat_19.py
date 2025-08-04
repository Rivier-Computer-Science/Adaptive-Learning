import param
import panel as pn
import asyncio
import re
import pandas as pd
import autogen as autogen
from src.UI.avatar import avatar
import src.Agents.agents as agents
from src import globals as globals
import logging

class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, tab_type="default", **params):
        super().__init__(**params)
        self.tab_type = tab_type
        pn.extension(design="material")

        pn.config.raw_css.append("""
        .tabulator-cell {
            white-space: normal !important;
            word-wrap: break-word;
            padding: 5px;
        }
        .custom-table-container {
            width: 99vw;
            margin: 0 auto;
        }
        """)

        self.groupchat_manager = groupchat_manager

        self.LEARN_TAB_NAME = "LearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback, name=self.LEARN_TAB_NAME)

        self.dashboard_view = pn.pane.Markdown("Total messages: 0")

        self.progress_text = pn.pane.Markdown("Student Progress")
        self.progress = 0
        self.max_questions = 10
        self.quiz_score = 0
        self.progress_bar = pn.widgets.Progress(name='Progress', value=0, max=10)
        self.progress_info = pn.pane.Markdown(f"0 out of 10 | Points: 0", width=160)

        self.question_details = pn.widgets.Tabulator(
            pd.DataFrame(columns=['Question', 'Student Answer', 'Points']),
            show_index=False,
            height=400,
            sizing_mode='stretch_width',
            configuration={
                'layout': 'fitColumns',
                'columns': [
                    {'field': 'Question', 'title': 'Question', 'widthGrow': 3},
                    {'field': 'Student Answer', 'title': 'Student Answer', 'widthGrow': 1},
                    {'field': 'Points', 'title': 'Points', 'hozAlign': 'center'}
                ],
            }
        )

        self.MODEL_TAB_NAME = "ModelTab"
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback, name=self.MODEL_TAB_NAME)
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)

        self.groupchat_manager.chat_interface = self.learn_tab_interface

    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        self.groupchat_manager.chat_interface = instance
        if 'solve' in contents.lower():
            globals.last_question = contents
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)

    def update_learn_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name != self.LEARN_TAB_NAME:
            return
        last_content = messages[-1]['content']
        user = messages[-1].get('name', recipient.name)
        self.learn_tab_interface.send(last_content, user=user, avatar=avatar.get(user), respond=False)

    def update_dashboard(self):
        self.dashboard_view.object = f"Total messages: {len(self.groupchat_manager.groupchat.get_messages())}"

    def update_progress(self, contents, user):
        if user != "LevelAdapterAgent":
            return

        all_messages = self.groupchat_manager.groupchat.get_messages()
        question = student_answer = None
        for msg in reversed(all_messages):
            if not question and msg['name'] == 'ProblemGeneratorAgent':
                question = msg['content']
            if not student_answer and msg['name'] == 'StudentAgent':
                student_answer = msg['content']
            if question and student_answer:
                break

        pattern_correct = re.compile(r"\b(correct|is correct|well done|solution was verified|answer is accurate)\b", re.IGNORECASE)
        is_correct = bool(pattern_correct.search(contents))
        point_value = 1 if is_correct else 0

        if self.tab_type == "quiz":
            self.quiz_score += point_value
            if self.progress < self.max_questions:
                self.progress += 1
                self.progress_bar.value = self.progress
                self.progress_info.object = f"{self.progress} out of {self.max_questions} | Points: {self.quiz_score}"

            new_row = pd.DataFrame({
                'Question': [question],
                'Student Answer': [student_answer],
                'Points': [point_value]
            })

            self.question_details.value = pd.concat([self.question_details.value, new_row], ignore_index=True)

    async def handle_button_update_model(self, event=None):
        self.groupchat_manager.chat_interface = self.model_tab_interface
        await self.a_update_model()

    async def a_update_model(self):
        if self.groupchat_manager.chat_interface.name != self.MODEL_TAB_NAME:
            return
        messages = self.groupchat_manager.groupchat.get_messages()
        for m in messages:
            agents.learner_model.send(m, recipient=agents.learner_model, request_reply=False)
        await agents.learner_model.a_send("What is the student's current capabilities", recipient=agents.learner_model, request_reply=True)
        response = agents.learner_model.last_message(agent=agents.learner_model)["content"]
        self.model_tab_interface.send(response, user=agents.learner_model.name, avatar=avatar[agents.learner_model.name])

    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        self.groupchat_manager.chat_interface = instance
        if user in ["System", "User"]:
            response = agents.learner_model.last_message(agent=agents.learner_model)["content"]
            self.learn_tab_interface.send(response, user=agents.learner_model.name, avatar=avatar[agents.learner_model.name])

    def draw_view(self):
        return pn.Tabs(
            ("Learn", pn.Column(self.learn_tab_interface)),
            ("Dashboard", pn.Column(self.dashboard_view)),
            ("Progress", pn.Column(
                self.progress_text,
                pn.Row(self.progress_bar, self.progress_info),
                self.question_details
            )),
            ("Model", pn.Column(
                pn.Row(self.button_update_learner_model),
                pn.Row(self.model_tab_interface)
            ))
        )

    @property
    def groupchat_manager(self) -> autogen.GroupChatManager:
        return self._groupchat_manager

    @groupchat_manager.setter
    def groupchat_manager(self, value):
        self._groupchat_manager = value


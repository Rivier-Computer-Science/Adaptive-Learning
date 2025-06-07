
import pandas as pd
import panel as pn
import param
import asyncio
import re
import autogen as autogen
from src.UI.avatar import avatar
import src.Agents.agents as agents
from src import globals as globals
from src.UI.bookmark import BookmarkPage # ✅ Added
from firebase_admin import credentials, firestore
import firebase_admin
import os
from dotenv import load_dotenv

load_dotenv()
key_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
if not key_path:
    raise EnvironmentError("FIREBASE_SERVICE_ACCOUNT_KEY_PATH is not set")

if not firebase_admin._apps:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

class Leaderboard():
    def __init__(self, **params):
        super().__init__(**params)
        self.leaderboard_data = self.fetch_leaderboard_data()
        self.leaderboard_table = self.create_centered_table(self.leaderboard_data)

    def fetch_leaderboard_data(self):
        leaderboard_ref = db.collection("leaderboard").order_by('score', direction=firestore.Query.DESCENDING)
        docs = leaderboard_ref.stream()
        data = {"ProfilePic": [], "Student": [], "Score": []}
        print("pkofca Developed by Bhasker Muda")
        for doc in docs:
            doc_data = doc.to_dict()
            username = doc_data.get("username", "Unknown")
            score = doc_data.get("score", 0)
            profile_pic_url = doc_data.get("profile_image_url", "") or "https://cdn.pixabay.com/photo/2021/07/02/04/48/user-6380868_1280.png"
            data["Student"].append(username)
            data["Score"].append(score)
            data["ProfilePic"].append(profile_pic_url)
            print("odododo", doc, profile_pic_url)
        df = pd.DataFrame(data)
        df['Rank'] = df['Score'].rank(ascending=False, method='min').astype(int)
        df = df.sort_values(by='Rank')
        df = df[['Rank', 'ProfilePic', 'Student', 'Score']]
        return df.reset_index(drop=True)

    def create_centered_table(self, data):
        rows = []
        for _, row in data.iterrows():
            profile_pic_html = f'<img src="{row["ProfilePic"]}" alt="" style="border-radius: 50%; width: 30px; height: 30px; margin-right: 10px;">'
            student_html = f"{profile_pic_html}{row['Student']}"
            rows.append(f"<tr><td>{row['Rank']}</td><td>{student_html}</td><td>{row['Score']}</td></tr>")
        html_table = "<table class='centered-table'><thead><tr><th>Rank</th><th>Student</th><th>Score</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
        custom_css = """
        <style>
            .centered-table {
                width: 100%;
                border-collapse: collapse;
            }
            .centered-table th, .centered-table td {
                text-align: center;
                padding: 8px;
                border: 1px solid #ddd;
            }
            .centered-table th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
        </style>
        """
        return pn.pane.HTML(custom_css + html_table, sizing_mode="stretch_both")

    def update_leaderboard(self):
        self.leaderboard_data = self.fetch_leaderboard_data()
        self.leaderboard_table.object = self.create_centered_table(self.leaderboard_data)

    def draw_view(self):
        return pn.Column(self.leaderboard_table)

class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)
        pn.extension(design="material")
        self.groupchat_manager = groupchat_manager

        self.LEARN_TAB_NAME = "LearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback, name=self.LEARN_TAB_NAME)
        self.dashboard_view = pn.pane.Markdown(f"Total messages: {len(self.groupchat_manager.groupchat.messages)}")
        self.leaderboard = Leaderboard()
        self.bookmark_component = BookmarkPage()  # ✅ Added
        self.progress_text = pn.pane.Markdown(f"**Student Progress**")
        self.progress = 0
        self.max_questions = 10
        self.progress_bar = pn.widgets.Progress(name='Progress', value=self.progress, max=self.max_questions)
        self.progress_info = pn.pane.Markdown(f"{self.progress} out of {self.max_questions}", width=60)
        self.MODEL_TAB_NAME = "ModelTab"
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback, name=self.MODEL_TAB_NAME)
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)
        self.is_model_tab = False
        self.groupchat_manager.chat_interface = self.learn_tab_interface

    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)

    def update_learn_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name is not self.LEARN_TAB_NAME:
            return
        last_content = messages[-1]['content']
        if 'name' in messages[-1]:
            self.learn_tab_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.learn_tab_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)

    def update_dashboard(self):
        self.dashboard_view.object = f"Total messages: {len(self.groupchat_manager.groupchat.get_messages())}"

    def update_progress(self, contents, user):
        if user == "LevelAdapterAgent":
            pattern = re.compile(r'\b(correct|yes|excellent|right|good)\b', re.IGNORECASE)
            if pattern.search(contents):
                if self.progress < self.max_questions:
                    self.progress += 1
                    self.progress_bar.value = self.progress
                    self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"

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
        tabs = pn.Tabs(
            ("Learn", pn.Column(self.learn_tab_interface)),
            ("Dashboard", pn.Column(self.dashboard_view)),
            ("Progress", pn.Column(self.progress_text, pn.Row(self.progress_bar, self.progress_info))),
            ("Model", pn.Column(pn.Row(self.button_update_learner_model), pn.Row(self.model_tab_interface))),
            ("Bookmark", self.bookmark_component.get_view()),  # ✅ Confirmed working
            ("Leaderboard", self.leaderboard.draw_view())       # ✅ Confirmed working
        )
        return tabs

    @property
    def groupchat_manager(self) -> autogen.GroupChatManager:
        return self._groupchat_manager

    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager


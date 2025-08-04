import autogen
import panel as pn
import openai
import os
import asyncio
from typing import List, Dict
from src import globals
from src.Agents.agent_factory import get_fresh_agents_dict, AgentKeys
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat_19 import ReactiveChat
from src.UI.avatar import avatar
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(module)s - %(filename)s - %(funcName)s - line %(lineno)d - %(asctime)s - %(name)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

##############################################
# Main Adaptive Learning Application
##############################################
globals.input_future = None
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

# ✅ Fresh agents per tab
agents_dict = get_fresh_agents_dict()
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

reactive_chat = ReactiveChat(groupchat_manager=manager,tab_type="quiz")

# Register agents
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    if hasattr(agent, 'autogen_reply_func'):
        agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

reactive_chat.update_dashboard()

##############################################
# ✅ Updated Quiz Tab
##############################################

def create_quiz_tab():
    subject_selector = pn.widgets.Select(
        name="Select Subject",
        options=["Math", "Science", "English", "History"],
        value="Math",
        width=200
    )

    intro_text = pn.pane.Markdown(
        "💬 *Select a subject and type a message to start the quiz.*",
        styles={'font-size': '16px', 'color': 'gray'}
    )

    subject_message = pn.pane.Markdown(
        f"✅ **Subject selected: {subject_selector.value}.** Please type a message about **{subject_selector.value}** to begin.",
        styles={'font-size': '16px', 'color': 'green'}
    )

    def update_subject_message(event):
        selected = event.new
        subject_message.object = f"✅ **Subject selected: {selected}.** Please type a message about **{selected}** to begin."

    subject_selector.param.watch(update_subject_message, 'value')

    return pn.Column(
        pn.pane.Markdown("## 🧠 Quiz Assistant", styles={'font-size': '20px'}),
        pn.Row(subject_selector, margin=(0, 0, 15, 0)),
        intro_text,
        subject_message,
        reactive_chat.draw_view()
    )

# ✅ Run standalone
if __name__ == "__main__":
    app = create_quiz_tab()
    pn.serve(app, show=True)


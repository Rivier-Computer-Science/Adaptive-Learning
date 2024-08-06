import autogen
import panel as pn
import os
import json
import plotly.graph_objects as go
import asyncio
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.avatar import avatar

# Setup for autogen and chat manager
os.environ["AUTOGEN_USE_DOCKER"] = "False"

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

globals.input_future = None

fsm = FSM(agents_dict)

# Create the GroupChat with agents and a manager
groupchat = CustomGroupChat(
    agents=list(agents_dict.values()),
    messages=[],
    max_round=30,
    send_introductions=True,
    speaker_selection_method=fsm.next_speaker_selector
)

manager = CustomGroupChatManager(
    groupchat=groupchat,
    filename=progress_file_path,
    is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0
)

def get_chat_history():
    try:
        print('Getting JSON file:', progress_file_path)
        with open(progress_file_path, "r") as f:
            data = json.load(f)
            print(data)  # Debug print
            return data
    except FileNotFoundError:
        print("No previous chat history found.")
        return []

def analyze_student_performance(chat_history):
    performance_data = defaultdict(int)
    topic_counts = defaultdict(int)
    
    for message in chat_history:
        print(message)  # Debug print
        role = message.get('role', '')
        content = message.get('content', '').lower()
        
        if role == 'student':
            performance_data['questions_asked'] += 1
            if 'math' in content:
                topic_counts['Math'] += 1
            elif 'science' in content:
                topic_counts['Science'] += 1
            elif 'english' in content:
                topic_counts['English'] += 1
    
    print(performance_data)  # Debug print
    print(topic_counts)  # Debug print
    
    return {
        'total_questions_asked': performance_data['questions_asked'],
        'topic_counts': dict(topic_counts)
    }

def create_bar_chart(performance_data):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(performance_data['topic_counts'].keys()),
        y=list(performance_data['topic_counts'].values())
    ))
    
    fig.update_layout(
        title='Student Performance by Subject',
        xaxis_title='Subjects',
        yaxis_title='Number of Questions'
    )
    
    print(fig)  # Debug print
    return pn.pane.Plotly(fig, width=600, height=400)

def generate_performance_report(performance_data):
    return f"""
    ## Student Performance Report

    - **Total Questions Asked**: {performance_data['total_questions_asked']}
    
    ### Questions by Subject:
    - Math: {performance_data['topic_counts'].get('Math', 0)}
    - Science: {performance_data['topic_counts'].get('Science', 0)}
    - English: {performance_data['topic_counts'].get('English', 0)}
    """

async def update_report(event):
    chat_history_messages = get_chat_history()
    performance_data = analyze_student_performance(chat_history_messages)
    report_pane.object = generate_performance_report(performance_data)
    bar_chart_pane.object = create_bar_chart(performance_data)

def create_app():
    pn.extension(design="material")

    async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
        if not globals.initiate_chat_task_created:
            asyncio.create_task(manager.delayed_initiate_chat(tutor, manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")

    chat_interface = pn.chat.ChatInterface(callback=callback)

    def print_messages(recipient, messages, sender, config):
        content = messages[-1]['content']
        print(f"Sending message: {content}")  # Debug print
        if 'name' in messages[-1]:
            chat_interface.send(content, user=messages[-1]['name'], avatar=avatar.get(messages[-1]['name'], None), respond=False)
        else:
            chat_interface.send(content, user=recipient.name, avatar=avatar.get(recipient.name, None), respond=False)
        return False, None

    for agent in groupchat.agents:
        agent.chat_interface = chat_interface
        agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

    app = pn.template.BootstrapTemplate(title="Adaptive Learning System")

    global report_pane, bar_chart_pane
    report_pane = pn.pane.Markdown()
    refresh_button = pn.widgets.Button(name='Refresh Report')
    refresh_button.on_click(update_report)

    bar_chart_pane = pn.pane.Plotly()
    
    app.main.append(
        pn.Column(
            chat_interface,
            refresh_button,
            report_pane,
            bar_chart_pane
        )
    )

    chat_history_messages = get_chat_history()
    if chat_history_messages:
        for message in chat_history_messages:
            if 'exit' not in message:
                chat_interface.send(
                    message["content"],
                    user=message["role"],
                    avatar=avatar.get(message["role"], None),
                    respond=False
                )
        chat_interface.send("Time to continue your studies!", user="System", respond=False)
    else:
        chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="System", respond=False)

    return app

if __name__ == "__main__":
    app = create_app()
    pn.serve(app)

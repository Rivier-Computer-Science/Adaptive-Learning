import autogen
import panel as pn
import os
import asyncio
import json
from collections import defaultdict
import plotly.graph_objects as go
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.avatar import avatar
import re

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

# Define patterns for identifying questions and answers
QUESTION_PATTERN = re.compile(r"Solve for x:")
ANSWER_PATTERN = re.compile(r"x\s*=\s*\d+")

# Example topic patterns to identify subjects
TOPIC_PATTERNS = {
    'Algebra': re.compile(r"(linear|quadratic)"),
    'Geometry': re.compile(r"pythagorean|triangle")
}

def analyze_student_performance(chat_history):
    """
    Analyze student performance based on chat history.
    
    Args:
        chat_history (list): List of chat messages.
        
    Returns:
        dict: Performance data for each topic.
    """
    performance_data = defaultdict(lambda: defaultdict(int))  # Nested defaultdict for topics and metrics
    total_questions = defaultdict(int)
    correct_answers = defaultdict(int)

    for message in chat_history:
        if message['role'] == 'user':
            content = message.get('content', '')

            # Determine the topic based on the message content
            current_topic = None
            for topic, pattern in TOPIC_PATTERNS.items():
                if pattern.search(content.lower()):
                    current_topic = topic
                    break

            if current_topic:
                # Check if it's a question
                if QUESTION_PATTERN.search(content):
                    total_questions[current_topic] += 1
                # Check if it's an answer
                elif ANSWER_PATTERN.search(content):
                    correct_answers[current_topic] += 1

    for topic in TOPIC_PATTERNS.keys():
        performance_data[topic]['Total Questions'] = total_questions[topic]
        performance_data[topic]['Correct Answers'] = correct_answers[topic]
        performance_data[topic]['Accuracy (%)'] = (
            (correct_answers[topic] / total_questions[topic]) * 100
            if total_questions[topic] > 0 else 0
        )

    return performance_data

def create_performance_chart(performance_data):
    """
    Create a Plotly chart to visualize performance data.
    
    Args:
        performance_data (dict): Performance data for each topic.
        
    Returns:
        pn.pane.Plotly: Plotly chart pane.
    """
    fig = go.Figure()

    for metric in ['Total Questions', 'Correct Answers', 'Accuracy (%)']:
        x_values = []
        y_values = []
        for topic, metrics in performance_data.items():
            x_values.append(topic)
            y_values.append(metrics[metric])
        
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=metric
        ))

    fig.update_layout(
        title='Student Performance Report',
        xaxis_title='Topics',
        yaxis_title='Values',
        barmode='group'
    )
    
    return pn.pane.Plotly(fig, width=1000, height=600)

# Panel Interface
def create_app():
    pn.extension(design="material")

    performance_chart = pn.pane.Plotly(width=1000, height=600)  # Adjusted width and height
    
    async def update_performance_chart():
        chat_history_messages = manager.get_messages_from_json()
        print("Chat History:", chat_history_messages)  # Debug print
        
        performance_data = analyze_student_performance(chat_history_messages)
        print("Performance Data:", performance_data)  # Debug print
        
        new_chart = create_performance_chart(performance_data)
        if new_chart is not None:
            performance_chart.object = new_chart.object
            performance_chart.param.trigger('object')  # Explicitly trigger the update
            print("Chart Updated")  # Debug print
        else:
            print("Failed to create chart")  # Debug print

    refresh_button = pn.widgets.Button(name='Refresh Performance Report', button_type='primary')
    refresh_button.on_click(lambda event: asyncio.create_task(update_performance_chart()))

    async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
        if not globals.initiate_chat_task_created:
            await manager.delayed_initiate_chat(tutor, manager, contents)
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")
        
        # Ensure this runs asynchronously
        await update_performance_chart()

    chat_interface = pn.chat.ChatInterface(callback=callback, width=800, height=300)  # Adjusted width and height

    def print_messages(recipient, messages, sender, config):
        content = messages[-1]['content']
        if 'name' in messages[-1]:
            chat_interface.send(content, user=messages[-1]['name'], avatar=avatar.get(messages[-1]['name'], None), respond=False)
        else:
            chat_interface.send(content, user=recipient.name, avatar=avatar.get(recipient.name, None), respond=False)
        return False, None

    for agent in groupchat.agents:
        agent.chat_interface = chat_interface
        agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

    app = pn.template.BootstrapTemplate(title="Adaptive Learning System")
    app.main.append(pn.Column(chat_interface, performance_chart, refresh_button))

    # Load chat history and update the performance chart
    asyncio.run(update_performance_chart())

    return app

if __name__ == "__main__":
    app = create_app()
    pn.serve(app)

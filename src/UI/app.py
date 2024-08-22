import os
import json
import asyncio
from datetime import datetime
from typing import Dict
import panel as pn
import plotly.graph_objects as go

# Import necessary modules from your project
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.avatar import avatar

# Initialize environment and file paths
os.environ["AUTOGEN_USE_DOCKER"] = "False"
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create a separate folder for reports
report_folder = os.path.join(script_dir, 'reports')
os.makedirs(report_folder, exist_ok=True)

# Define file paths
progress_file_path = os.path.join(report_folder, 'progress.json')
report_file_path = os.path.join(report_folder, 'performance_report.json')
chart_file_path = os.path.join(report_folder, 'performance_chart.png')

# Initialize global variables
globals.input_future = None

# Set up FSM and GroupChat
fsm = FSM(agents_dict)
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

# Define report generation functions
def collect_data() -> Dict:
    # Placeholder for data collection logic
    # Here you can add logic to dynamically fetch or calculate data based on chat history or other sources
    data = {
        "student_id": "123",
        "student_name": "surendra Reddy",
        "problems_attempted": 50,
        "correct_answers": 40,
        "time_taken": "1 hour 30 minutes",
        "mistakes": {
            "algebra": 5,
            "geometry": 3
        },
        "performance_summary": {
            "overall_accuracy": 80,  # in percentage
            "average_time_per_problem": "1.8 minutes"
        }
    }
    return data

def generate_report(data: Dict):
    try:
        # Generate JSON report
        report = {
            "timestamp": datetime.now().isoformat(),
            "student_information": {
                "student_id": data.get("student_id"),
                "student_name": data.get("student_name")
            },
            "performance_summary": data.get("performance_summary"),
            "detailed_data": {
                "problems_attempted": data.get("problems_attempted"),
                "correct_answers": data.get("correct_answers"),
                "time_taken": data.get("time_taken"),
                "mistakes": data.get("mistakes")
            }
        }

        # Write JSON report to file
        with open(report_file_path, 'w') as file:
            json.dump(report, file, indent=4)
        
        print(f"Dynamic report generated and saved to {report_file_path}")
    except Exception as e:
        print(f"Error generating report: {e}")

def create_performance_chart(data: Dict):
    try:
        # Create performance chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Overall Accuracy', 'Average Time per Problem'],
            y=[data['performance_summary']['overall_accuracy'], 
               float(data['performance_summary']['average_time_per_problem'].split()[0])],
            name='Performance Metrics'
        ))
        fig.update_layout(
            title='Student Performance Overview',
            xaxis_title='Metrics',
            yaxis_title='Values'
        )
        # Save the chart as an image file
        fig.write_image(chart_file_path)
        print(f"Performance chart saved to {chart_file_path}")
    except Exception as e:
        print(f"Error creating performance chart: {e}")

# Define Panel interface and app creation
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
        print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

        content = messages[-1]['content']
        user_name = messages[-1].get('name', recipient.name)
        chat_interface.send(content, user=user_name, avatar=avatar.get(user_name, None), respond=False)
        return False, None

    for agent in groupchat.agents:
        agent.chat_interface = chat_interface
        agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

    app = pn.template.BootstrapTemplate(title=globals.APP_NAME)
    app.main.append(pn.Column(chat_interface))

    # Load and handle chat history dynamically
    chat_history_messages = manager.get_messages_from_json()
    
    if chat_history_messages:
        last_message = chat_history_messages[-1]
        last_user = last_message.get('role', 'Teacher')
        
        # Personalized greeting based on last message
        if last_message.get('content'):
            greeting = f"Welcome back, {last_user}! How can I assist you further today?"
        else:
            greeting = f"Welcome back, {last_user}! What would you like to do today?"

        # Resume chat from history
        manager.resume(chat_history_messages, 'exit')
        
        # Send past messages and the greeting
        for message in chat_history_messages:
            if 'exit' not in message:
                chat_interface.send(
                    message["content"],
                    user=message["role"], 
                    avatar=avatar.get(message["role"], None),
                    respond=False
                )
        chat_interface.send(greeting, user="System", respond=False)
    else:
        chat_interface.send("Welcome to the Adaptive Math teacher! How can I assist you today?", user="System", respond=False)

    return app

if __name__ == "__main__":
    # Collect data and generate the report
    data = collect_data()
    print("Data collected:", data)  # Debug statement
    generate_report(data)
    create_performance_chart(data)
    
    # Start the Panel app
    app = create_app()
    pn.serve(app)

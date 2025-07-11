import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))


import panel as pn
from datetime import datetime
from src.LangGraph.workflow.langgraph_main import graph



pn.extension()

# Step 1: Define UI Widgets
goal_name = pn.widgets.TextInput(name="Goal Name", placeholder="e.g., Learn Python")
description = pn.widgets.TextAreaInput(name="Description", placeholder="What is the goal about?")
target_date = pn.widgets.DatePicker(name="Target Date", value=datetime.today())
code_input = pn.widgets.TextAreaInput(name="Code", placeholder="Enter Python code here", height=100)
priority = pn.widgets.Select(name="Priority", options=["Low", "Medium", "High"])
category = pn.widgets.Select(name="Category", options=["Programming", "Math", "Science"])

submit_btn = pn.widgets.Button(name="Submit Goal", button_type="primary")

# Step 2: Output Panel
stdout_panel = pn.pane.Markdown("", name="Code Output")
tracer_panel = pn.pane.Markdown("", name="Mastery Output")
student_response_panel = pn.pane.Markdown("",name="Student Agent Response")

def on_submit(event):
    if not code_input.value.strip():
        stdout_panel.object = "❗ Please enter valid Python code before submitting."
        tracer_panel.object = ""
        student_response_panel.object = ""
        return

    # Immediately update UI to show processing
    stdout_panel.object = "🔄 Running code..."
    tracer_panel.object = ""
    student_response_panel.object = ""

    # Define async-safe execution in next tick
    def execute():
        user_input = {
            "student_input": {
                "goal_name": goal_name.value,
                "description": description.value,
                "target_date": target_date.value.isoformat(),
                "priority": priority.value,
                "category": category.value
            },
            "code_input": code_input.value
        }

        try:
            result = graph.invoke(user_input)
            print("🔍 Result from LangGraph:", result)
        except Exception as e:
            stdout_panel.object = f"❗ LangGraph error:\n```\n{str(e)}\n```"
            tracer_panel.object = ""
            student_response_panel.object = ""
            return

        code_output = result.get("code_output")
        tracer_output = result.get("tracer_output")
        student_response_output = result.get("student_output")

        stdout = getattr(code_output, 'stdout', 'No code output')
        status = getattr(tracer_output, 'status', 'N/A')
        mastery = getattr(tracer_output, 'mastery_level', 0.0)
        student_response = getattr(student_response_output, 'message', 'No response from Student')

        student_response_panel.object = f"### Student Agent:\n```\n{student_response}\n```"
        stdout_panel.object = f"### Code Output:\n```\n{stdout}\n```"
        tracer_panel.object = f"### Mastery Result:\n- Status: **{status}**\n- Score: **{mastery}**"

    # Ensure UI renders "Running..." before processing starts
    pn.state.curdoc.add_next_tick_callback(execute)



submit_btn.on_click(on_submit)

# Step 4: Layout
layout = pn.Column(
    pn.pane.Markdown("# LangGraph Learning Goal Form"),
    goal_name,
    description,
    target_date,
    code_input,
    priority,
    category,
    submit_btn,
    pn.layout.Divider(),
    student_response_panel,
    stdout_panel,
    tracer_panel
)

# Step 5: Serve or Export
layout.servable()

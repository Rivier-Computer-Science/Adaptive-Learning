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

def on_submit(event):
    if not code_input.value.strip():
        stdout_panel.object = "❗ Please enter valid Python code before submitting."
        return

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

    result = graph.invoke(user_input)
    print("🔍 Result from LangGraph:", result)


    code_output = result.get("code_output")
    tracer_output = result.get("tracer_output")

    stdout = code_output.stdout if code_output else "No code output"
    status = tracer_output.status if tracer_output else "N/A"
    mastery = tracer_output.mastery_level if tracer_output else 0.0

    stdout_panel.object = f"### Code Output:\n```\n{stdout}\n```"
    tracer_panel.object = f"### Mastery Result:\n- Status: **{status}**\n- Score: **{mastery}**"


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
    stdout_panel,
    tracer_panel
)

# Step 5: Serve or Export
layout.servable()

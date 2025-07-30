import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import panel as pn
from datetime import datetime
from src.LangGraph.workflow.langgraph_main import graph

pn.extension()

# Step 1: Define UI Widgets
goal_name = pn.widgets.TextInput(name="Goal Name", placeholder="e.g., Learn Python", sizing_mode="stretch_width")
description = pn.widgets.TextAreaInput(name="Description", placeholder="What is the goal about?", sizing_mode="stretch_width")
target_date = pn.widgets.DatePicker(name="Target Date", value=datetime.today(), sizing_mode="stretch_width")
code_input = pn.widgets.TextAreaInput(name="Code", placeholder="Enter Python code here", height=120, sizing_mode="stretch_width")
priority = pn.widgets.Select(name="Priority", options=["Low", "Medium", "High"], sizing_mode="stretch_width")
category = pn.widgets.Select(name="Category", options=["Programming", "Math", "Science"], sizing_mode="stretch_width")

submit_btn = pn.widgets.Button(name="Submit Goal", button_type="primary")
test_run_btn = pn.widgets.Button(name="Run Sample Goal", button_type="success")  # New test run button

# Step 2: Output Panels
stdout_panel = pn.pane.Markdown("", name="Code Output", height=150, sizing_mode="stretch_width")
tracer_panel = pn.pane.Markdown("", name="Mastery Output", height=120, sizing_mode="stretch_width")
student_response_panel = pn.pane.Markdown("", name="Student Agent Response", height=100, sizing_mode="stretch_width")
error_panel = pn.pane.Markdown("", name="Error Output", height=80, sizing_mode="stretch_width")
fallback_panel = pn.pane.Markdown("", name="Fallback Output", height=80, sizing_mode="stretch_width")

def on_submit(event):
    if not code_input.value.strip():
        stdout_panel.object = "❗ Please enter valid Python code before submitting."
        tracer_panel.object = ""
        student_response_panel.object = ""
        return

    # Clear all outputs
    stdout_panel.object = ""
    tracer_panel.object = ""
    student_response_panel.object = ""
    fallback_panel.object = ""
    error_panel.object = ""

    # Show processing
    stdout_panel.object = "🔄 Running code..."
    tracer_panel.object = ""
    student_response_panel.object = ""

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
            error = result.get("error", None)
            if error:
                error_panel.object = f"### ⚠️ Error:\n```\n{error}\n```"
                fallback_panel.object = f"⚠️ Fallback Triggered:\n```\n{error}\n```"
            else:
                error_panel.object = ""
                fallback_panel.object = ""

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
        student_response = getattr(student_response_output, 'message', 'No response from Student')

        student_response_panel.object = f"### Student Agent:\n```\n{student_response}\n```"

        if code_output and code_output.success:
            stdout_panel.object = f"✅ **Success:**\n```\n{stdout}\n```"
        else:
            stderr = getattr(code_output, 'stderr', 'Unknown Error')
            stdout_panel.object = f"❌ **Error:**\n```\n{stderr}\n```"

        if tracer_output:
            status = tracer_output.status
            mastery = tracer_output.mastery_level
            tracer_panel.object = f"### Mastery Result:\n- Status: **{status}**\n- Score: **{mastery}**"
        else:
            tracer_panel.object = "❗ No mastery data available (fallback triggered)"

    pn.state.curdoc.add_next_tick_callback(execute)

submit_btn.on_click(on_submit)

# New callback for test run
def on_test_run(event):
    goal_name.value = "Learn Loops"
    description.value = "Understand for-loops in Python"
    target_date.value = datetime.today()
    priority.value = "High"
    category.value = "Programming"
    code_input.value = "for i in range(5): print(i)"
    on_submit(None)

test_run_btn.on_click(on_test_run)



# Step 4: Layout
layout = pn.Column(
    pn.pane.Markdown("## 🧠 Adaptive Learning – LangGraph Goal Submission", sizing_mode="stretch_width"),
    pn.pane.Markdown("### 🎯 Goal Details"),
    goal_name,
    description,
    target_date,
    code_input,
    priority,
    category,
    pn.Row(submit_btn, test_run_btn),  # Submit + Test buttons side-by-side
    pn.layout.Divider(),
    pn.pane.Markdown("### 📤 Output Results"),
    fallback_panel,
    student_response_panel,
    stdout_panel,
    tracer_panel,
    error_panel
)

# Step 5: Serve
layout.servable()

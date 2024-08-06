import panel as pn
from crewai import Crew, Process, Agent, Task
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler

pn.extension()

# Define the title
title = pn.pane.Markdown("# Adaptive Tutor", sizing_mode='stretch_width')

# Create a text area input widget
text_area = pn.widgets.TextAreaInput(placeholder="Type your math question here...")

# Create a button to submit the input
submit_button = pn.widgets.Button(name="Submit")

# Create a button to rerun the last question
rerun_button = pn.widgets.Button(name="Rerun Last Question")

# Create a placeholder for displaying results
result_pane = pn.pane.Markdown("**Response will appear here...**", sizing_mode='stretch_width')

# Create a placeholder for the conversation history
history_pane = pn.pane.Markdown("### Conversation History", sizing_mode='stretch_width')

# Store the last question and response
last_question = None
last_response = None

# Define the callback function for the button
def on_submit(event):
    global last_question, last_response
    question = text_area.value
    if question:
        if last_question:
            history_pane.object += f"**Student:** {last_question}\n\n**Tutor:** {last_response}\n\n"
        response = process_with_crew_ai(question)
        last_question = question
        last_response = response
        # Update conversation history
        history_pane.object += f"**Student:** {question}\n\n**Tutor:** {response}\n\n"
        result_pane.object = response
        text_area.value = ""  # Clear the text area
    else:
        result_pane.object = "Please enter a question."

def on_rerun(event):
    global last_question, last_response
    if last_question:
        response = process_with_crew_ai(last_question)
        last_response = response
        # Update conversation history with rerun response
        history_pane.object += f"**Student:** {last_question}\n\n**Tutor:** {response}\n\n"
        result_pane.object = response
    else:
        result_pane.object = "No previous question to rerun."

submit_button.on_click(on_submit)
rerun_button.on_click(on_rerun)

# Layout the widgets
layout = pn.Column(title, history_pane, result_pane, text_area, submit_button, rerun_button)

# Define Crew AI setup
def process_with_crew_ai(question):
    # Setting up the language model
    llm = ChatOpenAI(model="gpt-4")
    
    # Define the agent
    tutor_agent = Agent(
        role='Math Tutor',
        backstory='You are a math tutor with knowledge of various math topics. You should be able to explain and solve problems across different areas of mathematics.',
        goal="Assist with any math-related questions or problems.",
        llm=llm
    )
    
    # Define the task
    task = Task(
        description=f"Provide an explanation or solution for the following math question: {question}",
        agent=tutor_agent,
        expected_output="A detailed explanation or solution."
    )
    
    # Create the Crew
    crew = Crew(
        tasks=[task],
        agents=[tutor_agent],
        manager_llm=llm,
        process=Process.hierarchical
    )
    
    result = crew.kickoff()
    return str(result)

# Initialize with a greeting
history_pane.object = "### Conversation History\n**Tutor:** I'm a math tutor. How can I help you today?\n\n"

# Serve the layout
layout.servable()

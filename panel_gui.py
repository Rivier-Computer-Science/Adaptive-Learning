import os
import queue as queue
from openai import OpenAI
import panel as pn
from conversation_handler_agent import ConversationHandlerAgent, ConversationHistory
from gpt_completion_agent import GPT3CompletionAgent

# Instantiate Agents
message_queue = queue.Queue()
gpt_completion_agent = GPT3CompletionAgent()
conversation_handler_agent = ConversationHandlerAgent(gpt_completion_agent, message_queue)
conversation_history = ConversationHistory()


# PANEL DASHBOARD
pn.extension(loading_spinner='dots', loading_color='#00aa41')

# inp = pn.widgets.TextInput(value="", placeholder='Enter text here...')
# button_conversation = pn.widgets.Button(name="Chat!")
convos_text = [] # store all texts in a list
convos = [] # store all panel objects in a list

def update_ui(_):
    if conversation_handler_agent.latest_response:
        new_response_element = pn.Row('\U0001F916', pn.pane.Markdown(conversation_handler_agent.latest_response, width=600, style={'background-color': '#F6F6F6'}))
        conversation_handler_agent.convo_history.messages.append(new_response_element)  # Add to history
        conversation_handler_agent.latest_response = None  # Reset 

pn.panel(update_ui).servable(period=500)  # Poll every 500ms

def update_conversations(_):  # Changed name for clarity 
    # Assuming 'conversation_history' is available from the agent
    convos.clear()  # Clear previous conversation display

    for message in conversation_handler_agent.conversation_history.messages: 
        if message.startswith("YOUR_USER_MARKER"):  # Replace if needed
            convos.append(pn.Row('\U0001F60A', pn.pane.Markdown(message, width=600)))
        else:
            convos.append(pn.Row('\U0001F916', pn.pane.Markdown(message, width=600, style={'background-color': '#F6F6F6'})))

    return pn.Column(*convos)

# def send_message(_):
#     new_message = inp.value
#     inp.value = ""
#     if new_message:
#         message_queue.put(new_message)  # Enqueue the message 

# interactive_conversation = pn.bind(update_conversations, button_conversation)
# #button_conversation.param.watch(send_message, 'clicks') 

# dashboard = pn.Column(
#     inp,
#     pn.Row(button_conversation),
#     pn.panel(interactive_conversation, loading_indicator=True, height=500),
# )


inp = pn.widgets.TextInput(value="", placeholder='Enter text here...')
button_conversation = pn.widgets.Button(name="Chat!")
output_area = pn.pane.Markdown("")  # Placeholder for displaying responses 

def send_message(_):
    new_message = inp.value
    inp.value = ""
    if new_message:
        # Here's where you'll integrate logic to send to your AutoGen agent
        output_area.object += f"\n**You:** {new_message}"  # Simulate a response for now

button_conversation.param.watch(send_message, 'clicks') 

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    output_area
)


dashboard.servable()
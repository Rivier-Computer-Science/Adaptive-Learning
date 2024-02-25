import os
from openai import OpenAI
import panel as pn


# OPENAI APIs
def openai_completion(prompt):
    """
    OpenAI text completion API given prompt return text
    """
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content
 

# PANEL DASHBOARD
pn.extension(loading_spinner='dots', loading_color='#00aa41')

inp = pn.widgets.TextInput(value="", placeholder='Enter text here...')
button_conversation = pn.widgets.Button(name="Chat!")
convos_text = [] # store all texts in a list
convos = [] # store all panel objects in a list

def get_conversations(_):
    prompt = inp.value
    inp.value = ''
    if prompt != "":
        convos_text.append(prompt)
        openai_answer = openai_completion('\n'.join(convos_text)) # prompt includes all history
        convos_text.append(openai_answer)
        convos.append(
            pn.Row('\U0001F60A', pn.pane.Markdown(prompt, width=600))
        )
        convos.append(
            pn.Row('\U0001F916', pn.pane.Markdown(openai_answer, width=600, style={'background-color': '#F6F6F6'}))
        )
    if len(convos_text) == 0:
        convos.append(pn.Row('\U0001F916', pn.pane.Markdown("Give me something!", width=600, style={'background-color': '#F6F6F6'})))
    return pn.Column(*convos)



interactive_conversation = pn.bind(get_conversations, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=500),
)

dashboard.servable()
import autogen
import panel as pn
import os
import asyncio

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {'model': "gpt-3.5-turbo"}  # You can adjust the model if needed
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}

input_future = None

# Agents
class MyConversableAgent(autogen.ConversableAgent):
    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        chat_interface.send(prompt, user="System", respond=False)

        if input_future is None or input_future.done():
            input_future = asyncio.Future()

        await input_future

        input_value = input_future.result()
        input_future = None
        return input_value

learner = MyConversableAgent(
    name="Learner",
    human_input_mode="ALWAYS",
    llm_config=gpt4_config,
)

tutor = autogen.AssistantAgent(
    name="Tutor",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
    system_message="""A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin."""
)

problem_generator = autogen.AssistantAgent(
    name="ProblemGenerator",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
)

solution_verifier = autogen.AssistantAgent(
    name="SolutionVerifier",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
)

motivator = autogen.AssistantAgent(
    name="Motivator",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
)

visualizer = autogen.AssistantAgent(
    name="Visualizer",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
)

executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
)

critic = autogen.AssistantAgent(
    name="Critic",
    system_message="""Critic. Double check plan, claims, code from other agents and provide feedback.""",
    llm_config=gpt4_config,
    human_input_mode="NEVER",
)

# Backend logic for answer checking
def check_answer(message_content):
    # Simple simulation: check if the message matches a predefined correct answer
    correct_answers = ["yes", "no", "correctly", "correct", "well done"]
    if message_content.lower() in correct_answers:
        return True
    return False

# Functionality for creating/gathering explanations and hints
def provide_explanation():
    return "Here is an explanation for the problem."

def provide_hint():
    return "Try breaking down the problem into smaller steps."

groupchat = autogen.GroupChat(agents=[learner, tutor, problem_generator, solution_verifier, motivator, visualizer,executor], messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

avatar = {
    learner.name: "🎓", tutor.name: "🧑‍🏫", problem_generator.name: "❓",
    solution_verifier.name: "✅", motivator.name: "🙌", visualizer.name: "📊", executor.name: "🖥️", critic.name: '📝'
}

# Define custom CSS for the correctness indicator
custom_css = """
.custom-boolean-indicator .bk.true {
    background-color: #4CAF50; /* Green for success */
    border-color: #4CAF50;
}

.custom-boolean-indicator .bk.false {
    background-color: #F44336; /* Red for incorrect */
    border-color: #F44336;
}
"""

def print_messages(recipient, messages, sender, config):
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    content = messages[-1]['content']
    is_correct = check_answer(content)  # Check the answer

    if 'name' not in messages[-1]:
        messages[-1]['name'] = sender.name  # Set the correct user name

    chat_interface.send(content, user=messages[-1]['name'], avatar=avatar.get(messages[-1]['name'], "🤖"), respond=False)
    
    # Correctness
    if sender.name == "Learner":
        # Send a confirmation or request for further action based on the check result
        if is_correct:
            correctness_symbol = "✅"
            css_class = "true"
            chat_interface.send(f"{sender.name}'s answer is correct.", user=recipient.name, respond=False)
        else:
            correctness_symbol = "❌"
            css_class = "false"

        content_with_symbol = f"{content} {correctness_symbol}"
        content_with_css = f'<div class="custom-boolean-indicator {css_class}">{content_with_symbol}</div>'
        chat_interface.send(content_with_css, user=messages[-1]['name'], avatar=avatar.get(messages[-1]['name'], "🤖"), respond=False)

    # Explanations and hints if requested
    elif content.lower() == "explain":
        explanation = provide_explanation()
        chat_interface.send(explanation, user=recipient.name, respond=False)
    
    elif content.lower() == "hint":
        hint = provide_hint()
        chat_interface.send(hint, user=recipient.name, respond=False)
 
    else:
        # For other agents, just display the message
        chat_interface.send(content, user=messages[-1]['name'], avatar=avatar.get(messages[-1]['name'], "🤖"), respond=False)

 
 
 
    pn.io.push_notebook()  # Force UI update after sending the message
    return False, None

# Register the print_messages function for each agent
for agent in groupchat.agents:
    agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

# --- Panel Interface ---
pn.extension(design="material")



initiate_chat_task_created = False

async def delayed_initiate_chat(agent, recipient, message):
    global initiate_chat_task_created
    initiate_chat_task_created = True
    await asyncio.sleep(2) 
    await agent.a_initiate_chat(recipient, message=message)



async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global initiate_chat_task_created
    global input_future

    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(learner, tutor, contents))  
    else:
        if input_future and not input_future.done():
            input_future.set_result(contents)
        else:
            print("There is currently no input being awaited.")

chat_interface = pn.chat.ChatInterface(callback=callback)

# Correctness indicator

correctness_indicator = pn.indicators.BooleanIndicator(name="Answer Correctness", value=False, width=50, height=50)


# Difficulty Meter
difficulty_level = pn.widgets.Select(name="Difficulty Level", options=["Easy", "Medium", "Hard"])
layout = pn.Column(
    difficulty_level, 
    chat_interface,
    width=1200
)

# For Correct Indicator
layout.css_classes = ['custom-boolean-indicator']
pn.config.raw_css.append(custom_css)

layout.servable()


# Register chat interface with ConversableAgent
learner.chat_interface = chat_interface

chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="Tutor", respond=False)
chat_interface.servable()

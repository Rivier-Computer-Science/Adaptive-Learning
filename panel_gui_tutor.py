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
        print('AGET!!!!!!')  # Display the prompt
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
    correct_answers = ["Yes", "No"]
    return message_content.lower() in correct_answers

groupchat = autogen.GroupChat(
    agents=[learner, tutor, problem_generator, solution_verifier, motivator, visualizer, executor, critic],
    messages=[], 
    max_round=20
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

avatar = {
    learner.name: "🎓", tutor.name: "🧑‍🏫", problem_generator.name: "❓",
    solution_verifier.name: "✅", motivator.name: "🙌", visualizer.name: "📊", executor.name: "🖥️", critic.name: '📝'
}

def print_messages(recipient, messages, sender, config):
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    content = messages[-1]['content']
    is_correct = check_answer(content)  # Check the answer

    if 'name' not in messages[-1]:
        messages[-1]['name'] = sender.name  # Set the correct user name

    chat_interface.send(content, user=messages[-1]['name'], avatar=avatar.get(messages[-1]['name'], "🤖"), respond=False)
    
    # Send a confirmation or request for further action based on the check result
    if is_correct:
        chat_interface.send(f"{sender.name}'s answer is correct.", user=recipient.name, respond=False)
    else:
        chat_interface.send(f"Please review {sender.name}'s answer.", user=recipient.name, respond=False)
    
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

# Register chat interface with ConversableAgent
learner.chat_interface = chat_interface

chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="Tutor", respond=False)
chat_interface.servable()

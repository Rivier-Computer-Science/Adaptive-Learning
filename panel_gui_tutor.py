import autogen
import panel as pn
import openai
import os
import time
import asyncio

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {'model': "gpt-3.5-turbo"}  # You can adjust the model if needed
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}

input_future = None


class LearnerAgent(autogen.ConversableAgent):  
    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        chat_interface.send(prompt, user="Tutor", respond=False) 

        if input_future is None or input_future.done():
            input_future = asyncio.Future()

        await input_future

        input_value = input_future.result()
        input_future = None
        return input_value


learner = LearnerAgent(
    name="Learner",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
    system_message="""You are a student learning math. You will ask questions, solve problems, and receive feedback from the Tutor.""",
    code_execution_config=False,
    human_input_mode="ALWAYS",
    llm_config=gpt4_config,
)

tutor = autogen.AssistantAgent(
    name="Tutor",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
    system_message='''You are a patient and helpful math tutor. Adapt your explanations and problem difficulty to the Learner's progress. Guide the Learner, provide hints, and assess their understanding. When necessary, you can ask the Problem Generator to create practice problems, the Solution Verifier to check the Learner's answers, or the Visualizer to generate visualizations of equations and concepts. Encourage the Learner with positive feedback from the Motivator. 
    ''',
)

problem_generator = autogen.AssistantAgent(
    name="Problem Generator",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
    system_message='''You generate math problems at the appropriate level for the Learner, based on the Tutor's request and the Learner's current skill level.''',
)

solution_verifier = autogen.AssistantAgent(
    name="Solution Verifier",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
    system_message='''You check the Learner's solutions to math problems and provide feedback to the Tutor on whether the solution is correct and, if not, why.''',
)

motivator = autogen.AssistantAgent(
    name="Motivator",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
    system_message='''You provide positive and encouraging feedback to the Learner to keep them motivated. Offer specific praise and acknowledge their effort and progress.''',
)

visualizer = autogen.AssistantAgent(
    name="Visualizer",
    human_input_mode="NEVER",
    llm_config=gpt4_config,
    system_message='''You are skilled at creating visualizations of mathematical equations and concepts. You can generate code (e.g., Python with libraries like Matplotlib or Plotly) to produce graphs, plots, or interactive visualizations based on requests from the Tutor. Please provide the code within code blocks specifying the language. Do not ask for user input in the code.''',
)



# --- Group Chat and Interface ---

groupchat = autogen.GroupChat(agents=[learner, tutor, problem_generator, solution_verifier, motivator, visualizer], messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)


avatar = {
    learner.name: "🎓", tutor.name: "🧑‍🏫", problem_generator.name: "❓", 
    solution_verifier.name: "✅", motivator.name: "🙌", visualizer.name: "📊"
}  



def print_messages(recipient, messages, sender, config):
    content = messages[-1]['content']

    # Check if the message is from the Problem Generator and intended for the Tutor
    if sender == problem_generator and recipient == tutor:
        return False, None  # Don't print or send to chat interface

    # Set the appropriate user for the chat interface
    if sender == learner:  # Check if the sender is the Learner
        user_name = "Learner"  # Use "Learner" as the user for their messages
    else:
        user_name = sender.name  # Otherwise, use the agent's name

    # Ensure all messages have a 'name' key for proper display
    if 'name' not in messages[-1]:
        messages[-1]['name'] = user_name  # Set the correct user name

    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    chat_interface.send(content, user=user_name, avatar=avatar.get(user_name, "🤖"), respond=False)
    pn.io.push_notebook()   # Force UI update after sending the message
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
        asyncio.create_task(delayed_initiate_chat(learner, tutor, contents))  # CORRECTED LINE PLACEMENT
    else:
        if input_future and not input_future.done():
            input_future.set_result(contents)
        else:
            print("No input being awaited.")


chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="Tutor", respond=False)
chat_interface.servable()

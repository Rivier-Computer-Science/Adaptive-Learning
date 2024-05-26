import autogen
import panel as pn
import openai
import os
import time
import asyncio
import globals
from agents import LearnerAgent, TutorAgent, ProblemGeneratorAgent, SolutionVerifierAgent, MotifatorAgent, VisualizerAgent, CodeExecutorAgent

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {'model': "gpt-3.5-turbo"}  # You can adjust the model if needed
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}

globals.input_future = None

# Agents
learner = LearnerAgent()
tutor = TutorAgent()
problem_generator = ProblemGeneratorAgent()
solution_verifier = SolutionVerifierAgent()
motivator = MotifatorAgent()
visualizer = VisualizerAgent()
executor = CodeExecutorAgent()


groupchat = autogen.GroupChat(agents=[learner, tutor, problem_generator, solution_verifier, motivator, visualizer,executor], messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)


avatar = {
    learner.name: "🎓", tutor.name: "🧑‍🏫", problem_generator.name: "❓", 
    solution_verifier.name: "✅", motivator.name: "🙌", visualizer.name: "📊", executor.name: "🖥️"
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

    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(learner, tutor, contents))  
    else:
        if globals.input_future and not globals.input_future.done():
            globals.input_future.set_result(contents)
        else:
            print("No input being awaited.")


chat_interface = pn.chat.ChatInterface(callback=callback)

#Register chat interface with ConversableAgent
learner.chat_interface = chat_interface

chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="Tutor", respond=False)
chat_interface.servable()

import panel as pn
import asyncio
import autogen 
from agents import AdminAgent, EngineerAgent, ScientistAgent, PlannerAgent, ExecutorAgent, CriticAgent
from globals import input_future

pn.extension(design="material")


async def delayed_initiate_chat(agent, recipient, message):
    global initiate_chat_task_created
    initiate_chat_task_created = True
    await asyncio.sleep(2)
    await agent.a_initiate_chat(recipient, message=message)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global initiate_chat_task_created
    global input_future
    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(admin, manager, contents))
    else:
        if input_future and not input_future.done():
            input_future.set_result(contents)
        else:
            print("There is currently no input being awaited.")

def print_messages(recipient, messages, sender, config):
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    content = messages[-1]['content']
    if all(key in messages[-1] for key in ['name']):
        chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
    else:
        chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
    return False, None


chat_interface = pn.chat.ChatInterface(callback=callback)
admin = AdminAgent(chat_interface)
engineer = EngineerAgent()
scientist = ScientistAgent()
planner = PlannerAgent()
executor = ExecutorAgent()
critic = CriticAgent()

groupchat = autogen.GroupChat(agents=[admin, engineer, scientist, planner, executor, critic], messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": [{"model": "gpt-3.5-turbo"}], "temperature": 0, "seed": 53})

avatar = {
    "Admin": "👨‍💼",
    "Engineer": "👩‍💻",
    "Scientist": "👩‍🔬",
    "Planner": "🗓",
    "Executor": "🛠",
    "Critic": "📝",
}


admin.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})
engineer.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})
scientist.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})
planner.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})
executor.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})
critic.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

initiate_chat_task_created = False



chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()

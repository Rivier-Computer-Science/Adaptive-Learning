import panel as pn
import asyncio
from asyncio import Queue
import autogen
from agents import AdminAgent, EngineerAgent, ScientistAgent, PlannerAgent, ExecutorAgent, CriticAgent, print_messages
from globals import input_future, initiate_chat_task_created

pn.extension(design="material")
input_queue = Queue()

async def delayed_initiate_chat(agent, recipient, message):
    global initiate_chat_task_created
    initiate_chat_task_created = True
    await asyncio.sleep(2)
    await agent.a_initiate_chat(recipient, message=message)


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global initiate_chat_task_created
    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(admin, manager, contents))
    else:
        await input_queue.put(contents)


chat_interface = pn.chat.ChatInterface(callback=callback)

admin = AdminAgent(input_queue, chat_interface) 
engineer = EngineerAgent(input_queue)
scientist = ScientistAgent(input_queue)
planner = PlannerAgent(input_queue)
executor = ExecutorAgent()
critic = CriticAgent(input_queue)

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

chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()

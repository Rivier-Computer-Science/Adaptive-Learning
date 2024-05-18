import panel as pn
import asyncio
from asyncio import Queue
import autogen
from agents import CoachAgent, TutorAgent, ContentProviderAgent, EvaluatorAgent, LearnerAgent, VerifierAgent, print_messages
from globals import input_future, initiate_chat_task_created

pn.extension(design="material")

async def delayed_initiate_chat(agent, recipient, message):
    global initiate_chat_task_created
    initiate_chat_task_created = True
    await asyncio.sleep(2)
    await agent.a_initiate_chat(recipient, message=message)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface, input_queue: Queue = None):
    global initiate_chat_task_created
    print(f"Callback received contents: {contents}, user: {user}")
    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(coach, manager, contents))
        return
    if input_queue is not None:
        await input_queue.put({'content': contents, 'name': user})
    print(f"Content put into queue: {contents}")

chat_interface = pn.chat.ChatInterface(callback=callback)

input_queue = Queue()

coach = CoachAgent(input_queue, chat_interface)
tutor = TutorAgent(input_queue, chat_interface)
contentprovider = ContentProviderAgent(input_queue, chat_interface)
evaluator = EvaluatorAgent(input_queue)
learner = LearnerAgent()
verifier = VerifierAgent(input_queue, chat_interface)

groupchat = autogen.GroupChat(agents=[coach, tutor, contentprovider, evaluator, learner, verifier], messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": [{"model": "gpt-3.5-turbo"}], "temperature": 0, "seed": 53})

coach.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": coach.get_queue()})
tutor.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": tutor.get_queue()})
contentprovider.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": contentprovider.get_queue()})
evaluator.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": evaluator.get_queue()})
learner.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": None})
verifier.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": verifier.get_queue()})

chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()

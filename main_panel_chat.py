import panel as pn
import asyncio
from asyncio import Queue
import autogen
from agents import CustomGroupChat, CoachAgent, TutorAgent, ContentProviderAgent, EvaluatorAgent, LearnerAgent, VerifierAgent, print_messages
from globals import input_future, initiate_chat_task_created

pn.extension(design="material")

# main.py
# async def delayed_initiate_chat(agent, recipient, message):
#     global initiate_chat_task_created, current_task

#     # Cancel any existing task before starting a new one
#     if current_task and not current_task.done():
#         current_task.cancel()

#     initiate_chat_task_created = True
#     current_task = asyncio.current_task()  # Store the current task
#     await asyncio.sleep(2)

#     # Prepare messages to send, including user's message and initial system message
#     user_message = {'content': message, 'role': 'user'}
#     system_message = {'role': 'system', 'content': recipient.system_message}
#     recipient.groupchat._oai_messages = [user_message, system_message]

#     # Trigger the reply generation of the Coach (speaker) first
#     await agent.a_generate_reply([system_message, user_message], recipient)

async def handle_user_message(contents, user):
    global initiate_chat_task_created

    message_to_send = {'content': contents, 'role': 'user'}

    if not initiate_chat_task_created:
        system_message = {'role': 'system', 'content': coach.system_message}
        manager.groupchat._oai_messages = [message_to_send, system_message]  # Use manager.groupchat
        await coach.a_generate_reply([system_message, message_to_send], manager)
        initiate_chat_task_created = True
    else:
        try:
            await input_queue.put({'content': contents, 'name': user})
            print(f"Content put into queue: {contents}")
        except AttributeError as e:
            print(f"Error putting message into queue: {e}")


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):  
    asyncio.create_task(handle_user_message(contents, user))



chat_interface = pn.chat.ChatInterface(callback=callback)

input_queue = Queue()

coach = CoachAgent(input_queue, chat_interface)
tutor = TutorAgent(input_queue, chat_interface)
contentprovider = ContentProviderAgent(input_queue, chat_interface)
evaluator = EvaluatorAgent(input_queue)
learner = LearnerAgent()
verifier = VerifierAgent(input_queue, chat_interface)


groupchat = CustomGroupChat(agents=[coach, tutor, contentprovider, evaluator, learner, verifier], messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": [{"model": "gpt-3.5-turbo"}], "temperature": 0, "seed": 53})


coach.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": coach.get_queue()})
tutor.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": tutor.get_queue()})
contentprovider.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": contentprovider.get_queue()})
evaluator.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": evaluator.get_queue()})
learner.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": None})
verifier.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": callback, "input_queue": verifier.get_queue()})

chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()

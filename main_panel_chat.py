import panel as pn
import asyncio
from asyncio import Queue
import autogen
from agents import CoachAgent, TutorAgent, ContentProviderAgent, EvaluatorAgent, LearnerModelAgent, \
                    VerifierAgent, UserProxyAgent, print_messages #, MyGroupChatManager, 
from globals import input_future, initiate_chat_task_created
from avatar import avatar

pn.extension(design="material")



# The LearnerAgent represents the human user in the multi-agent conversation. 
# By setting the sender to learner, we're effectively indicating that the messages 
# originating from the callback function (i.e., user input) are coming from the "learner" 
# perspective within the system.


# async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
#     # Get the UserProxyAgent
#     print("CALLBACK FROM PANEL:  contents= ", contents, '  user= ', user)
#     user_proxy_agent = next((agent for agent in manager.groupchat.agents if isinstance(agent, UserProxyAgent)), None)

#     # If the UserProxyAgent is found, send the message to it
#     if user_proxy_agent:
#         await user_proxy_agent.a_send(
#             {"role": "user", "content": contents}, 
#             recipient=manager
#         )
#     else:
#         print("Warning: UserProxyAgent not found in the groupchat.")

# async def callback(contents: str, user: str, instance: pn.chat.ChatInterface, learner):
#     print("Callback triggered with content:", contents, "from user:", user)
#     print("Sending message to UserProxyAgent")
#     await learner.a_send({"role": "user", "content": contents}) 


initiate_chat_task_created = False
async def delayed_initiate_chat(agent, recipient, message):

    global initiate_chat_task_created
    # Indicate that the task has been created
    initiate_chat_task_created = True

    # Wait for 2 seconds
    await asyncio.sleep(2)

    # Now initiate the chat
    await agent.a_initiate_chat(recipient, message=message)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface, learner, manager):
    
    global initiate_chat_task_created
    global input_future

    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(learner, manager, contents))

    else:
        if input_future and not input_future.done():
            input_future.set_result(contents)
        else:
            print("There is currently no input being awaited.")





# Create agents
learner = UserProxyAgent()  # The human in the loop
coach_agent = CoachAgent()
tutor_agent = TutorAgent()
content_provider_agent = ContentProviderAgent()  
verifier_agent = VerifierAgent()  
evaluator_agent = EvaluatorAgent()  
learner_model_agent = LearnerModelAgent()



# Configure the llm_config for gpt-3.5-turbo
llm_config = {"model": "gpt-3.5-turbo"}  # Hardcoded configuration

# # Group Conversable and Assistant Agents
# conversable_group = autogen.ConversableAgentGroup(
#     agents=[coach_agent, tutor_agent], 
#     llm_config=llm_config
# )

# assistant_group = autogen.AssistantAgentGroup(
#     agents=[content_provider_agent, verifier_agent, evaluator_agent, learner_model_agent],
#     llm_config=llm_config
# )

allowed_agent_transitions = {
    coach_agent: [learner, tutor_agent],
    learner: [coach_agent, tutor_agent],
    tutor_agent: [content_provider_agent, learner, verifier_agent, coach_agent, learner_model_agent],
    content_provider_agent: [tutor_agent],
    evaluator_agent: [verifier_agent, tutor_agent],
    verifier_agent: [tutor_agent, evaluator_agent],
    learner_model_agent: [tutor_agent]
}


# Create the GroupChat with agents and a manager
groupchat = autogen.GroupChat(agents=[coach_agent, tutor_agent, content_provider_agent, evaluator_agent, verifier_agent, 
                                      learner_model_agent,learner], 
                              messages=[],
                              max_round=20,
                              send_introductions=True,
                              #speaker_transitions_type="allowed",
                              #allowed_or_disallowed_speaker_transitions=allowed_agent_transitions,
                               )
manager = autogen.GroupChatManager(groupchat=groupchat)

# Register the reply functions for each agent AFTER on_load
# for agent in groupchat.agents:
#     agent.register_reply([autogen.Agent, None], reply_func=agent.reply_func)
for agent in groupchat.agents:
    agent.register_reply([autogen.Agent, None], reply_func=print_messages)




# Start the chat interface
# Now the coach initiates the conversation asking about the type of math
# async def initiate_chat_delayed():
#     welcome_message = {
#         "role": "assistant",
#         "content": "Hi there! I'm your learning coach. What type of mathematics would you like to learn today?",
#     }

#     # Send the welcome message directly to the UI
#     chat_interface.send(welcome_message["content"], user=coach_agent.name, avatar=avatar.get(coach_agent.name, "👤"))

 
# Panel chat interface
#chat_interface = pn.chat.ChatInterface(callback=callback)  
chat_interface = pn.chat.ChatInterface(callback=lambda contents, user, instance: callback(contents, user, instance, learner, manager))  

# Register chat_interface
coach_agent.set_chat_interface(chat_interface)
tutor_agent.set_chat_interface(chat_interface)


# Schedule the initiate_conversation function to run when the panel is ready.
#pn.state.onload(initiate_chat_delayed)  # Using on_load

chat_interface.send("Send a message!", user="System", respond=False)   
 
# Run the Panel app
chat_interface.servable()

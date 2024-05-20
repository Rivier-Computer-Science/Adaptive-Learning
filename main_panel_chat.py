import panel as pn
import asyncio
from asyncio import Queue
import autogen
from agents import CoachAgent, TutorAgent, ContentProviderAgent, EvaluatorAgent, LearnerModelAgent, \
                    VerifierAgent, UserProxyAgent, MyGroupChatManager, print_messages
from autogen.agentchat import GroupChat, GroupChatManager
#from globals import input_future, initiate_chat_task_created
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

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    print("Callback triggered with content:", contents, "from user:", user)  
    await asyncio.sleep(0.1)

    user_proxy_agent = next((agent for agent in manager.groupchat.agents if isinstance(agent, UserProxyAgent)), None)
    if user_proxy_agent:
        await user_proxy_agent.a_send(
            {"role": "user", "content": contents}, 
            recipient=manager
        )
        print("Message sent to UserProxyAgent")
    else:
        print("Warning: UserProxyAgent not found in the groupchat.")



# Panel chat interface
chat_interface = pn.chat.ChatInterface(callback=callback)  

# Create agents
learner = UserProxyAgent()  # The human in the loop
coach_agent = CoachAgent(chat_interface=chat_interface)
tutor_agent = TutorAgent(chat_interface=chat_interface)
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

# Create the GroupChat with agents and a manager
groupchat = autogen.GroupChat(agents=[coach_agent, tutor_agent, content_provider_agent, evaluator_agent, verifier_agent, 
                                      learner_model_agent,learner], 
                              messages=[])
manager = MyGroupChatManager(groupchat=groupchat)

# Register the reply functions for each agent AFTER on_load
for agent in groupchat.agents:
    agent.register_reply([autogen.Agent, None], reply_func=agent.reply_func)




# Start the chat interface
# Now the coach initiates the conversation asking about the type of math
async def initiate_chat_delayed():
    welcome_message = {
        "role": "assistant",
        "content": "Hi there! I'm your learning coach. What type of mathematics would you like to learn today?",
    }

    # Send the welcome message directly to the UI
    chat_interface.send(welcome_message["content"], user=coach_agent.name, avatar=avatar.get(coach_agent.name, "👤"))

 
# Schedule the initiate_conversation function to run when the panel is ready.
pn.state.onload(initiate_chat_delayed)  # Using on_load




# Run the Panel app
chat_interface.servable()

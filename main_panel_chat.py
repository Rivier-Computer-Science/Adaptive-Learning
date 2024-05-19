import panel as pn
import asyncio
from asyncio import Queue
import sys
sys.path.insert(0, '/home/jglossner/anaconda3/envs/math/lib/python3.11/site-packages') 

import pyautogen
from agents import CoachAgent, TutorAgent, ContentProviderAgent, EvaluatorAgent, LearnerModelAgent, VerifierAgent, print_messages
#from globals import input_future, initiate_chat_task_created
from avatar import avatar

pn.extension(design="material")



# The LearnerAgent represents the human user in the multi-agent conversation. 
# By setting the sender to learner, we're effectively indicating that the messages 
# originating from the callback function (i.e., user input) are coming from the "learner" 
# perspective within the system.


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    # Simulate the human learner's response via the LearnerModelAgent
    await manager.groupchat.agents[-1].a_send(  
        {"role": "user", "content": contents}, 
        recipient=manager
    )


# Panel chat interface
chat_interface = pn.chat.ChatInterface(callback=callback)  

# Create agents
coach_agent = CoachAgent(chat_interface=chat_interface)
tutor_agent = TutorAgent(chat_interface=chat_interface)
content_provider_agent = ContentProviderAgent()  
verifier_agent = VerifierAgent()  
evaluator_agent = EvaluatorAgent()  
learner_model_agent = LearnerModelAgent()

# Configure the llm_config for gpt-3.5-turbo
llm_config = {"model": "gpt-3.5-turbo"}  # Hardcoded configuration

# Group Conversable and Assistant Agents
conversable_group = pyautogen.ConversableAgentGroup(
    agents=[coach_agent, tutor_agent], 
    llm_config=llm_config
)

assistant_group = pyautogen.AssistantAgentGroup(
    agents=[content_provider_agent, verifier_agent, evaluator_agent, learner_model_agent],
    llm_config=llm_config
)

# Create the GroupChat with agents and a manager
groupchat = pyautogen.GroupChat(agents=[coach_agent, tutor_agent, content_provider_agent, evaluator_agent, verifier_agent, learner_model_agent], messages=[])
manager = pyautogen.GroupChatManager(groupchat=groupchat)


# Register the reply functions for each agent
def reply_func(recipient, messages, sender, config):
    print(f"Messages from: {sender.name if sender else 'Unknown'} sent to: {recipient.name if recipient else 'Unknown'} | num messages: {len(messages)}")
    if messages and hasattr(recipient, 'chat_interface'):
        last_message = messages[-1]
        recipient.chat_interface.send(
            last_message['content'],
            user=sender.name if sender else 'Unknown',
            avatar=avatar.get(sender.name, "👤")
        )
    return False, None



# Register the combined reply function for each agent
for agent in groupchat.agents:
    agent.register_reply([pyautogen.Agent, None], reply_func=reply_func)



# Start the chat interface
# Now the coach initiates the conversation asking about the type of math
asyncio.create_task(coach_agent.a_initiate_chat(
    manager, 
    message="Hi there! I'm your learning coach. What type of mathematics would you like to learn today?"
))

# Run the Panel app
chat_interface.servable()

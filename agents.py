import autogen
from autogen.agentchat.groupchat import GroupChat
import os
import asyncio
from globals import input_future

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {
        'model': "gpt-3.5-turbo",
    }
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}



####################################################################
#
# Group Chat
#
##################################################################### 
class CustomGroupChat(GroupChat):
    def __init__(self, agents, messages=None, max_round=20, allow_code_execution=False): 
        super().__init__(agents, messages, max_round)
        self.allow_code_execution = allow_code_execution 

    async def a_run_chat(self, speaker, receiver, max_turn=5):
        self._oai_messages = []
        round_count = 0
        while round_count < max_turn:
            round_count += 1

            # If sending to the group chat manager, ensure the recipient is set to the appropriate agent
            if isinstance(receiver, autogen.GroupChatManager):
                if round_count == 1:
                    receiver = list(filter(lambda x: x != speaker, self.agents))[0]
                else:
                    receiver = speaker.chat_partner

            # speaker sends message
            print(f"{speaker.name} (to {receiver.name}):\n\n{self._oai_messages[-1]['content'] if self._oai_messages else ''}\n\n")
            if round_count == 1 and speaker.system_message:
                self._oai_messages.append({"role": "system", "content": speaker.system_message})

            if self.allow_code_execution:
                reply = await speaker.a_generate_reply(sender=receiver)  
                _, output = await self._process_code(reply, speaker, receiver)

                if reply.get("content") and output is not None:  
                    self._oai_messages.append({"role": "assistant", "content": reply.get("content")})  
                    self._oai_messages.append({"role": "function", "name": reply["function_call"]["name"], "content": output})

            else: 
                reply = await speaker.a_generate_reply(messages=self._oai_messages, sender=self)

                if reply.get("content"):  
                    self._oai_messages.append({"role": "assistant", "content": reply.get("content")}) 

            # stop if termination_msg
            if speaker._is_termination_msg(reply):  # Access the protected method
                break

            # receiver receives and replies
            print(f"{receiver.name} (to {speaker.name}):\n\n{reply.get('content')}\n\n")
            self._oai_messages.append({"role": "user", "content": reply.get("content")})  

            # stop if termination_msg
            if receiver._is_termination_msg(reply):  # Access the protected method
                break

            # Break the loop if it's the first round and the speaker is the coach 
            if round_count == 1 and speaker.name == "Coach":
                break


        return self._oai_messages





####################################################################
#
# Conversable Agents
#
##################################################################### 

class MyConversableAgent(autogen.ConversableAgent):
    def __init__(self, input_queue, chat_interface, **kwargs):
        super().__init__(**kwargs)
        self.chat_interface = chat_interface
        self.input_queue = input_queue

    def get_queue(self):
        return self.input_queue

    async def a_get_human_input(self, prompt: str) -> str:
        self.chat_interface.send(prompt, user="System", respond=False)
        response = await self.input_queue.get()
        return response

    async def a_receive(self, message, sender, request_reply=True, silent=False):
        # If messages is not defined, initialize it to an empty list
        if not hasattr(self, "messages"):
            self.messages = []

        print(f"Received message: {message['content']}")
        self.messages.append(message)  # Add the message to the message history
        reply = await self.a_generate_reply(self.messages, sender, config=None)
        if not silent:
            self.chat_interface.send(reply['content'], user=self.name, avatar=avatar.get(self.name, "👤"), respond=False)
        return reply


class CoachAgent(MyConversableAgent):
    def __init__(self, input_queue, chat_interface):
        super().__init__(
            input_queue=input_queue,
            chat_interface=chat_interface,
            name="Coach",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message="""Coach. You are a Learning Coach, dedicated to supporting and motivating the learner. 
                Your primary goal is to enhance their learning experience and foster a positive learning environment.
                Your responsibilities include:
                1. Build Rapport: Establish a friendly and encouraging connection with the learner.  
                    Make them feel comfortable and supported.
                2. Set Goals and Track Progress: Collaborate with the learner to set achievable learning goals. 
                    Regularly check in on their progress, celebrating milestones and identifying areas for improvement.
                3. Provide Motivation and Encouragement: Offer positive reinforcement and constructive feedback. 
                    Keep the learner engaged and motivated throughout their journey.
                4. Identify Challenges and Offer Solutions: Recognize when the learner is struggling and provide 
                        guidance or resources to overcome obstacles. 
                        Suggest alternative approaches or strategies as needed.
                5. Facilitate Communication: Encourage open communication between the learner, tutor, and other agents. 
                    Ensure everyone is on the same page and working together effectively.
                6. Monitor the Learning Process: Observe interactions between the learner and tutor. 
                    Offer suggestions to the tutor if you notice areas where the learning experience could be enhanced.
                Remember: Your role is to be a supportive coach, not an instructor or evaluator. 
                    Focus on building a positive relationship with the learner and empowering them to take ownership of their learning journey.
                """,
            code_execution_config=False,
            human_input_mode="ALWAYS",
            llm_config=gpt4_config,
        )

    async def a_generate_reply(self, messages, sender):
        print(f"CoachAgent received message: {messages[-1]}")
        latest_message = messages[-1]['content'].lower()  # Get the latest message

        if any(keyword in latest_message for keyword in ['feedback', 'continue']):  
            reply_content = "Great! Let's continue."
        elif any(keyword in latest_message for keyword in ['hello', 'hi']):
            reply_content = "Hi there! I'm your learning coach. How can I help you today?"
        else:
            reply_content = "Let's get started on algebra. What do you need help with?"

        reply = {'content': reply_content, 'name': self.name, 'role': 'assistant'}
        print(f"CoachAgent generated reply: {reply}")
        if hasattr(self, 'chat_interface'):
            self.chat_interface.send(reply['content'], user=self.name, avatar=avatar.get(self.name, "👤"), respond=False)
        return reply



class TutorAgent(MyConversableAgent):
    def __init__(self, input_queue, chat_interface):
        super().__init__(
            input_queue=input_queue,
            chat_interface=chat_interface,
            name="Tutor",
            human_input_mode="ALWAYS",
            llm_config=gpt4_config,
            system_message="""Tutor. You are a personalized tutor. Your role is to guide the learner.  
                1. Analyze the learner's current knowledge and skills.
                2. Select appropriate content for the learner.
                3. Generate questions or tasks to assess the learner's understanding.
                4. Provide clear and constructive feedback.
                5. Adjust the learning path based on the learner's performance.
                """
        )

    async def a_generate_reply(self, messages, sender, config=None):
        print(f"TutorAgent received message: {messages[-1]}")
        reply_content = f"I received your message: {messages[-1]['content']}. Let's start with basic algebra concepts."
        reply = {'content': reply_content, 'name': self.name, 'role': 'assistant'}
        print(f"TutorAgent generated reply: {reply}")
        if hasattr(self, 'chat_interface'):
            self.chat_interface.send(reply['content'], user=self.name, avatar=avatar.get(self.name, "👤"), respond=False)
        return reply



class ContentProviderAgent(MyConversableAgent):
    '''
        Manages the learning content (e.g., texts, exercises, quizzes).
        Retrieves appropriate content based on the learner's progress and the tutor's recommendations.
    '''
    def __init__(self, input_queue, chat_interface):
        super().__init__(
            input_queue = input_queue,
            chat_interface=chat_interface,
            name="ContentProvider",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message="""ContentProvider. You provide learning materials. 
                Retrieve the most suitable content based on the learner's level and the tutor's request.
                """,
        )

class VerifierAgent(MyConversableAgent):
    def __init__(self, input_queue, chat_interface):
        super().__init__(
            input_queue = input_queue,
            chat_interface=chat_interface,
            name="Verifier",
            system_message="""You are a VerifierAgent. Your role is to double-check the information and responses generated by other agents in the system. 
                Key Responsibilities:
                1. Factual Accuracy: Validate the factual accuracy of information provided by the 
                    TutorAgent and ContentProviderAgent, using external sources and your own knowledge base.
                2. Response Consistency: Ensure that responses from the TutorAgent and LearningCoachAgent align 
                    with the learner's needs and the overall learning objectives.
                3. Alternative Perspectives: Offer alternative explanations or approaches to enhance the 
                    learning experience and broaden the learner's understanding.
                4. Identify Biases and Errors:  Detect any biases or errors in the information or responses 
                    generated by other agents, and suggest corrections as needed.
                5. Utilize a Different LLM: Leverage a different Large Language Model (LLM) than the other 
                    agents to provide an independent perspective and cross-validate information.
                6. Suggest Improvements:  If you identify any areas where the quality of information or responses 
                    could be enhanced, offer constructive feedback to the respective agents.
                Remember: Your primary goal is to ensure the accuracy and reliability of the information presented 
                    to the learner, contributing to a high-quality and trustworthy learning experience.
            """,
            llm_config=gpt4_config,
            human_input_mode="NEVER",
        )


####################################################################
#
# Assisstant Agents
#
#####################################################################        

class MyAssisstantAgent(autogen.AssistantAgent):
    def __init__(self, input_queue, **kwargs):
        super().__init__(**kwargs)
        self.input_queue = input_queue

    def get_queue(self):
        return self.input_queue

    async def generate_reply(self, messages, sender, config):  # Override generate_reply
        self.reply_message = self.llm_generate_reply(messages, sender, config)  # Generate the reply
        await self.input_queue.put(self.reply_message)  # Put the reply into the queue
        return self.reply_message
    
    # async def enqueue_reply(self):
    #     await self.input_queue.put(self.reply_message)  # Now awaited in a separate task




class EvaluatorAgent(MyAssisstantAgent):
    '''
        Assesses the learner's answers or task performance.
        Provides feedback to both the learner and the tutor.
    '''
    def __init__(self, input_queue):
        super().__init__(
            input_queue = input_queue,
            name="Evaluator",
            human_input_mode="NEVER",
            system_message="""Evaluator. You evaluate the learner's responses and performance. 
                Provide feedback that highlights strengths and areas for improvement.  """,
            llm_config=gpt4_config,
        )





####################################################################
#
# UserProxy Agents
#
#####################################################################        

class LearnerAgent(autogen.UserProxyAgent):
    '''
        This agent will represent the learner or student.
        It receives learning materials, questions, or tasks.
        It can be configured to provide answers or attempt tasks, either automatically 
            (based on its knowledge level) or by soliciting input from the actual user.
    '''
    def __init__(self):
        super().__init__(
            name="Learner",
            system_message="""Learner. You are the learner. 
                Your goal is to master the subject matter. 
                Engage with the tutor, ask questions, and actively participate in the learning process.""",
            human_input_mode="NEVER",
            #code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
        )



avatar = {
    "Learner": "🎓",        # Graduate cap: Represents the learner
    "Tutor": "👩‍🏫",       # Woman teacher: Represents the tutor
    "ContentProvider": "📚",  # Books: Represents the source of learning materials
    "Evaluator": "✅",       # Checkmark: Represents assessment and feedback
    "Verifier": "🔍",       # Magnifying glass: Represents the verification process
    "Coach": "💪"   # Flexed biceps: Represents support and encouragement
}

# def print_messages(recipient, messages, sender, config):
#     print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
#     content = messages[-1]['content']
#     if hasattr(recipient, 'chat_interface'):
#         if all(key in messages[-1] for key in ['name']):
#             recipient.chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
#         else:
#             recipient.chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
#     return False, None

def print_messages(recipient, messages, sender, config):
    print(f"Messages from: {sender.name if sender else 'Unknown'} sent to: {recipient.name if recipient else 'Unknown'} | num messages: {len(messages)}")  

    if messages: # Check if messages is not empty before accessing the last message
        content = messages[-1]['content']
        user_name = messages[-1].get('name', sender.name if sender else 'Unknown') 
        avatar_icon = avatar.get(user_name, "👤")
        if hasattr(recipient, 'chat_interface'):
            recipient.chat_interface.send(content, user=user_name, avatar=avatar_icon, respond=False)
        print(f"Message sent to chat interface: {content}")
    else:
        print("No messages to send.")
    return False, None
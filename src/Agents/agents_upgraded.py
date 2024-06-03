# High-Level Workflow
#
#     Initialization:
#         The chat interface (e.g., terminal, web interface) is initialized.
#         The CoachAgent (ConversableAgent) welcomes the human user and establishes rapport.
#         The CoachAgent and human user discuss and collaboratively set learning goals.
#         The LearnerModelAgent (AssistantAgent) is initialized to represent the learner's knowledge and skill level.
#
#     Learning Loop:
#         Needs Assessment: The TutorAgent (ConversableAgent) assesses the LearnerModelAgent to estimate the learner's current knowledge.
#         Content Selection:
#             The TutorAgent consults the ContentProviderAgent (AssistantAgent) based on the assessment.
#             The ContentProviderAgent retrieves suitable learning materials.
#         Content Delivery: The TutorAgent presents the content to the human user through the chat interface.
#         Human Input:
#             The TutorAgent poses questions or tasks to the human user via the chat interface.
#             The chat interface captures the human user's responses.
#         Evaluation:
#             The EvaluatorAgent (AssistantAgent) evaluates the human user's response and updates the LearnerModelAgent accordingly.
#             The VerifierAgent (AssistantAgent) double-checks the evaluation for accuracy and offers alternative perspectives if necessary.
#         Feedback:
#             The TutorAgent provides feedback to the human user through the chat interface, focusing on strengths and areas for improvement.
#             The CoachAgent offers motivational support and reinforces positive learning behaviors through the chat interface.
#             The LearnerModelAgent updates its internal representation of the learner's knowledge based on the feedback.
#
#     Adaptation & Progress Tracking:
#         The TutorAgent and CoachAgent continuously analyze the LearnerModelAgent to adapt the learning path and content selection in real time.
#         The CoachAgent engages in periodic conversations with the human user to discuss progress, goals, and challenges.
#
#     Termination:
#         When the learning goals are met or the user decides to end the session, the CoachAgent provides a summary of the learner's progress and offers encouragement.
#
# Example Message Flow:

#     Tutor: "Welcome to the math tutor! Let's get started. What areas of math are you interested in?"
#     Human: "I want to learn about algebra."
#     Tutor (to ContentProvider): "Please provide a question about algebra."
#     ContentProvider (to Tutor): "What is the quadratic formula?"
#     Tutor (to Human): "What is the quadratic formula?"
#     Human: "x equals negative b plus or minus the square root of b squared minus 4ac, all over 2a"
#     Tutor (to Evaluator): "Evaluate the answer: 'x equals negative b plus or minus the square root of b squared minus 4ac, all over 2a'"
#     Evaluator (to Verifier): "The answer is correct."
#     Verifier (to Tutor): "Confirmed: The answer is correct."
#     Tutor (to Human): "That's absolutely right! The quadratic formula is x = (-b ± √(b² - 4ac)) / 2a"

import autogen
#from autogen.agentchat import ChatMessage
import os
import asyncio
from src.globals import input_future
from UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {
        'model': "gpt-3.5-turbo",
    }
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}


####################################################################
#
# GroupChatManager
#
##################################################################### 

# class MyGroupChatManager(autogen.GroupChatManager):
#     async def dispatch(self, message: dict, sender: autogen.Agent, recipient: autogen.Agent) -> None:
#         print("Dispatching message:", message, "from:", sender, "to:", recipient)  # Add debugging print
#         await super().dispatch(message, sender, recipient)



####################################################################
#
# Base Agent (common methods)
#
##################################################################### 

class MyBaseAgent: 
    def find_agent_by_type(self, agent_type):
        for agent in self.groupchat.agents:
            if isinstance(agent, agent_type):
                return agent
        return None  # Return None if agent not found


####################################################################
#
# Conversable Agents
#
##################################################################### 

class MyConversableAgent(autogen.ConversableAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.response_event = asyncio.Event()  # Add an event object
        self.description = self.system_message

    # async def a_get_human_input(self, prompt: str) -> str:
    #     self.chat_interface.send(prompt, user="System", respond=False)
    #     self.response_event.clear()  # Reset the event before waiting

    #     # Wait for a new message to be received through the callback
    #     await self.response_event.wait()

    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        print('AGET!!!!!!')  # or however you wish to display the prompt
        self.chat_interface.send(prompt, user="System", respond=False)
        # Create a new Future object for this input operation if none exists
        if input_future is None or input_future.done():
            input_future = asyncio.Future()

        # Wait for the callback to set a result on the future
        await input_future

        # Once the result is set, extract the value and reset the future for the next input operation
        input_value = input_future.result()
        input_future = None
        return input_value


    def set_chat_interface(self, chat_interface):
        self.chat_interface = chat_interface

    # def reply_func(recipient, messages, sender, config):
    #     if messages and hasattr(recipient, "chat_interface"):
    #         last_message = messages[-1]
    #         if isinstance(sender, CoachAgent):  # Check if sender is of type CoachAgent
    #             recipient.chat_interface.send(  # Send directly to the UI
    #                 last_message["content"],
    #                 user=sender.name if sender else "Unknown",
    #                 avatar=avatar.get(sender.name, "👤"),
    #             )
    #         else:
    #             recipient.chat_interface.send(  # Continue with the existing behavior
    #                 last_message["content"],
    #                 user=sender.name if sender else "Unknown",
    #                 avatar=avatar.get(sender.name, "👤")
    #             )

    #         print(
    #             f"Message from: {sender.name if sender else 'Unknown'} "
    #             f"to: {recipient.name if recipient else 'Unknown'} | "
    #             f"Content: {last_message['content']}"
    #         )

    #     return False, None



class CoachAgent(MyConversableAgent):
    description = """Coach. You are a Learning Coach, dedicated to supporting and motivating the learner. 
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
                """
    def __init__(self):
        super().__init__(
            name="Coach",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message=self.description,
            description=self.description,
            code_execution_config=False,
            human_input_mode="ALWAYS",
            llm_config=gpt4_config,
        )

    # async def on_message(self, message: dict) -> None:
    #     # Check for first round and if message is from CoachAgent
    #     if (self.groupchat.round_idx == 0 and message["sender"] == self) or \
    #     (isinstance(message["sender"], UserProxyAgent)): 
    #         if self.groupchat.round_idx == 0:
    #             # Initial conversation - get the topic of interest
    #             print("Sending welcome message to user")
    #             await self.a_send(
    #                 {
    #                     "role": "assistant",
    #                     "content": "Hi there! I'm your learning coach. What type of mathematics would you like to learn today?",
    #                 },
    #                 recipient=self.chat_interface.user,  
    #             )
    #         else:
    #             # Message from the user - pass topic to TutorAgent
    #             topic_of_interest = message["content"]

    #             # ... (Optional: Update LearnerModelAgent)

    #             # Find TutorAgent using find_agent_by_type (inherited from MyBaseAgent)
    #             tutor_agent = self.find_agent_by_type(TutorAgent)

    #             if tutor_agent:
    #                 print("Sending topic to TutorAgent")
    #                 await self.a_send(
    #                     {
    #                         "role": "user",
    #                         "content": f"The learner is interested in learning about {topic_of_interest}. Please start the tutoring session.",
    #                     },
    #                     recipient=tutor_agent,
    #                 )
    #             else:
    #                 print("Warning: TutorAgent not found in the groupchat.")
    #     else:
    #         print("Message not from UserProxyAgent or self")  # Log message source




    def update_learner_model(self, message):
        """Updates the LearnerModelAgent with relevant information."""
        # This method might update the learner's progress, confidence, etc.
        pass

    def provide_motivation_and_encouragement(self):
        """Generates motivational messages for the learner."""
        # This method could be triggered periodically or based on specific events
        pass

    def provide_constructive_feedback(self):
        """Provides feedback based on the LearnerModelAgent's state."""
        # This method could be triggered after evaluations or at specific intervals
        pass

    def check_in_on_progress(self):
        """Initiates a conversation with the learner to discuss progress and challenges."""
        # This method could be triggered periodically
        pass

    def summarize_progress(self):
        """Provides a summary of the learner's progress at the end of the session."""
        pass


class TutorAgent(MyConversableAgent):
    descriptioin = """Tutor. You are a personalized tutor. Your role is to guide the learner.  
                1. Analyze the learner's current knowledge and skills.
                2. Select appropriate content for the learner.
                3. Generate questions or tasks to assess the learner's understanding.
                4. Provide clear and constructive feedback.
                5. Adjust the learning path based on the learner's performance.
                """
    def __init__(self):
        super().__init__(
            name="Tutor",
            human_input_mode="ALWAYS",
            llm_config=gpt4_config,
            system_message=self.descriptioin,
            description=self.descriptioin
        )
    # async def handle_human_response(self, human_response):
    #     """Handles human response and directs the flow."""
    #     self.learner_answer = human_response  # Store the answer
    #     await self.a_send(
    #         {"role": "user", "content": self.learner_answer},  # Send to Evaluator
    #         recipient=self.groupchat.agents[3]  # Assuming EvaluatorAgent is at index 3
    #     )

    # async def handle_verifier_confirmation(self, message):
    #     """Handles confirmation from VerifierAgent."""
    #     # Assuming EvaluatorAgent is at index 3 in your groupchat
    #     evaluator_answer = self.groupchat.agents[3].last_message()["content"]  

    #     await self.a_send(
    #         {"role": "assistant", "content": evaluator_answer},
    #         recipient=self.chat_interface.user
    #     )

    #     # You can potentially ask the ContentProvider for a new question here
    #     # and continue the loop

    # async def on_message(self, message: dict) -> None:
    #     if (message["sender"] == self.find_agent_by_type(CoachAgent) and
    #         "interested in learning about" in message["content"]):
    #         await self.a_send(
    #             {"role": "user", "content": "Please provide a question."},
    #             recipient=self.find_agent_by_type(ContentProviderAgent)
    #         )
    #     elif message["sender"] == self.find_agent_by_type(ContentProviderAgent):
    #         self.question = message["content"]
    #         await self.a_send(
    #             {"role": "assistant", "content": self.question},
    #             recipient=self.chat_interface.user
    #         )
    #     elif message["sender"] == self.find_agent_by_type(VerifierAgent):
    #         await self.handle_verifier_confirmation(message)
    #     elif message["sender"] == self.chat_interface.user:
    #         await self.handle_human_response(message["content"])


                

####################################################################
#
# Assisstant Agents
#
#####################################################################        

class MyAssisstantAgent(autogen.AssistantAgent, MyBaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    
    # Add reply_func for assistant agents (modify as needed)
    def reply_func(self, recipient, messages, sender, config):
        # Do nothing (just needed for registration)
        return True, None  

class ContentProviderAgent(MyAssisstantAgent):
    '''
        Manages the learning content (e.g., texts, exercises, quizzes).
        Retrieves appropriate content based on the learner's progress and the tutor's recommendations.
    '''
    description = """ContentProvider. You provide learning materials. 
                Retrieve the most suitable content based on the learner's level and the tutor's request.
                """
    def __init__(self):
        super().__init__(
             name="ContentProvider",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message=self.description,
            description = self.description,
        )

    # async def on_message(self, message: dict) -> None:
    #     if (
    #         message["sender"] == self.find_agent_by_type(TutorAgent) 
    #         and message["content"] == "Please provide a question."
    #     ):
    #         question = self.generate_question()  # Replace with your question generation logic
    #         await self.a_send(
    #             {"role": "assistant", "content": question},
    #             recipient=message.sender  # Send back to TutorAgent
    #         )




class VerifierAgent(MyAssisstantAgent):
    descriptioin = """You are a VerifierAgent. Your role is to double-check the information and responses generated by other agents in the system. 
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
            """
    def __init__(self):
        super().__init__(
             name="Verifier",
            system_message=self.descriptioin,
            description=self.descriptioin,
            llm_config=gpt4_config,
            human_input_mode="NEVER",
        )

    # async def on_message(self, message: dict) -> None:
    #     if message["sender"] == self.find_agent_by_type(EvaluatorAgent):  
    #         evaluation_result = message["content"]
    #         verification_result = self.verify_evaluation(evaluation_result)
    #         await self.a_send(
    #             {"role": "assistant", "content": verification_result},
    #             recipient=self.find_agent_by_type(TutorAgent)
    #         )



class EvaluatorAgent(MyAssisstantAgent):
    '''
        Assesses the learner's answers or task performance.
        Provides feedback to both the learner and the tutor.
    '''
    description = """Evaluator. You evaluate the learner's responses and performance. 
                Provide feedback that highlights strengths and areas for improvement.  """
    
    def __init__(self):
        super().__init__(
             name="Evaluator",
            human_input_mode="NEVER",
            system_message=self.description,
            description=self.description,
            llm_config=gpt4_config,
        )

    # async def on_message(self, message: dict) -> None:
    #     if message["sender"] == self.find_agent_by_type(TutorAgent):  
    #         learner_answer = message["content"]
    #         evaluation_result = self.evaluate_answer(learner_answer)  
    #         await self.a_send(
    #             {"role": "assistant", "content": evaluation_result},
    #             recipient=self.find_agent_by_type(VerifierAgent) 
    #         )




class LearnerModelAgent(MyAssisstantAgent):
    '''
        This agent will represent the learner or student.
        It receives learning materials, questions, or tasks.
        It can be configured to provide answers or attempt tasks, either automatically 
            (based on its knowledge level) or by soliciting input from the actual user.
    '''
    description = """You are the LearnerModelAgent. 
                Your purpose is to model the knowledge and skills of a human learner. 
                Initially, you have no information about the learner's abilities. 
                As you receive feedback and observe the learner's responses, you will update your 
                    internal representation of their knowledge.
                Focus on accurately reflecting the learner's strengths and weaknesses so that the system 
                    can personalize the learning experience effectively.
            """
    def __init__(self):
        super().__init__(
            name="LearnerModel",
            system_message=self.description,
            description=self.description,
            human_input_mode="NEVER",
            #code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
        )

    # async def on_message(self, message: dict) -> None:
    #     # The LearnerModelAgent doesn't need to actively respond to messages, 
    #     # but it can update its internal model based on the conversation.
    #     self.update_learner_model(message)  # Update the learner model based on the message (logic not shown)



####################################################################
#
# User Proxy Agent
#
#####################################################################        


class UserProxyAgent(autogen.UserProxyAgent, MyBaseAgent):
    description="You are the human user interacting with the system. Forward all messages you receive to the CoachAgent."
    def __init__(self):        
        super().__init__(
            name="UserProxy",
            system_message=self.description,
            description=self.description,
            human_input_mode="ALWAYS",
        )
        # Add a reply function for UserProxyAgent
    # def reply_func(self, recipient, messages, sender, config):
    #     # Do nothing (just needed for registration)
    #     return True, None  
    
    #     # Send first message to coach. All subsequent to tutor.
    # # Send first message to coach. All subsequent to tutor.
    # def send_message(self, message: dict, recipient):
    #     if self.groupchat.round_idx == 1 and recipient is None:  # Send the first message to the coach
    #         recipient = self.find_agent_by_type(CoachAgent)
    #     else:
    #         recipient = self.find_agent_by_type(LearnerModelAgent)

    #     # Error handling in case the agent is not found
    #     if recipient is None:
    #         print(f"Warning: Recipient agent not found for message: {message}")
    #         return  # Don't send the message if recipient is not found
    #     print(f"Message sent to: {recipient.name if recipient else 'Unknown'}")
    #     # Modify the message before sending it to the recipient to indicate that it is from the user.
    #     modified_message = {"role": "user", "content": message["content"]}

    #     return recipient.send_message(modified_message)  # Send modified message to recipient.










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
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


import autogen
from autogen.agentchat.groupchat import GroupChat
import os
import asyncio
#from globals import input_future
from avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {
        'model': "gpt-3.5-turbo",
    }
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}



####################################################################
#
# Conversable Agents
#
##################################################################### 

class MyConversableAgent(autogen.ConversableAgent):
    def __init__(self, chat_interface, **kwargs):
        super().__init__(**kwargs)
        self.chat_interface = chat_interface
        self.response_event = asyncio.Event()  # Add an event object

    async def a_get_human_input(self, prompt: str) -> str:
        self.chat_interface.send(prompt, user="System", respond=False)
        self.response_event.clear()  # Reset the event before waiting

        # Wait for a new message to be received through the callback
        await self.response_event.wait()



class CoachAgent(MyConversableAgent):
    def __init__(self, chat_interface):
        super().__init__(
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


class TutorAgent(MyConversableAgent):
    def __init__(self, chat_interface):
        super().__init__(
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


####################################################################
#
# Assisstant Agents
#
#####################################################################        

class MyAssisstantAgent(autogen.AssistantAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    


class ContentProviderAgent(MyAssisstantAgent):
    '''
        Manages the learning content (e.g., texts, exercises, quizzes).
        Retrieves appropriate content based on the learner's progress and the tutor's recommendations.
    '''
    def __init__(self):
        super().__init__(
             name="ContentProvider",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message="""ContentProvider. You provide learning materials. 
                Retrieve the most suitable content based on the learner's level and the tutor's request.
                """,
        )

class VerifierAgent(MyAssisstantAgent):
    def __init__(self):
        super().__init__(
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


class EvaluatorAgent(MyAssisstantAgent):
    '''
        Assesses the learner's answers or task performance.
        Provides feedback to both the learner and the tutor.
    '''
    def __init__(self):
        super().__init__(
             name="Evaluator",
            human_input_mode="NEVER",
            system_message="""Evaluator. You evaluate the learner's responses and performance. 
                Provide feedback that highlights strengths and areas for improvement.  """,
            llm_config=gpt4_config,
        )



class LearnerModelAgent(MyAssisstantAgent):
    '''
        This agent will represent the learner or student.
        It receives learning materials, questions, or tasks.
        It can be configured to provide answers or attempt tasks, either automatically 
            (based on its knowledge level) or by soliciting input from the actual user.
    '''
    def __init__(self):
        super().__init__(
            name="LearnerModel",
            system_message="""You are the LearnerModelAgent. 
                Your purpose is to model the knowledge and skills of a human learner. 
                Initially, you have no information about the learner's abilities. 
                As you receive feedback and observe the learner's responses, you will update your 
                    internal representation of their knowledge.
                Focus on accurately reflecting the learner's strengths and weaknesses so that the system 
                    can personalize the learning experience effectively.
            """,
            human_input_mode="NEVER",
            #code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
        )



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
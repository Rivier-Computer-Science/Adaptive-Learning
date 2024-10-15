import asyncio

import autogen as autogen
import panel as pn
import param

import src.Agents.agents as agents
from src import globals as globals
from src.UI.avatar import avatar



import asyncio
import re


class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)
        
        pn.extension(design="material")

        self.groupchat_manager = groupchat_manager
 
        # Learn tab
        self.LEARN_TAB_NAME = "LearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback, name=self.LEARN_TAB_NAME)

        # Dashboard tab
        self.dashboard_view = pn.pane.Markdown(f"Total messages: {len(self.groupchat_manager.groupchat.messages)}")
        
        # Progress tab
        self.progress_text = pn.pane.Markdown(f"**Student Progress**")
        self.progress = 0
        self.max_questions = 10
        self.progress_bar = pn.widgets.Progress(name='Progress', value=self.progress, max=self.max_questions)        
        self.progress_info = pn.pane.Markdown(f"{self.progress} out of {self.max_questions}", width=60)

        # Model tab. Capabilities for the LearnerModel
        self.MODEL_TAB_NAME = "ModelTab"
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback, name=self.MODEL_TAB_NAME)
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)
        self.is_model_tab = False
        
        self.promptC=PromptBasedLearning(groupchat_manager=groupchat_manager)

        # TODO: Consider whether groupchat_manager or this class should manage the chat_interface
        #       Currently, I have placed it in CustomGroupChatManager
        self.groupchat_manager.chat_interface = self.learn_tab_interface  # default chat tab

    ############ tab1: Learn interface
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            All panel callbacks for the learn tab come through this callback function
            Because there are two chat panels, we need to save the instance
            Then, when update is called, check the instance name
        '''                      
        self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, contents))  
        else:
            if globals.input_future and not globals.input_future.done():                
                globals.input_future.set_result(contents)                 
            else:
                print("No input being awaited.")
    
    def update_learn_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name is not self.LEARN_TAB_NAME: return
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.learn_tab_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.learn_tab_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
        
    ########## tab2: Dashboard
    def update_dashboard(self):
        self.dashboard_view.object = f"Total messages: {len(self.groupchat_manager.groupchat.get_messages())}"

    ########### tab3: Progress
    def update_progress(self, contents, user):
        # Parse the agent's output for keywords                 
        if user == "LevelAdapterAgent":            
            pattern = re.compile(r'\b(correct|correctly|verified|yes|well done|excellent|successfully|that\'s right|good job|excellent|right|good|affirmative)\b', re.IGNORECASE)            
            is_correct = pattern.search(contents)
            if is_correct:
               print("################ CORRECT ANSWER #################")
               if self.progress < self.max_questions:  
                    self.progress += 1
                    self.progress_bar.value = self.progress
                    self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"

            else:
                print("################ WRONG ANSWER #################")

    ########## Model Tab
    async def handle_button_update_model(self, event=None):
        self.groupchat_manager.chat_interface = self.model_tab_interface
        await self.a_update_model()
     
    async def a_update_model(self):
        '''
            This is a long latency operation therefore async
        '''
        if self.groupchat_manager.chat_interface.name is not self.MODEL_TAB_NAME: return
        messages = self.groupchat_manager.groupchat.get_messages()
        for m in messages:
            agents.learner_model.send(m, recipient=agents.learner_model, request_reply=False)
        await agents.learner_model.a_send("What is the student's current capabilities", recipient=agents.learner_model, request_reply=True)
        response = agents.learner_model.last_message(agent=agents.learner_model)["content"]
        self.model_tab_interface.send(response, user=agents.learner_model.name,avatar=avatar[agents.learner_model.name])


    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Receive any input from the ChatInterface of the Model tab
        '''
        self.groupchat_manager.chat_interface = instance
        if user == "System" or user == "User":
            response = agents.learner_model.last_message(agent=agents.learner_model)["content"]
            self.learn_tab_interface.send(response, user=agents.learner_model.name,avatar=avatar[agents.learner_model.name])
    

    ########## Create the "windows" and draw the tabs
    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Learn", pn.Column(self.learn_tab_interface)
                    ),
            ("Dashboard", pn.Column(self.dashboard_view)
                    ),
            ("Progress", pn.Column(
                    self.progress_text,
                    pn.Row(                        
                        self.progress_bar,
                        self.progress_info))
                    ),
            ("Model", pn.Column(
                      pn.Row(self.button_update_learner_model),
                      pn.Row(self.model_tab_interface))
                    ),   
             ("Prompt-Based Learning", self.promptC.draw_view()),  # New tab added here
    
        )
        return tabs

    @property
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager



class PromptBasedLearning(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)
        self.groupchat_manager = groupchat_manager
        
        self.PROMPT_TAB_NAME="PromptTab"

        # Text input for selecting the topic
        self.topic_input = pn.widgets.TextInput(placeholder="Enter topic...", width=300)
        
        # Button to run the function when the topic is given
        self.run_button = pn.widgets.Button(name="Select Topic", button_type="primary")
        self.run_button.on_click(self.on_topic_select)

        # Chat interface for the prompt-based learning
        self.prompt_chat_name = "PromptTab"
        self.prompt_chat_interface = pn.chat.ChatInterface(callback=self.a_prompt_tab_callback, name=self.prompt_chat_name)
        self.groupchat_manager.chat_interface = self.prompt_chat_interface
        
        # Progress tracker
        self.progress = 0  # Track the student's progress
        self.progress_display = pn.widgets.Progress(name="Learning Progress", value=self.progress, max=100)
        self.progress_info = pn.pane.Markdown(f"{self.progress} out of 100", width=60)


        # Layout: Combine the text input, button, progress tracker, and chat interface
        self.layout = pn.Column(self.topic_input, self.run_button, pn.Row(self.progress_display,self.progress_info), self.prompt_chat_interface)

    async def a_prompt_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        """Handle chat interactions, including decision tracking."""
        self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")
                
        # Track user decision and response
        self.track_decision(contents,user)

    def update_prompt_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name is not self.PROMPT_TAB_NAME: return
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.learn_tab_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.learn_tab_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)

    def track_decision(self, user_response: str,user):
        """Track user decisions and adapt future prompts."""
        # Example decision tracking logic
        # Here, we simulate checking the user's response and adjusting progress
        if user == "LevelAdapterAgent":            
            pattern = re.compile(r'\b(correct|correctly|verified|yes|well done|excellent|successfully|that\'s right|good job|excellent|right|good|affirmative)\b', re.IGNORECASE)            
            is_correct = pattern.search(user_response)
            if is_correct:
               print("################ CCORRECT ANSWER #################")
               if self.progress < 100:
                    self.progress += 10
                    self.progress_display.value = self.progress
                    self.progress_info.object = f"**{self.progress} out of 100**"

            else:
                print("################ WRONG ANSWER #################")


        # Adapt future questions based on progress
        self.adapt_learning_path()

    def adapt_learning_path(self):
        """Adjust future prompts based on the student's performance."""
        if self.progress >= 80:
            print("Student is doing well! Increase difficulty.")
            # Adapt prompt to increase difficulty
            con = "Ask more advanced fill-in-the-blank questions based on the student's skill level."
        elif self.progress < 50:
            print("Student needs more practice. Lower difficulty.")
            # Adapt prompt to lower difficulty
            con = "Ask simpler fill-in-the-blank questions to help the student improve."
        else:
            print("Student is progressing steadily.")
            con = "Continue with moderate difficulty questions."

        # Initiate adapted chat based on learning path
        self.groupchat_manager.chat_interface = self.prompt_chat_interface
        asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, con))

    def on_topic_select(self, event):
        """Handle topic selection."""
        topic = self.topic_input.value
        if topic:
            # Process the selected topic (You can call a specific function based on the topic here)
            print(f"Topic selected: {topic}")
            con = "Ask question to student in the fill-in-the-blank format on topic " + topic + ". Also consider the student's skill to give better questions."
            self.groupchat_manager.chat_interface = self.prompt_chat_interface
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, con))
        
            # Clear the input field after selecting the topic
            self.topic_input.value = ""

    def update_prompt_tab(self, recipient, messages, sender, config):
        """Update chat with new messages."""
        if self.groupchat_manager.chat_interface.name is not self.prompt_chat_name:
            return
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.prompt_chat_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.prompt_chat_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
      
    def draw_view(self):
        """Return the layout for the prompt-based learning tab."""
        return self.layout

    @property
    def groupchat_manager(self) -> autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager



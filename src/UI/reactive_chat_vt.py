

import param
import panel as pn
import asyncio
import re
import autogen as autogen
from src import globals as globals
from src.Agents.agents import AgentKeys

#from src.UI.reactive_chat23 import StudentChat


class ReactiveChat(param.Parameterized):
    def __init__(self, agents_dict,  avatars=None, groupchat_manager=None, **params):
        super().__init__(**params)
        
        pn.extension(design="material")

        self.agents_dict = agents_dict
        self.avatars = avatars
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
        self.button_find_jobs = pn.widgets.Button(name='Find Jobs', button_type='primary')
        self.button_find_jobs.on_click(self.handle_button_find_jobs)
        self.is_model_tab = False

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
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(self.agents_dict[AgentKeys.TUTOR.value], self.groupchat_manager, contents))  
        else:
            if globals.input_future and not globals.input_future.done():                
                globals.input_future.set_result(contents)                 
            else:
                print("No input being awaited.")
    
    def update_learn_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name is not self.LEARN_TAB_NAME: return
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.learn_tab_interface.send(last_content, user=messages[-1]['name'], avatar=self.avatars[messages[-1]['name']], respond=False)
        else:
            self.learn_tab_interface.send(last_content, user=recipient.name, avatar=self.avatars[recipient.name], respond=False)
        
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
            self.agents_dict[AgentKeys.LEARNER_MODEL.value].send(m, recipient=self.agents_dict[AgentKeys.LEARNER_MODEL.value], request_reply=False)
        await self.agents_dict[AgentKeys.LEARNER_MODEL.value].a_send("What is the student's current capabilities", recipient=self.agents_dict[AgentKeys.LEARNER_MODEL.value], request_reply=True)
        response = self.agents_dict[AgentKeys.LEARNER_MODEL.value].last_message(agent=self.agents_dict[AgentKeys.LEARNER_MODEL.value])["content"]
        self.model_tab_interface.send(response, user=self.agents_dict[AgentKeys.LEARNER_MODEL.value].name,avatar=self.avatars[self.agents_dict[AgentKeys.LEARNER_MODEL.value].name])

    async def handle_button_find_jobs(self, event=None):
        self.groupchat_manager.chat_interface = self.model_tab_interface
        await self.a_find_jobs()

    async def a_find_jobs(self):
        '''
            Ask the agents to find jobs based on the learner model
        '''
        if self.groupchat_manager.chat_interface.name is not self.MODEL_TAB_NAME: return
        messages = self.groupchat_manager.groupchat.get_messages()
        for m in messages:
            self.agents_dict[AgentKeys.JOB_FINDER.value].send(m, recipient=self.agents_dict[AgentKeys.JOB_FINDER.value], request_reply=False)
        await self.agents_dict[AgentKeys.JOB_FINDER.value].a_send("Based on the StudentAgent's capabilities, recommend jobs to apply for.", recipient=self.agents_dict[AgentKeys.JOB_FINDER.value], request_reply=True)
        response = self.agents_dict[AgentKeys.JOB_FINDER.value].last_message(agent=self.agents_dict[AgentKeys.JOB_FINDER.value])["content"]
        self.model_tab_interface.send(response, user=self.agents_dict[AgentKeys.JOB_FINDER.value].name,avatar=self.avatars[self.agents_dict[AgentKeys.JOB_FINDER.value].name])


    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Receive any input from the ChatInterface of the Model tab
        '''
        self.groupchat_manager.chat_interface = instance
        if user == "System" or user == "User":
            response = self.agents_dict[AgentKeys.LEARNER_MODEL.value].last_message(agent=self.agents_dict[AgentKeys.LEARNER_MODEL.value])["content"]
            self.learn_tab_interface.send(response, user=self.agents_dict[AgentKeys.LEARNER_MODEL.value].name,avatar=self.avatars[self.agents_dict[AgentKeys.LEARNER_MODEL.value].name])
    

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
                      pn.Row(self.button_find_jobs),
                      pn.Row(self.model_tab_interface))
                    ),     

        )
        return tabs

    @property
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager


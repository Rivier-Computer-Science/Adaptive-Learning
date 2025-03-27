import param
import panel as pn
import asyncio
import re
import autogen as autogen
from src import globals as globals
from src.Agents.history_agents import AgentKeys
from src.Agents.shared_data import set_selected_country, get_selected_country

import logging

class ReactiveChat(param.Parameterized):
    def __init__(self, agents_dict, avatars=None, groupchat_manager=None, **params):
        logging.info("Beginning Reactive Chat Window Initialization")
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

        # Model tab
        self.MODEL_TAB_NAME = "ModelTab"
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback, name=self.MODEL_TAB_NAME)
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)
        self.is_model_tab = False

        # Assign chat interface to group chat manager
        self.groupchat_manager.chat_interface = self.learn_tab_interface

        logging.info("Reactive Chat Window Initialized")

    ########## Learn Tab ##########
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Handles user input and extracts country names dynamically.
        '''
        if isinstance(contents, tuple):
            logging.error(f"Contents is a tuple, which is unexpected: {contents}")

        logging.debug(f"Entered with contents type= {type(contents)} and Contents= {contents} and instance= {instance}")                  
        self.groupchat_manager.chat_interface = instance

        self.detect_country(contents)

        if not globals.initiate_chat_task_created:
            logging.debug("calling asyncio.create_task() ")
            try:
                asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(self.agents_dict[AgentKeys.TUTOR.value], self.groupchat_manager, contents))  
                logging.info("COMPLETED asyncio.create_task(groupchat_manager.delayed_initiate_chat) ")
            except Exception as e:
                logging.error("Exception occurred while trying to create task delayed_initiate_chat")
                raise
        else:
            if globals.input_future and not globals.input_future.done():
                logging.debug("globals.input_future.done() not completed")     
                logging.debug(f"Type of contents: {type(contents)}, Contents: {contents}")           
                globals.input_future.set_result(contents)                 
                logging.debug(f"Setting globals.input_future.set_results(contents) with contents = {contents}")
            else:
                print("No input being awaited.")
    
    def detect_country(self, text):
        '''
            Extracts the country name from user input and updates `shared_data.py`.
        '''
        country_list = ["India", "USA", "Canada", "UK", "Germany", "France", "Australia"]
        for country in country_list:
            if country.lower() in text.lower():
                set_selected_country(country)
                logging.info(f"Detected country: {country}")
                return country
        return None

    def update_learn_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name != self.LEARN_TAB_NAME:
            return

        last_content = messages[-1]['content']
        try: 
            if 'name' in messages[-1]:
                self.learn_tab_interface.send(
                    last_content, 
                    user=messages[-1]['name'], 
                    avatar=self.avatars.get(messages[-1]['name'], None),
                    respond=False
                )
            else:
                self.learn_tab_interface.send(
                    last_content, 
                    user=recipient.name, 
                    avatar=self.avatars.get(recipient.name, None),
                    respond=False
                )
        except Exception as e:
            logging.exception("Error in update_learn_tab: Possibly a bad avatars dictionary")
            raise
        
    ########## Dashboard Tab ##########
    def update_dashboard(self):
        self.dashboard_view.object = f"Total messages: {len(self.groupchat_manager.groupchat.get_messages())}"

    ########## Progress Tab ##########
    def update_progress(self, contents, user):
        if isinstance(contents, tuple):
            logging.error(f"Contents is a tuple, which is unexpected: {contents}")

        if user == "LevelAdapterAgent":            
            pattern = re.compile(r'\b(correct|verified|yes|excellent|right|good job|affirmative)\b', re.IGNORECASE)            
            if pattern.search(contents):
                if self.progress < self.max_questions:  
                    self.progress += 1
                    self.progress_bar.value = self.progress
                    self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"

    ########## Model Tab ##########
    async def handle_button_update_model(self, event=None):
        self.groupchat_manager.chat_interface = self.model_tab_interface
        await self.a_update_model()
     
    async def a_update_model(self):
        '''
            Long latency operation for updating the learner model.
        '''
        if self.groupchat_manager.chat_interface.name != self.MODEL_TAB_NAME:
            return
        
        messages = self.groupchat_manager.groupchat.get_messages()
        for m in messages:
            self.agents_dict[AgentKeys.LEARNER_MODEL.value].send(
                m, 
                recipient=self.agents_dict[AgentKeys.LEARNER_MODEL.value], 
                request_reply=False
            )

        await self.agents_dict[AgentKeys.LEARNER_MODEL.value].a_send(
            "What is the student's current capabilities", 
            recipient=self.agents_dict[AgentKeys.LEARNER_MODEL.value], 
            request_reply=True
        )

        response = self.agents_dict[AgentKeys.LEARNER_MODEL.value].last_message(
            agent=self.agents_dict[AgentKeys.LEARNER_MODEL.value]
        )["content"]

        self.model_tab_interface.send(
            response, 
            user=self.agents_dict[AgentKeys.LEARNER_MODEL.value].name,
            avatar=self.avatars.get(self.agents_dict[AgentKeys.LEARNER_MODEL.value].name, None)
        )

    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Receive any input from the Model tab chat interface.
        '''
        if isinstance(contents, tuple):
            logging.error(f"Contents is a tuple, which is unexpected: {contents}")

        self.groupchat_manager.chat_interface = instance
        if user in ["System", "User"]:
            response = self.agents_dict[AgentKeys.LEARNER_MODEL.value].last_message(
                agent=self.agents_dict[AgentKeys.LEARNER_MODEL.value]
            )["content"]

            self.learn_tab_interface.send(
                response, 
                user=self.agents_dict[AgentKeys.LEARNER_MODEL.value].name,
                avatar=self.avatars.get(self.agents_dict[AgentKeys.LEARNER_MODEL.value].name, None)
            )

    ########## Draw View ##########
    def draw_view(self):         
        return pn.Tabs(
            ("Learn", pn.Column(self.learn_tab_interface)),
            ("Dashboard", pn.Column(self.dashboard_view)),
            ("Progress", pn.Column(self.progress_text, pn.Row(self.progress_bar, self.progress_info))),
            ("Model", pn.Column(pn.Row(self.button_update_learner_model), pn.Row(self.model_tab_interface))),
        )

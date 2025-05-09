import param
import panel as pn
import asyncio
import re
import autogen as autogen
from src import globals as globals
from src.Agents.language_agents import AgentKeys  # Updated import

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

        
        # Model tab. Capabilities for the LearnerModel
        self.MODEL_TAB_NAME = "ModelTab"
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback, name=self.MODEL_TAB_NAME)
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)
        self.is_model_tab = False

        # TODO: Consider whether groupchat_manager or this class should manage the chat_interface
        #       Currently, I have placed it in CustomGroupChatManager
        self.groupchat_manager.chat_interface = self.learn_tab_interface  # default chat tab

        logging.info("Reactive Chat Window Initialized")

    ############ tab1: Learn interface
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            All panel callbacks for the learn tab come through this callback function
            Because there are two chat panels, we need to save the instance
            Then, when update is called, check the instance name
        '''    
        if isinstance(contents, tuple):
            logging.error(f"Contents is a tuple, which is unexpected: {contents}")

        logging.debug(f"Entered with contents type= {type(contents)} and Contents= {contents} and instance= {instance}")                  
        self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            logging.debug("calling asyncio.create_task() ")
            try:
                #Do not use await here or it will lock the panel tab and not allow further student input
                asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(self.agents_dict[AgentKeys.TUTOR.value], self.groupchat_manager, contents))  
                logging.info("COMPLETED asyncio.create_task(groupchat_manager.delayed_initiate_chat) ")
            except Exception as e:
                logging.error("Exception occured while trying to create task delayed_initiate_chat")
                raise
            
        else:
            if globals.input_future and not globals.input_future.done():
                logging.debug("globals.input_future.done() not completed")     
                logging.debug(f"Type of contents: {type(contents)}, Contents: {contents}")           
                globals.input_future.set_result(contents)                 
                logging.debug(f"Setting globals.input_future.set_results(contents) with contents = {contents}")
            else:
                print("No input being awaited.")
    
    def update_learn_tab(self, recipient, messages, sender, config):
        logging.debug(f"chat_interface.name = {self.groupchat_manager.chat_interface.name} and tab name= {self.LEARN_TAB_NAME} ")
        if self.groupchat_manager.chat_interface.name is not self.LEARN_TAB_NAME: return
        logging.debug(f"Called with messages=  \n {messages}")
        last_content = messages[-1]['content']
        try: 
            if all(key in messages[-1] for key in ['name']):
                logging.debug(f"learn_tab_interface.send( last_content: {last_content} \n user={messages[-1]['name']} \n avatars={self.avatars[messages[-1]['name']]}")
                self.learn_tab_interface.send(last_content, user=messages[-1]['name'], avatar=self.avatars[messages[-1]['name']], respond=False)
                logging.debug("learn_tab updated")
            else:
                logging.debug(f"learn_tab_interface.send( last_content: {last_content} \n user={recipient.name} \n avatars={self.avatars[recipient.name]}")
                self.learn_tab_interface.send(last_content, user=recipient.name, avatar=self.avatars[recipient.name], respond=False)
                logging.debug('learn_tab updated')
        except Exception as e:
            logging.exception("This is possibly due toa a bad avatars dictionary")
            print("EXCEPTION: reactive_chat24_language.py update_learn_tab() writing learn_tab_interface.send() caused an exception ")
            print("This is possibly due to a bad avatars dictionary")
            print(e)
            raise
        
    ########## tab2: Dashboard
    def update_dashboard(self):
        self.dashboard_view.object = f"Total messages: {len(self.groupchat_manager.groupchat.get_messages())}"

    ########### tab3: Progress
    def update_progress(self, contents, user):
        if isinstance(contents, tuple):
            logging.error(f"Contents is a tuple, which is unexpected: {contents}")

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

    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Receive any input from the ChatInterface of the Model tab
        '''
        if isinstance(contents, tuple):
            logging.error(f"Contents is a tuple, which is unexpected: {contents}")

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
                      pn.Row(self.model_tab_interface))
                    ),     

        )
        return tabs

    @property
    def groupchat_manager(self) -> autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager
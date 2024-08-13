import autogen
import panel as pn
import openai
import os
import time
import re
import asyncio
from typing import List, Dict
import param
import logging
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.avatar import avatar

# logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

globals.input_future = None
    
fsm = FSM(agents_dict)

# Create the GroupChat with agents and a manager
groupchat = CustomGroupChat(agents=list(agents_dict.values()), 
                              messages=[],
                              max_round=30,
                              send_introductions=True,
                              speaker_selection_method=fsm.next_speaker_selector
                              )


manager = CustomGroupChatManager(groupchat=groupchat,
                                filename=progress_file_path, 
                                is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0 )    

import panel as pn
import param
from typing import List, Dict

class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat, **params):
        super().__init__(**params)
        self.groupchat = groupchat

        # Learn tab
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback)

        # Dashboard tab
        self.dashboard_view = pn.pane.Markdown(f"Total messages: {len(self.groupchat.messages)}")
        
        # Progress tab
        self.progress_text = pn.pane.Markdown(f"**Student Progress**")
        self.progress = 0
        self.max_questions = 10
        self.progress_bar = pn.widgets.Progress(name='Progress', value=self.progress, max=self.max_questions)        
        self.progress_info = pn.pane.Markdown(f"{self.progress} out of {self.max_questions}", width=60)

        # Model tab. Capabilities for the LearnerModel
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback)
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)
        self.is_model_tab = False
        #self.learner_model_interface.send("What is the student's current capabilities", user="System", respond=True)

    ############ tab1: Learn interface
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        if not globals.initiate_chat_task_created:
            asyncio.create_task(manager.delayed_initiate_chat(tutor, manager, contents))  
        else:
            if globals.input_future and not globals.input_future.done():
                self.is_learn_tab = True
                globals.input_future.set_result(contents)                     
            else:
                print("No input being awaited.")
    
    def update_learn_tab(self, recipient, messages, sender, config):
        if self.is_model_tab: return 

        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.learn_tab_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.learn_tab_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
        
    ########## tab2: Dashboard
    def update_dashboard(self):
        self.dashboard_view.object = f"Total messages: {len(groupchat.get_messages())}"

    ########### tab3: Progress
    def update_progress(self, contents, user):
        # Parse the agent's output for keywords                 
        if user == "LevelAdapterAgent":            
            pattern = re.compile(r'\b(correct|correctly|verified|yes|well done|excellent|successfully|that\'s right|good job|excellent|right|good|affirmative)\b', re.IGNORECASE)            
            is_correct = pattern.search(contents)
            if is_correct:
               print("################ CORRECT ANSWER #################")
               if self.progress < 10:  # Ensure we don't exceed the max progress
                    self.progress += 1
                    self.progress_bar.value = self.progress
                    self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"

            else:
                print("################ WRONG ANSWER #################")

    ########## tab4: Learner Model
    async def handle_button_update_model(self, event=None):
        self.is_model_tab = True
        await self.a_update_model()
        self.is_learn_tab = False

    async def a_update_model(self):
        '''
            This is a long latency operation therefore async
        '''
        if not self.is_model_tab: return

        messages = groupchat.get_messages()
        for m in messages:
            learner_model.send(m, recipient=learner_model, request_reply=False)
        await learner_model.a_send("What is the student's current capabilities", recipient=learner_model, request_reply=True)
        response = learner_model.last_message(agent=learner_model)["content"]
        self.model_tab_interface.send(response, user=learner_model.name,avatar=avatar[learner_model.name])


    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Receive any input from the ChatInterface of the Model tab
        '''
        self.is_model_tab = True
        if user == "System" or user == "User":
            response = learner_model.last_message(agent=learner_model)["content"]
            self.learn_tab_interface.send(response, user=learner_model.name,avatar=avatar[learner_model.name])
        self.is_model_tab = False

    ########## Create the "windows" and draw the tabs
    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Learn", pn.Column(self.learn_tab_interface)),
            ("Dashboard", pn.Column(self.dashboard_view)),
            ("Progress", pn.Column(
                    self.progress_text,
                    pn.Row(                        
                        self.progress_bar,
                        self.progress_info
                    ))),
            ("Model", pn.Column(
                      pn.Row(self.button_update_learner_model),
                      pn.Row(self.model_tab_interface)))            
        )
        return tabs




# --- Panel Interface ---
def create_app():
    reactive_chat = ReactiveChat(groupchat)
    
    #Load chat history on startup 
    chat_history_messages = manager.get_messages_from_json()
    # Send the chat history to the panel interface
    if chat_history_messages:        
        for message in chat_history_messages:
            if globals.IS_TERMINATION_MSG not in message:
                reactive_chat.learn_tab_interface.send(
                    message["content"],
                    user=message["role"], 
                    avatar=avatar.get(message["role"], None),  
                    respond=False
                )

        reactive_chat.learn_tab_interface.send("Time to continue your studies!", user="System", respond=False)
    else:
        reactive_chat.learn_tab_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="System", respond=False)
        
    
    # --- Panel Interface ---    
    reactive_chat.update_dashboard()    #Call after history loaded
    pn.extension(design="material")


    # Anytime an agent processes a message, this function will be called.
    # It prints the message to stdout and sends it to the chat interface
    def autogen_reply_func(recipient, messages, sender, config):
        print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

        last_content = messages[-1]['content']        

        ###############################
        # Update panel tabs
        #############################
        reactive_chat.update_learn_tab(recipient=recipient, messages=messages, sender=sender, config=config)
        reactive_chat.update_dashboard()                          
        reactive_chat.update_progress(contents=last_content,user=recipient.name)
        #Note: do not call update_model_tab. The button takes care of that.
                
        return False, None

    
    # Register chat interface with ConversableAgents and the reply_functioni
    for agent in groupchat.agents:
        agent.chat_interface = reactive_chat.learn_tab_interface
        agent.register_reply([autogen.Agent, None], reply_func=autogen_reply_func, config={"callback": None})

    
    return reactive_chat.draw_view()


if __name__ == "__main__":
    app = create_app()
    #pn.serve(app, debug=True)
    pn.serve(app, callback_exception='verbose')
 
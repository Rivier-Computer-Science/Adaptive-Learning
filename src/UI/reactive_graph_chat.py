

import param
import panel as pn
import asyncio
import re
import autogen as autogen
from src.UI.avatar import avatar
import src.Agents.agents as agents
from src import globals as globals

class ReactiveGraphChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, graph_groupchat_manager=None, **params):
        super().__init__(**params)
        
        pn.extension(design="material")

        self.groupchat_manager = groupchat_manager
        self.graph_groupchat_manager = graph_groupchat_manager

        # Learn tab
        self.GRAPH_TAB_NAME = "GraphTab"
        self.graph_tab_interface = pn.chat.ChatInterface(callback=self.a_graph_tab_callback, name=self.GRAPH_TAB_NAME)


    ############ tab1: Learn interface
    async def a_graph_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            All panel callbacks for the learn tab come through this callback function
            Because there are two chat panels, we need to save the instance
            Then, when update is called, check the instance name
        '''                      
        #self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.knowledge_tracer, self.groupchat_manager, contents))  
        else:
            if globals.input_future and not globals.input_future.done():                
                globals.input_future.set_result(contents)                 
            else:
                print("No input being awaited.")
    
    def update_graph_tab(self, recipient, messages, sender, config):
        #if self.groupchat_manager.chat_interface.name is not self.GRAPH_TAB_NAME: return
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.graph_tab_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.graph_tab_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
        
    
       ########## Create the "windows" and draw the tabs
    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Graph", pn.Column(self.graph_tab_interface)
                    ))
        return tabs

    @property
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager

  
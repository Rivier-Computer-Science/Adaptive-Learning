import asyncio

import autogen as autogen
import panel as pn
import param

import src.Agents.agents as agents
from src import globals as globals
from src.UI.avatar import avatar


class PromptBasedLearning(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)
        self.groupchat_manager = groupchat_manager
        
        # Text input for selecting the topic
        self.topic_input = pn.widgets.TextInput(placeholder="Enter topic...", width=300)
        
        # Button to run the function when the topic is given
        self.run_button = pn.widgets.Button(name="Select Topic", button_type="primary")
        self.run_button.on_click(self.on_topic_select)

        # Chat interface for the prompt-based learning
        self.prompt_chat_name = "PromptTab"
        self.prompt_chat_interface = pn.chat.ChatInterface(callback=self.a_prompt_tab_callback, name=self.prompt_chat_name)
        self.groupchat_manager.chat_interface = self.prompt_chat_interface
        
        # Layout: Combine the text input, button, and chat interface
        self.layout = pn.Column(self.topic_input, self.run_button, self.prompt_chat_interface)

    async def a_prompt_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        # Process the input prompt
        self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")

    def on_topic_select(self, event):
        """Handle topic selection."""
        topic = self.topic_input.value
        if topic:
            # Process the selected topic (You can call a specific function based on the topic here)
            print(f"Topic selected: {topic}")
            con="Ask question to student in the fillinblank format on topic "+topic+"."
            self.groupchat_manager.chat_interface = self.prompt_chat_interface
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, con))
        
            # You can add additional logic to handle the selected topic as needed

            # Clear the input field after selecting the topic
            self.topic_input.value = ""

    def update_prompt_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name is not self.prompt_chat_name: return
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.prompt_chat_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.prompt_chat_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
      
    def draw_view(self):
        return self.layout  # Return the combined layout

    @property
    def groupchat_manager(self) -> autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager

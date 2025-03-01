import param
import panel as pn
import asyncio
import re
import autogen as autogen
from src import globals as globals
from src.Agents.agents import AgentKeys

class ReactiveChat(param.Parameterized):
    def __init__(self, agents_dict, avatars=None, groupchat_manager=None, **params):
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

        # Model tab for career & job recommendations
        self.MODEL_TAB_NAME = "ModelTab"
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback, name=self.MODEL_TAB_NAME)

        # Buttons for career guidance
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)

        self.button_find_jobs = pn.widgets.Button(name='Find Jobs', button_type='primary')
        self.button_find_jobs.on_click(self.handle_find_jobs)

        self.is_model_tab = False

        # Default chat tab
        self.groupchat_manager.chat_interface = self.learn_tab_interface  

    ########## tab1: Learn Interface
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        """Handles chat input for the learn tab."""
        self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(
                self.agents_dict[AgentKeys.TUTOR.value], 
                self.groupchat_manager, 
                contents
            ))  
        else:
            if globals.input_future and not globals.input_future.done():                
                globals.input_future.set_result(contents)                 
            else:
                print("No input being awaited.")
    
    def update_learn_tab(self, recipient, messages, sender, config):
        """Updates the learn tab chat interface."""
        if self.groupchat_manager.chat_interface.name is not self.LEARN_TAB_NAME: 
            return
        last_content = messages[-1]['content']
        user_name = messages[-1].get('name', recipient.name)
        avatar_icon = self.avatars.get(user_name, None)

        self.learn_tab_interface.send(last_content, user=user_name, avatar=avatar_icon, respond=False)
    
    def update_dashboard(self):
        """Fetch the latest career pathway updates and display student progress."""
        student_progress = self.groupchat_manager.groupchat.messages  # Track messages
        total_messages = len(student_progress)
        # Ensure StudentCareerDashboardAgent is used correctly
        if AgentKeys.STUDENT_CAREER_DASHBOARD.value in self.agents_dict:
            career_progress_report = self.agents_dict[AgentKeys.STUDENT_CAREER_DASHBOARD.value].update_progress(
                "Student", "Career Pathway", f"{total_messages} steps completed."
                )
        else:
            career_progress_report = "Career Progress Agent is unavailable."
        self.dashboard_view.object = f"**Career Progress:** {career_progress_report}"


    

    ########### tab3: Progress
    def update_progress(self, contents, user):
        """Tracks student's progress dynamically."""
        if user == "LevelAdapterAgent":
            pattern = re.compile(r'\b(correct|verified|yes|excellent|successfully|good job|right|affirmative)\b', re.IGNORECASE)
            is_correct = pattern.search(contents)
            if is_correct:
                if self.progress < self.max_questions:
                    self.progress += 1
                    self.progress_bar.value = self.progress
                    self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"

    ########## Model Tab Handlers
    async def handle_button_update_model(self, event=None):
        """Updates the learner model dynamically."""
        self.groupchat_manager.chat_interface = self.model_tab_interface
        await self.a_update_model()
     
    async def a_update_model(self):
        """Fetches student capabilities from the Learner Model Agent."""
        if self.groupchat_manager.chat_interface.name is not self.MODEL_TAB_NAME:
            return

        messages = self.groupchat_manager.groupchat.get_messages()
        for msg in messages:
            self.agents_dict[AgentKeys.LEARNER_MODEL.value].send(msg, recipient=self.agents_dict[AgentKeys.LEARNER_MODEL.value], request_reply=False)

        await self.agents_dict[AgentKeys.LEARNER_MODEL.value].a_send(
            "What is the student's current capabilities?", 
            recipient=self.agents_dict[AgentKeys.LEARNER_MODEL.value], 
            request_reply=True
        )

        response = self.agents_dict[AgentKeys.LEARNER_MODEL.value].last_message(agent=self.agents_dict[AgentKeys.LEARNER_MODEL.value])["content"]
        self.model_tab_interface.send(response, user=self.agents_dict[AgentKeys.LEARNER_MODEL.value].name, avatar=self.avatars[self.agents_dict[AgentKeys.LEARNER_MODEL.value].name])

    ########## Job Finder Integration
    async def handle_find_jobs(self, event=None):
        """Handles the job finder button event."""
        self.groupchat_manager.chat_interface = self.model_tab_interface
        await self.a_find_jobs()

    async def a_find_jobs(self):
        """Fetches job recommendations from Job Finder Agent using ChatGPT."""
        if self.groupchat_manager.chat_interface.name is not self.MODEL_TAB_NAME:
            return
        
        await self.agents_dict[AgentKeys.JOB_FINDER.value].a_send(
            "Provide job recommendations based on the student's skills.", 
            recipient=self.agents_dict[AgentKeys.JOB_FINDER.value], 
            request_reply=True
        )

        response = self.agents_dict[AgentKeys.JOB_FINDER.value].last_message(agent=self.agents_dict[AgentKeys.JOB_FINDER.value])["content"]
        self.model_tab_interface.send(response, user=self.agents_dict[AgentKeys.JOB_FINDER.value].name, avatar=self.avatars[self.agents_dict[AgentKeys.JOB_FINDER.value].name])

    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        """Handles chat input for the model tab."""
        self.groupchat_manager.chat_interface = instance
        if user in ["System", "User"]:
            response = self.agents_dict[AgentKeys.LEARNER_MODEL.value].last_message(agent=self.agents_dict[AgentKeys.LEARNER_MODEL.value])["content"]
            self.learn_tab_interface.send(response, user=self.agents_dict[AgentKeys.LEARNER_MODEL.value].name, avatar=self.avatars[self.agents_dict[AgentKeys.LEARNER_MODEL.value].name])
    
    ########## Create the UI Tabs
    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Learn", pn.Column(self.learn_tab_interface)),
            ("Dashboard", pn.Column(self.dashboard_view)),
            ("Progress", pn.Column(
                self.progress_text,
                pn.Row(self.progress_bar, self.progress_info)
            )),
            ("Model", pn.Column(
                pn.Row(self.button_update_learner_model),
                pn.Row(self.button_find_jobs),
                pn.Row(self.model_tab_interface)
            )),
        )
        return tabs

    @property
    def groupchat_manager(self) -> autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager

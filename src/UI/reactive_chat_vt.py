import os
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

        self.last_agent = None
        self.agents_dict = agents_dict
        self.avatars = avatars
        required_keys = [
            AgentKeys.LEARNER_MODEL.value,
            AgentKeys.USER_PREF_UPDATE.value,
            AgentKeys.REALTIME_CAREER_ADJUSTMENT.value,
            AgentKeys.RECOMMENDATION_TESTING.value,
            AgentKeys.STATE_DEFINITION.value,
            AgentKeys.STATE_TRANSITION.value,
            AgentKeys.DATA_SYNC.value,
            AgentKeys.STATE_MACHINE_TESTING.value,
            AgentKeys.AI_EVALUATION.value,
            AgentKeys.SCENARIO_SIMULATION.value,
            AgentKeys.DYNAMIC_RECOMMENDATION_TESTING.value
        ]

        for key in required_keys:
            if key not in self.agents_dict:
                raise KeyError(f"{key} missing from agents_dict. Please ensure all required agents are registered.")

        # ✅ Validate avatars for required agents
        for key in required_keys:
            agent = self.agents_dict[key]
            if agent.name not in self.avatars:
                raise KeyError(f"Avatar missing for {agent.name}. Please add it to the avatars dictionary.")

        # ✅ Assign the groupchat manager after validations
        self.groupchat_manager = groupchat_manager
        # Ensure LearnerModelAgent exists
        if AgentKeys.LEARNER_MODEL.value not in self.agents_dict:
            raise KeyError("LearnerModelAgent is missing from agents_dict. Please add it before initializing ReactiveChat.")
        if self.agents_dict[AgentKeys.LEARNER_MODEL.value].name not in self.avatars:
            raise KeyError("Avatar missing for LearnerModelAgent. Please add it to the avatars dictionary.")
        for key in [AgentKeys.USER_PREF_UPDATE.value, AgentKeys.REALTIME_CAREER_ADJUSTMENT.value, AgentKeys.RECOMMENDATION_TESTING.value]:
            if key not in self.agents_dict:
                raise KeyError(f"{key} missing from agents_dict. Please ensure all adaptive agents are registered.")

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
    # --- Update ReactiveChat.a_learn_tab_callback to properly route user messages ---
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Callback for user messages in the Learn tab.
            - If a last_agent is set, route message there.
            - Otherwise use default CompetencyExtractionAgent.
        '''
        self.groupchat_manager.chat_interface = instance
        print(f"[User message]: {contents}")

            # Route follow-up input to the last agent
        if self.last_agent:
            agent_name = self.last_agent.name
            print(f"[Routing to last agent]: {agent_name}")
            try:
                await self.last_agent.a_send(
                    f"The student mentioned: '{contents}'. Please provide updated recommendations accordingly.",
                    recipient=None,  # ⛔ Avoid agent-to-self loops
                    request_reply=True,
                    llm_config={
                        "config_list": [{"model": "gpt-4", "api_key": os.getenv("OPENAI_API_KEY")}],
                        "temperature": 0.7
                    }
                )
                response = self.last_agent.last_message(agent=self.last_agent)["content"]
            except Exception as e:
                response = f"⚠️ Failed to retrieve response from {agent_name}: {e}"

            self.learn_tab_interface.send(response, user=agent_name, avatar=self.avatars.get(agent_name))
            self.last_agent = None  # ✅ Reset so it doesn't get stuck
            return

        # Default: Use CompetencyExtractionAgent
        competency_agent = self.agents_dict.get(AgentKeys.COMPETENCY_EXTRACTION.value)
        if competency_agent is None:
            print("⚠️ CompetencyExtractionAgent is missing from agents_dict.")
            self.learn_tab_interface.send("⚠️ CompetencyExtractionAgent is not available. Please check configuration.", user="System")
            return

        try:
            await competency_agent.a_send(
                f"User input: {contents}. Please analyze and respond with relevant competencies.",
                recipient=competency_agent,
                request_reply=True
            )
            response = competency_agent.last_message(agent=competency_agent)["content"]
        except Exception as e:
            response = f"⚠️ Failed to get response: {e}"

        self.learn_tab_interface.send(response, user=competency_agent.name, avatar=self.avatars.get(competency_agent.name))

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
        if self.groupchat_manager.chat_interface.name is not self.MODEL_TAB_NAME:
            return

        learner = self.agents_dict[AgentKeys.LEARNER_MODEL.value]
        messages = self.groupchat_manager.groupchat.get_messages()

        for m in messages:
            learner.send(m, recipient=learner, request_reply=False)

        await learner.a_send("What is the student's current capabilities", recipient=learner, request_reply=True)

        try:
            response = learner.last_message(agent=learner)["content"]
        except KeyError:
            response = "No message history available yet for LearnerModelAgent."

        self.model_tab_interface.send(response, user=learner.name, avatar=self.avatars[learner.name])

        
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
        self.groupchat_manager.chat_interface = instance

        if user == "System" or user == "User":
            learner = self.agents_dict[AgentKeys.LEARNER_MODEL.value]
            try:
                response = learner.last_message(agent=learner)["content"]
            except KeyError:
                response = "No message history available yet for LearnerModelAgent."

            self.learn_tab_interface.send(response, user=learner.name, avatar=self.avatars[learner.name])

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
    
    def update_learn_tab(self, *args, **kwargs):
        """
        Placeholder method to avoid attribute errors.
        You can implement learning tab updates here if needed.
        """
        print("⚠️ Called update_learn_tab, but it's not implemented. Ignoring.")


    @property
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager

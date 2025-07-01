"""
reactive_chat_jg.py
This module defines the ReactiveChat class, which provides a chat interface
for interacting with agents in a learning environment. It includes tabs for learning, dashboard, progress tracking, and model management.
"""
import datetime
import param
import panel as pn
import asyncio
import re
import os
import autogen as autogen
from src import globals as globals
from src.Agents.agents import AgentKeys
from datetime import datetime

#from src.UI.reactive_chat23 import StudentChat


class ReactiveChat(param.Parameterized):
    def __init__(self, agents_dict,  avatars=None, groupchat_manager=None, **params):
        super().__init__(**params)
        self.topic = None
        self.steps_completed = []
        self.suggestions = []

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

    ############ tab1: Learn interface
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        print("FSM STATE ON USER INPUT:", self.groupchat_manager.fsm.state)
        print("LAST MSG:", self.groupchat_manager.groupchat.get_messages()[-1] if self.groupchat_manager.groupchat.get_messages() else "NO MESSAGES")

        # ---- Guard: only check messages if any exist ----
        messages = self.groupchat_manager.groupchat.get_messages()
        if messages:
            last_msg = messages[-1]
            agent_name = last_msg.get("name", "")

            if agent_name == "LevelAdapterAgent":
                self.suggestions.append({
                    "suggestion_id": len(self.suggestions) + 1,
                    "text": contents,
                    "created_at": datetime.now().isoformat(),
                    "agent": agent_name
                })

            if agent_name == "StudentAgent":
                self.groupchat_manager.actions.append({
                    "action_id": len(self.groupchat_manager.actions) + 1,
                    "type": "problem_attempt",
                    "actor": agent_name,
                    "timestamp": datetime.now().isoformat(),
                    "details": f"Attempted: {self.topic} | Answer: {contents}"
                })

                # Make step entry unique using question + answer
                pending = getattr(self.groupchat_manager, "pending_problem", {})
                question = pending.get("content", "Unknown Problem")
                self.steps_completed.append({
                    "step_id": len(self.steps_completed) + 1,
                    "description": f"Solved: \"{question}\" → \"{contents}\"",
                    "completed_at": datetime.now().isoformat()
                })

        # --- Exit command handling ---
        if contents.strip().lower() == "exit":
            if hasattr(self, "groupchat_manager"):
                self.groupchat_manager.topic = self.topic
                self.groupchat_manager.steps_completed = self.steps_completed
                self.groupchat_manager.suggestions = self.suggestions
                self.groupchat_manager.status = "completed"
                self.groupchat_manager.save_messages_to_json(self.groupchat_manager.filename)
            instance.send("**Session Ended. Thank you! Please close the tab now!**", user="System", respond=False)

            if hasattr(instance, "input_widget"):
                instance.input_widget.disabled = True
            elif hasattr(instance, "input_area"):
                instance.input_area.disabled = True
            await asyncio.sleep(1)
            os._exit(0)
            print(f"**Session Ended by the user**.")
            return

        # === PATCH: Only StudentAgent should compose verification message, and only once per problem ===
        answer = contents.strip()
        pending_problem = getattr(self.groupchat_manager, "pending_problem", None)
        is_awaiting_answer = getattr(self.groupchat_manager.fsm, "state", None) == "awaiting_answer"

        # Decide agent BEFORE clearing pending_problem
        if is_awaiting_answer and pending_problem:
            verify_message = (
                f"Given the original problem:\n{pending_problem['content']}\n\n"
                f"and the provided answer:\n{answer}\n\n"
                "Please verify if the answer solves the problem. Respond with verification and explanation."
            )
            contents = verify_message
            selected_agent = self.agents_dict[AgentKeys.STUDENT.value]
            #self.groupchat_manager.pending_problem = None  # Clear AFTER
            # Delay clearing. Let update_progress read it first.
            self.clear_pending_problem = True  # Add this as a temporary flag

        else:
            selected_agent = self.agents_dict[AgentKeys.TUTOR.value]

        # ✅ Add user message before triggering agent
        self.groupchat_manager.groupchat.messages.append({
            "content": contents,
            "role": "user",
            "name": selected_agent.name
        })

        # Launch chat task
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(
                selected_agent, self.groupchat_manager, contents))
        else:
            if globals.input_future and not globals.input_future.done():
                globals.input_future.set_result(contents)
            else:
                print("No input being awaited.")

        if contents.strip().lower().startswith("teach me "):
            self.topic = contents.strip()[len("teach me "):].strip().capitalize()

    def update_learn_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name is not self.LEARN_TAB_NAME:
            return
        last_content = messages[-1]['content']
        last_agent = messages[-1].get('name', "")

        # <<< --- ADDED LOGIC TO CAPTURE SUGGESTIONS --- >>>
        if last_agent == "LevelAdapterAgent":
            self.suggestions.append({
                "suggestion_id": len(self.suggestions) + 1,
                "text": last_content,
                "created_at": datetime.now().isoformat(),
                "agent": last_agent
            })
        
        #"actions" filled too
        if last_agent == "StudentAgent":
            self.groupchat_manager.actions.append({
                "action_id": len(self.groupchat_manager.actions) + 1,
                "type": "problem_attempt",
                "actor": last_agent,
                "timestamp": datetime.now().isoformat(),
                "details": f"Attempted: {last_content}"
            })


        if all(key in messages[-1] for key in ['name']):
            role = messages[-1].get("role", "agent")
            self.learn_tab_interface.send(last_content, user=messages[-1]['name'],
                                        avatar=self.avatars.get(messages[-1]['name']), respond=False)
        else:
            self.learn_tab_interface.send(last_content, user=recipient.name,
                                        avatar=self.avatars[recipient.name], respond=False)
            
        # If the last agent is ProblemGeneratorAgent, save the latest problem message
        if last_agent == "ProblemGeneratorAgent":
            # Save the latest problem message to groupchat_manager for persistence in JSON
            self.groupchat_manager.pending_problem = messages[-1]

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
                    ## Added
                    pending = getattr(self.groupchat_manager, "pending_problem", None)
                    question = pending.get("content") if pending and isinstance(pending, dict) else "Unknown Problem"
                    ##
                    self.steps_completed.append({
                        "step_id": len(self.steps_completed) + 1,
                        "description": f"Solved: \"{question}\"",
                        "completed_at": datetime.now().isoformat()
                    })
                    # self.steps_completed.append({
                    #     "step_id": len(self.steps_completed) + 1,
                    #     "description": "Solved a problem correctly",
                    #     "completed_at": datetime.now().isoformat()
                    # })
                    self.progress_bar.value = self.progress
                    self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"

                    # ✅ Clear pending_problem after logging it
                    if getattr(self, "clear_pending_problem", False):
                        self.groupchat_manager.pending_problem = None
                        self.clear_pending_problem = False

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
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager

    def replay_session_to_agents(self, session_data):
        """
        Replay messages from a previous session so both UI and agents are restored as if the session just happened.
        Ensures FSM and groupchat state are properly restored for continued dialog.
        """
        message_history = session_data.get("messages", [])
        if not message_history:
            return

        # Optionally clear the current chat interface
        if hasattr(self.learn_tab_interface, "clear"):
            self.learn_tab_interface.clear()

        # Restore the groupchat_manager's groupchat messages
        self.groupchat_manager.groupchat.messages = message_history.copy()  # key: must use copy for safety!

        # Set FSM state **before** new input
        fsm_state = session_data.get("fsm_state")
        if self.groupchat_manager.fsm and fsm_state:
            if hasattr(self.groupchat_manager.fsm, "set_state"):
                self.groupchat_manager.fsm.set_state(fsm_state)
            else:
                self.groupchat_manager.fsm.state = fsm_state

        # Replay messages in UI (but DON'T re-trigger agents)
        for msg in message_history:
            if "content" in msg and "name" in msg:
                self.learn_tab_interface.send(
                    msg["content"],
                    user=msg["name"],
                    avatar=self.avatars.get(msg["name"], None),
                    respond=False
                )

        self.update_dashboard()



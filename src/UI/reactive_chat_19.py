import param
import panel as pn
import asyncio
import re
import pandas as pd
import autogen as autogen
from src.UI.avatar import avatar
import src.Agents.agents as agents
from src import globals as globals
import pprint
import logging

class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)


        pn.extension(design="material")

        pn.config.raw_css.append("""
        .tabulator-cell {
            white-space: normal !important;  /* Allows text to wrap */
            word-wrap: break-word;           /* Breaks long words if necessary */
            padding: 5px;                    /* Adds some padding for better readability */
        }
        .custom-table-container {
            width: 99vw; /* 99% of the viewport width */
            margin: 0 auto; /* Center the table */
        }
        """)

        self.groupchat_manager = groupchat_manager

        # Learn tab
        self.LEARN_TAB_NAME = "LearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback, name=self.LEARN_TAB_NAME)

        # Dashboard tab
        self.dashboard_view = pn.pane.Markdown(f"Total messages: {len(self.groupchat_manager.groupchat.messages)}")

        # Progress tab
        self.progress_text = pn.pane.Markdown(f"Student Progress")
        self.progress = 0
        self.max_questions = 10
        self.progress_bar = pn.widgets.Progress(name='Progress', value=self.progress, max=self.max_questions)        
        self.progress_info = pn.pane.Markdown(f"{self.progress} out of {self.max_questions}", width=60)

        # Question and answer details for tracking
        self.question_details = pn.widgets.Tabulator(
            pd.DataFrame(columns=['Question', 'Student Answer', 'Correct']),
            show_index=False,  # Hide the index column
            height=400,        # Set height for better visibility
            sizing_mode='stretch_width',  # Stretch to fit the container
            configuration={
                'layout': 'fitColumns',  # Ensure columns fit the container
                'columns': [
                    {
                        'field': 'Question',
                        'title': 'Question',
                        'widthGrow': 3,  
                        'formatter': 'plaintext',  # Plain text formatter
                    },
                    {
                        'field': 'Student Answer',
                        'title': 'Student Answer',
                        'widthGrow': 1,  
                        'formatter': 'plaintext',  # Plain text formatter
                    },
                    {
                        'field': 'Correct',
                        'title': 'Correct',
                        'widthGrow': 1,  
                        'formatter': 'tickCross',  # Use tick/cross for boolean values
                        'hozAlign': 'center',     # Center align for better aesthetics
                    }
                ],
            }
        )



        # Model tab. Capabilities for the LearnerModel
        self.MODEL_TAB_NAME = "ModelTab"
        self.model_tab_interface = pn.chat.ChatInterface(callback=self.a_model_tab_callback, name=self.MODEL_TAB_NAME)
        self.button_update_learner_model = pn.widgets.Button(name='Update Learner Model', button_type='primary')
        self.button_update_learner_model.on_click(self.handle_button_update_model)
        self.is_model_tab = False

        # GroupChatManager sets up the chat interface
        self.groupchat_manager.chat_interface = self.learn_tab_interface  # default chat tab

    ############ tab1: Learn interface
    async def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            All panel callbacks for the learn tab come through this callback function
        '''                      
        self.groupchat_manager.chat_interface = instance
        # Store the question in globals if it contains 'solve'
        if 'solve' or 'Solve' in contents.lower():
            globals.last_question = contents  # Store the last question
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
        # chat_manager -> LearnerModelAgent has contents from CodeRunnerAgent
        # chat_manager -> LevelAdapterAgent has contents from LearnerModelAgent        
        if user == "LevelAdapterAgent":    # Get response from LearnerModelAgent
            logging.info(f"update_progress(). User= {user}. contents=\n{contents}")

            # Find original question
            all_messages = self.groupchat_manager.groupchat.get_messages()
            for message in list(reversed(all_messages)):
                if message['name'] == 'ProblemGeneratorAgent':
                    question = message['content']
                    break

            # Find Student's answer
            for message in list(reversed(all_messages)):
                if message['name'] == 'StudentAgent':
                    student_answer = message['content']
                    break
            
            # Is Student's answer correct?
            pattern_correct = re.compile(r"StudentAgent's answer is correct", re.IGNORECASE)
            is_correct = bool(pattern_correct.search(contents))

            if is_correct:
                print("################ CORRECT ANSWER #################")
                if self.progress < self.max_questions:  
                    self.progress += 1
                    self.progress_bar.value = self.progress
                    self.progress_info.object = f"{self.progress} out of {self.max_questions}"
            else:
                print("################ WRONG ANSWER #################")               
                
            # Update panel tab with history
            new_row = pd.DataFrame({'Question': [question], 'Student Answer': [student_answer], 'Correct': [is_correct]})
            self.question_details.value = pd.concat([self.question_details.value, new_row], ignore_index=True)

        
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
        self.model_tab_interface.send(response, user=agents.learner_model.name, avatar=avatar[agents.learner_model.name])

    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Receive any input from the ChatInterface of the Model tab
        '''
        self.groupchat_manager.chat_interface = instance
        if user == "System" or user == "User":
            response = agents.learner_model.last_message(agent=agents.learner_model)["content"]
            self.learn_tab_interface.send(response, user=agents.learner_model.name, avatar=avatar[agents.learner_model.name])

    ########## Create the "windows" and draw the tabs
    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Learn", pn.Column(self.learn_tab_interface)),
            ("Dashboard", pn.Column(self.dashboard_view)),
            ("Progress", pn.Column(
                    self.progress_text,
                    pn.Row(                        
                        self.progress_bar,
                        self.progress_info),
                    self.question_details
                    )),
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

if __name__ == "main":    
    app = ReactiveChat().draw_view()
    pn.serve(app, callback_exception='verbose')
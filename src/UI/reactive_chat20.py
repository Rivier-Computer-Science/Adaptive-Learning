import asyncio
import re

import autogen as autogen
import firebase_admin
import panel as pn
import param
from firebase_admin import credentials, firestore

import src.Agents.agents as agents
from src import globals as globals
from src.UI.avatar import avatar

# Initialize Firestore using the credentials
cred = credentials.Certificate(r'C:\Users\kutha\Downloads\adaptive-learning-rivier-firebase-adminsdk-6u1pl-d8fc406e6f.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# completed code of sprint 4


class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)
        
        pn.extension(design="material")

        self.groupchat_manager = groupchat_manager
        
        self.bookmarked_messages=[]
 
 
        # Learn tab
        self.LEARN_TAB_NAME = "LearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback, name=self.LEARN_TAB_NAME)

        # Dashboard tab
        self.dashboard_view = pn.pane.Markdown(f"Total messages: {len(self.groupchat_manager.groupchat.messages)}")
        
        # Initialize BookmarkPage
        self.bookmark_page = BookmarkPage()
        
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
        '''
            All panel callbacks for the learn tab come through this callback function
            Because there are two chat panels, we need to save the instance
            Then, when update is called, check the instance name
        '''                      
        self.groupchat_manager.chat_interface = instance
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.tutor, self.groupchat_manager, contents))  
        else:
            if globals.input_future and not globals.input_future.done():                
                globals.input_future.set_result(contents)                 
            else:
                print("No input being awaited.")
    
    def update_learn_tab(self, recipient, messages, sender, config):
        if self.groupchat_manager.chat_interface.name is not self.LEARN_TAB_NAME: return
        bookmark_button = pn.widgets.ButtonIcon(icon="heart", size="2em", description="favorite")
        
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            bookmark_button.on_click(lambda event: self.bookmark_page.add_bookmark({"message":last_content, "user":messages[-1]['name']}))
            
            self.learn_tab_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
            self.learn_tab_interface.append(pn.Column(bookmark_button))
        
        else:
            bookmark_button.on_click(lambda event: self.bookmark_page.add_bookmark({"message":last_content, "user": recipient.name}))
            
            self.learn_tab_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
            self.learn_tab_interface.append(pn.Column(bookmark_button))
        
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
            agents.learner_model.send(m, recipient=agents.learner_model, request_reply=False)
        await agents.learner_model.a_send("What is the student's current capabilities", recipient=agents.learner_model, request_reply=True)
        response = agents.learner_model.last_message(agent=agents.learner_model)["content"]
        self.model_tab_interface.send(response, user=agents.learner_model.name,avatar=avatar[agents.learner_model.name])


    async def a_model_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            Receive any input from the ChatInterface of the Model tab
        '''
        self.groupchat_manager.chat_interface = instance
        if user == "System" or user == "User":
            response = agents.learner_model.last_message(agent=agents.learner_model)["content"]
            self.learn_tab_interface.send(response, user=agents.learner_model.name,avatar=avatar[agents.learner_model.name])
    

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
            ("Bookmark", self.bookmark_page.get_view())
        )
        return tabs

    @property
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager



class BookmarkPage(param.Parameterized):
    def __init__(self, **params):
        super().__init__(**params)

        self.bookmarked_messages = []  # Local storage for bookmarks
        self.chat_interface = pn.chat.ChatInterface(callback=self.noop_callback, name="BookmarkInterface")
        
        self.confirm_float_panel = pn.layout.FloatPanel(
            pn.pane.Markdown("Are you sure you want to remove this bookmark?"),
            pn.widgets.Button(name="Confirm", button_type="danger", width=100),
            pn.widgets.Button(name="Cancel", button_type="primary", width=100),
            name="Confirm Deletion",
            contained=False,
            position='center',
            theme="warning filleddark",
            status="closed"  # Initially hidden
        )
        self.confirm_float_panel[1].on_click(self.confirm_remove)  # Confirm button
        self.confirm_float_panel[2].on_click(self.cancel_remove)   # Cancel button
        
        # Placeholder for the message to remove
        self.message_to_remove = None


        
        # Load initial bookmarks from Firestore for the user
        self.load_bookmarks()

    async def noop_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        """No operation callback for the bookmark interface."""
        pass

    def add_bookmark(self, message_data):
        """Add a new message to bookmarks, update Firestore, and update the chat interface."""
        self.bookmarked_messages.append(message_data)
        
        # Add the bookmark to Firestore (nested under the user's document)
        db.collection('bookmarks').add(message_data)

        self.update_bookmark_view()
        
    def confirm_remove(self, event=None):
        """Confirm the removal of a bookmark and update Firestore."""
        if self.message_to_remove:
            self.bookmarked_messages.remove(self.message_to_remove)
            
            # Remove the bookmark from Firestore
            bookmarks_ref = db.collection('bookmarks')
            query = bookmarks_ref.where('message', '==', self.message_to_remove).stream()
            
            for doc in query:
                doc.reference.delete()

            self.update_bookmark_view()
            self.cancel_remove()  # Hide the float panel after confirming

        
    def cancel_remove(self, event=None):
        """Hide the confirmation float panel without removing the bookmark."""
        self.confirm_float_panel.param.set_param(status="closed")
        self.message_to_remove = None  # Reset the message to remove

    def remove_bookmark(self, message_data):
        """Trigger the confirmation float panel for removing a bookmark."""
        self.message_to_remove = message_data
        self.confirm_float_panel.param.set_param(status="normalized")  # Show float panel

    def remove_bookmark(self, message_data):
        """Remove a message from bookmarks, update Firestore, and update the chat interface."""
        self.bookmarked_messages.remove(message_data)
        
        # Remove the bookmark from Firestore
        bookmarks_ref = db.collection('bookmarks')
        # Query for the specific bookmark document by its content
        query = bookmarks_ref.where('message', '==', message_data['message']).stream()
        
        for doc in query:
            doc.reference.delete()

        self.update_bookmark_view()

    def load_bookmarks(self):
        """Load the user's bookmarks from the Firestore sub-collection."""
        bookmarks_ref = db.collection('bookmarks')
        docs = bookmarks_ref.stream()

        # Clear current bookmarks
        self.bookmarked_messages = []

        for doc in docs:
            self.bookmarked_messages.append(doc.to_dict())

        self.update_bookmark_view()

    def update_bookmark_view(self):
        """Update the chat interface to display bookmarked messages with remove buttons."""
        self.chat_interface.clear()  # Clear previous messages

        for message_data in self.bookmarked_messages:
            user = message_data['user']
            message = message_data['message']

            # Create a button to remove the bookmark
            remove_button = pn.widgets.ButtonIcon(icon="heart", active_icon="heart-filled", value=True, size="2em", description="favorite")
            remove_button.on_click(lambda event, msg=message_data: self.remove_bookmark(msg))

            # Send the bookmarked message to the chat interface and append the remove button
            self.chat_interface.send(message, user=user, avatar=None, respond=False)
            self.chat_interface.append(pn.Row(remove_button))

    def get_view(self):
        """Return the view of the chat interface with bookmarked messages."""
        return pn.Column(self.chat_interface)

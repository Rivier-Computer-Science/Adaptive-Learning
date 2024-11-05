import asyncio
import datetime
import re

import autogen as autogen
import firebase_admin
import panel as pn
import param
from firebase_admin import credentials, firestore

import src.Agents.agents as agents
from src import globals as globals
from src.UI.avatar import avatar

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'C:\Users\kutha\Downloads\adaptive-learning-rivier-firebase-adminsdk-6u1pl-d8fc406e6f.json')
firebase_admin.initialize_app(cred)

# Firestore database reference
db = firestore.client()

class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)
        
        pn.extension(design="material")

        self.groupchat_manager = groupchat_manager
 
        # Learn tab
        self.LEARN_TAB_NAME = "LearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback, name=self.LEARN_TAB_NAME)

        # Dashboard tab
        self.dashboard_view = pn.pane.Markdown(f"Total messages: {len(self.groupchat_manager.groupchat.messages)}")
        
        #chat
        self.student_chat=StudentChat()

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
            ("Student Chat",self.student_chat.draw_view()),
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



class StudentChat(param.Parameterized):
    def __init__(self, **params):
        super().__init__(**params)

        # Input field for searching room IDs
        self.room_input = pn.widgets.TextInput(placeholder="Search room ID...", width=300)
        self.room_input.param.watch(self.update_displayed_rooms, 'value')

        # Button to create a new room
        self.create_room_button = pn.widgets.Button(name="Create Room", button_type="success")
        self.create_room_button.on_click(self.create_room)

        # Chat interface
        self.chat_interface = pn.chat.ChatInterface(callback=self.chat_callback, name="StudentChatTab")

        # Store room and chat data
        self.all_rooms = {}
        self.displayed_rooms = []
        self.selected_room = None
        self.displayed_message_ids = set()  # Track displayed message IDs
        self.pending_messages = set()  # Track messages being processed to avoid duplicates
        self.displayed_message = []
        self.displayed_message_user = {}
        
         # Row layout for room input, room list dropdown, and create room button with fixed width
        self.controls_row = pn.Row(self.room_input, self.create_room_button, self.create_room_list(), width=600)

        # Centered layout with alignment
        self.controls_column = pn.Column(self.controls_row, align="center", sizing_mode="stretch_width")

        # Main layout
        self.layout = pn.Column(self.controls_column, self.chat_interface)
        
        
        
        # Fetch rooms from Firestore
        self.fetch_rooms_from_firestore()

    def fetch_rooms_from_firestore(self):
        """Fetch chat rooms from Firestore."""
        rooms_ref = db.collection('chat_rooms')
        rooms = rooms_ref.get()

        self.all_rooms = {}
        for room in rooms:
            room_data = room.to_dict()
            self.all_rooms[room.id] = {
                'name': room.id,
                'messages': []
            }
            self.fetch_messages_for_room(room.id)  # Fetch messages for each room

        # Update the displayed rooms after fetching
        self.displayed_rooms = list(self.all_rooms.keys())
        self.room_list.options = self.displayed_rooms

    def fetch_messages_for_room(self, room_id):
        """Fetch chat messages for a specific room."""
        messages_ref = db.collection('chat_rooms').document(room_id).collection('messages')
        messages = messages_ref.order_by('timestamp')
        
        def on_snapshot(messages_snapshot, changes, read_time):
            self.all_rooms[room_id]['messages'] = []  # Clear the messages before updating

            for change in changes:
                message = change.document
                message_data = message.to_dict()
                message_id = message.id

                # Handle added and modified messages
                if change.type.name == 'ADDED' or change.type.name == 'MODIFIED':
                    if message_id not in self.displayed_message_ids:
                        self.displayed_message_ids.add(message_id)
                        self.pending_messages.add(message_data['content'])
                        self.all_rooms[room_id]['messages'].append(
                            {"id": message_id, "sender_name": message_data['sender_name'], "content": message_data['content']}
                        )
                        self.chat_interface.send(message_data['content'], user=message_data['sender_name'])

                # Handle removed messages if necessary (optional)
                elif change.type.name == 'REMOVED':
                    # You can implement message deletion handling here if needed
                    pass

        # Attach the snapshot listener
        messages_ref.on_snapshot(on_snapshot)
        
        print(self.all_rooms[room_id])
        

    def create_room_list(self):
        """Create a dropdown to display room IDs."""
        self.room_list = pn.widgets.Select(name="Rooms", options=self.displayed_rooms)
        self.room_list.param.watch(self.select_room, 'value')
        return self.room_list

    def update_displayed_rooms(self, event):
        """Update displayed room IDs based on search input."""
        search_term = self.room_input.value.lower()
        self.displayed_rooms = [room_id for room_id in self.all_rooms if search_term in room_id.lower()]
        self.room_list.options = self.displayed_rooms

    def select_room(self, event):
        """Handle room selection."""
        self.selected_room = self.room_list.value
        if self.selected_room:
            self.displayed_message_ids = set()
            self.refresh_chat_interface()

    def refresh_chat_interface(self):
        """Refresh the chat interface with the current room's messages."""
        self.chat_interface.clear()
        self.displayed_message_ids.clear()
        self.fetch_messages_for_room(self.selected_room)
        if self.selected_room in self.all_rooms:
            self.update_chat_box(self.selected_room)

    def update_chat_box(self, room_id):
        """Update the chat interface with new messages for the selected room."""
        if room_id in self.all_rooms:
            
            for message in self.all_rooms[room_id]['messages']:
                self.all_rooms[room_id]['messages']
                if message['id'] not in self.displayed_message_ids:
                    self.displayed_message_ids.add(message['id'])
                    self.pending_messages.add(message['content'])
                    self.chat_interface.send(message['content'], user=message['sender_name'])

    async def chat_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        """Handle incoming messages in the chat."""
        for message in instance.serialize():
            print("Meddage",message)
        if contents not in self.pending_messages:
            self.pending_messages.add(contents)  # Track messages being processed
            self.displayed_message.append(contents)
            self.displayed_message_user[contents] = {
                "user": user,
                "status": False,
                "time": datetime.datetime.now()
            }
            await self.save_message_to_firestore(contents, user)
            self.pending_messages.remove(contents)  # Remove from pending once saved

    async def save_message_to_firestore(self, contents: str, user: str):
        """Save new message to Firestore, ensuring no duplicates."""
        if self.selected_room:
            message_time = datetime.datetime.now()

            # Create new message document in Firestore
            messages_ref = db.collection('chat_rooms').document(self.selected_room).collection('messages').document(str(message_time)[:18])
            new_message = {
                "sender_name": user,
                "content": contents,
                "timestamp": message_time
            }

            # Save the message to Firestore
            messages_ref.set(new_message)
            print(f"Message saved: {contents} from {user} at {message_time}")

    def create_room(self, event):
        """Create a new chat room in Firestore."""
        new_room_id = self.room_input.value.strip()
        self.update_chat_box(self.selected_room)

        for contents in self.displayed_message:
            if not self.displayed_message_user[contents]["status"]:
                self.displayed_message_user[contents]["status"] = True
                self.save_message_to_firestore(contents, self.displayed_message_user[contents]["user"])

        if new_room_id and new_room_id not in self.all_rooms:
            room_ref = db.collection('chat_rooms').document(new_room_id)
            room_ref.set({'name': new_room_id, 'created_at': datetime.datetime.now()})

            # Initialize the new room locally
            self.all_rooms[new_room_id] = {'name': new_room_id, 'messages': []}
            self.displayed_rooms.append(new_room_id)
            self.room_list.options = self.displayed_rooms

            self.room_input.value = ""  # Clear input field
            print(f"Created new room: {new_room_id}")

    def draw_view(self):
        return self.layout

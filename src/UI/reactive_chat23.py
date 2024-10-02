import datetime

import firebase_admin
import panel as pn
import param
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred)

# Firestore database reference
db = firestore.client()

import asyncio


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

        # Layout
        self.layout = pn.Column(self.room_input, self.create_room_list(), self.create_room_button, self.chat_interface)

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
        messages = messages_ref.order_by('timestamp').get()
        
        self.all_rooms[room_id]['messages']=[]
        for message in messages:
            message_data = message.to_dict()
            message_id = message.id
            self.all_rooms[room_id]['messages'].append(
                {"id": message_id, "sender_name": message_data['sender_name'], "content": message_data['content']}
                )
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

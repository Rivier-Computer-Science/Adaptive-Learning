import asyncio
import re
import os
import autogen as autogen
import firebase_admin
import panel as pn
import param
from cryptography.fernet import Fernet
from firebase_admin import auth, credentials, firestore
from src.Tools.firebase import get_firestore_client  # adjust path as needed
import src.Agents.agents as agents
from src import globals as globals
from src.UI.avatar import avatar
from dotenv import load_dotenv

# Load from .env if using python-dotenv (optional but recommended)
load_dotenv()  # This will auto-load .env vars into os.environ

SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
if not SERVICE_ACCOUNT_KEY_PATH:
    raise ValueError("Missing environment variable: FIREBASE_SERVICE_ACCOUNT_KEY_PATH in reactive_chat17")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)

# Initialize Firebase
#cred = credentials.Certificate("ServiceAccountKey.json")
#firebase_admin.initialize_app(cred)

# Firestore database reference
db = firestore.client()


class ReactiveChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, **params):
        super().__init__(**params)
        
        pn.extension(design="material")
        
        # Subbmitting Fully Completed Code

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
        
        self.login_page=UserAuth()
        
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
            ("Model", pn.Column(
                      pn.Row(self.button_update_learner_model),
                      pn.Row(self.model_tab_interface))
                    ),     
            ("Login Page",self.login_page.draw_view())
        )
        return tabs

    @property
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager



class UserAuth(param.Parameterized):
    email = param.String(default='', label="Email")
    password = param.String(default='', label="Password")
    name = param.String(default='', label="Name")
    gender = param.Selector(default="Male", objects=["Male", "Female", "Other"], label="Gender")

    is_login_page = param.Boolean(default=True)  # Toggle between login and signup
    #user_uid = None  # Track logged-in user session
    user_uid = param.String(default=None, doc="Track logged-in user session")
    
    # Encryption
    encryption_key = Fernet.generate_key()  # Generate encryption key
    cipher_suite = Fernet(encryption_key)

    def __init__(self, **params):
        super().__init__(**params)

        # Widgets
        self.email_input = pn.widgets.TextInput(name='Email', placeholder='Enter email')
        self.password_input = pn.widgets.PasswordInput(name='Password', placeholder='Enter password')
        self.name_input = pn.widgets.TextInput(name='Name', placeholder='Enter full name')
        self.gender_input = pn.widgets.Select(name='Gender', options=["Male", "Female", "Other"])

        # Error message display
        self.error_message = pn.pane.Markdown("")

        # Buttons for login, signup, and logout
        self.login_button = pn.widgets.Button(name="Login", button_type="primary")
        self.signup_button = pn.widgets.Button(name="Sign Up", button_type="success")
        self.logout_button = pn.widgets.Button(name="Logout", button_type="danger")
        self.puser = {}

        # Event handlers
        self.login_button.on_click(self.handle_login)
        self.signup_button.on_click(self.handle_signup)
        self.logout_button.on_click(self.handle_logout)

        # Toggle between pages
        self.toggle_page_button = pn.widgets.Button(name="Switch to Sign Up", button_type="light")
        self.toggle_page_button.on_click(self.toggle_page)

        # Layout
        self.layout = pn.Column()  # Initialize an empty layout
        self.update_layout()  # Populate it with the correct form based on the current page

    def toggle_page(self, event):
        """Toggle between login and signup page."""
        self.is_login_page = not self.is_login_page
        self.error_message.object = ""  # Clear error message when switching pages

        # Update the button text and layout
        if self.is_login_page:
            self.toggle_page_button.name = "Switch to Sign Up"
        else:
            self.toggle_page_button.name = "Switch to Login"

        self.update_layout()  # Update the layout when toggling

    def update_layout(self):
        """Update the layout based on the current page."""
        if self.user_uid:
            # If user is logged in, show profile page
            self.display_profile_page()
        elif self.is_login_page:
            # Login page layout
            self.layout[:] = [
                self.error_message,
                self.email_input,
                self.password_input,
                self.toggle_page_button,
                self.login_button
            ]
        else:
            # Signup page layout
            self.layout[:] = [
                self.error_message,
                self.name_input,
                self.email_input,
                self.password_input,
                self.gender_input,
                self.toggle_page_button,
                self.signup_button
            ]

    def handle_login(self, event):
        """Handle user login using Firebase Auth."""
        try:
            print("login")
            # Simulate login by fetching the user from Firestore
            user = auth.get_user_by_email(self.email_input.value)
            print(f"User logged in: {user.email}")

            # Fetch user data from Firestore
            user_ref = db.collection('users').document(user.uid)
            user_data = user_ref.get().to_dict()

            if user_data:
                # Decrypt the data before displaying
                self.puser["name"] = self.cipher_suite.decrypt(user_data['name'].encode('utf-8')).decode('utf-8')
                self.puser["email"] = self.cipher_suite.decrypt(user_data['email'].encode('utf-8')).decode('utf-8')
                self.puser["gender"] = self.cipher_suite.decrypt(user_data['gender'].encode('utf-8')).decode('utf-8')

            # Set user session (store UID)
            self.user_uid = user.uid
            self.update_layout()  # Switch to profile page
        except Exception as e:
            # Update error message pane
            self.error_message.object = f"Error: {e}"
            self.update_layout()

    def handle_signup(self, event):
        """Handle user signup and save details in Firestore."""
        try:
            # Create a new user in Firebase Auth
            user = auth.create_user(
                email=self.email_input.value,
                password=self.password_input.value
            )

            user = auth.update_user(
                user.uid,
                email=self.email_input.value,
                display_name=self.name_input.value,
            )

            # Encrypt the data
            encrypted_name = self.cipher_suite.encrypt(self.name_input.value.encode('utf-8'))
            encrypted_email = self.cipher_suite.encrypt(self.email_input.value.encode('utf-8'))
            encrypted_gender = self.cipher_suite.encrypt(self.gender_input.value.encode('utf-8'))

            # Store additional info in Firestore (encrypted)
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'name': encrypted_name.decode('utf-8'),
                'email': encrypted_email.decode('utf-8'),
                'gender': encrypted_gender.decode('utf-8')
            })

            print(f"User {self.name_input.value} signed up successfully")

            # Set user session (store UID)
            self.user_uid = user.uid
            self.update_layout()  # Switch to profile page
        except Exception as e:
            # Update error message pane
            self.error_message.object = f"Error: {e}"
            self.update_layout()

    def update_user_data(self, updated_name, updated_email, updated_gender):
        """Update user data in Firestore."""
        try:
            if self.user_uid:
                # Encrypt updated data
                encrypted_name = self.cipher_suite.encrypt(updated_name.encode('utf-8'))
                encrypted_email = self.cipher_suite.encrypt(updated_email.encode('utf-8'))
                encrypted_gender = self.cipher_suite.encrypt(updated_gender.encode('utf-8'))

                # Update the user's document in Firestore
                user_ref = db.collection('users').document(self.user_uid)
                user_ref.update({
                    'name': encrypted_name.decode('utf-8'),
                    'email': encrypted_email.decode('utf-8'),
                    'gender': encrypted_gender.decode('utf-8')
                })

                print(f"User {updated_name} data updated successfully.")
        except Exception as e:
            print(f"Error updating user data: {e}")

    def display_profile_page(self):
        """Display the profile page with user details."""
        print("profile page function")
        if self.user_uid:
            user_ref = db.collection('users').document(self.user_uid)
            user_data = user_ref.get().to_dict()

            if user_data:
                # Decrypt the data before displaying
                decrypted_name = self.cipher_suite.decrypt(user_data['name'].encode('utf-8')).decode('utf-8')
                decrypted_email = self.cipher_suite.decrypt(user_data['email'].encode('utf-8')).decode('utf-8')
                decrypted_gender = self.cipher_suite.decrypt(user_data['gender'].encode('utf-8')).decode('utf-8')

                self.layout[:] = [
                    pn.pane.Markdown(f"### Welcome, {decrypted_name}"),
                    pn.pane.Markdown(f"**Email:** {decrypted_email}"),
                    pn.pane.Markdown(f"**Gender:** {decrypted_gender}"),
                    self.logout_button
                ]
            else:
                self.layout[:] = [
                    pn.pane.Markdown(f"**Name:** {self.puser['name']}"),
                    pn.pane.Markdown(f"**Email:** {self.puser['email']}"),
                    self.logout_button
                ]

    def handle_logout(self, event):
        """Handle user logout."""
        self.user_uid = None  # Clear user session
        self.error_message.object = ""  # Clear error message on logout
        self.update_layout()  # Switch back to login page
        print("User logged out.")

    def draw_view(self):
        return self.layout

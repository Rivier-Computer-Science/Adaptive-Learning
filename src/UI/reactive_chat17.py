import firebase_admin
import panel as pn
import param
from firebase_admin import auth, credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred)

# Firestore database reference
db = firestore.client()

class UserAuth(param.Parameterized):
    email = param.String(default='', label="Email")
    password = param.String(default='', label="Password")
    name = param.String(default='', label="Name")
    gender = param.Selector(default="Male", objects=["Male", "Female", "Other"], label="Gender")

    is_login_page = param.Boolean(default=True)  # Toggle between login and signup
    user_uid = None  # Track logged-in user session
    
    def __init__(self, **params):
        super().__init__(**params)
        
        
        # Widgets
        self.email_input = pn.widgets.TextInput(name='Email', placeholder='Enter email')
        self.password_input = pn.widgets.PasswordInput(name='Password', placeholder='Enter password')
        self.name_input = pn.widgets.TextInput(name='Name', placeholder='Enter full name')
        self.gender_input = pn.widgets.Select(name='Gender', options=["Male", "Female", "Other"])
        
        # Buttons for login, signup, and logout
        self.login_button = pn.widgets.Button(name="Login", button_type="primary")
        self.signup_button = pn.widgets.Button(name="Sign Up", button_type="success")
        self.logout_button = pn.widgets.Button(name="Logout", button_type="danger")
        self.puser={}

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
                self.email_input,
                self.password_input,
                self.toggle_page_button,
                self.login_button
            ]
        else:
            # Signup page layout
            self.layout[:] = [
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
            self.puser["name"]=user.display_name
            self.puser["email"]=user.email
            # Set user session (store UID)
            self.user_uid=user.uid
            print(self.puser)
            self.update_layout()  # Switch to profile page
        except Exception as e:
            print(f"Error: {e}")
    
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
                display_name='Jane Doe',
                
            )
            
            # Store additional info in Firestore
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'name': self.name_input.value,
                'email': self.email_input.value,
                'gender': self.gender_input.value
            })
            
            print(f"User {self.name_input.value} signed up successfully")
            
            # Set user session (store UID)
            self.user_uid = user.uid
            self.update_layout()  # Switch to profile page
        except Exception as e:
            print(f"Error: {e}")
    
    def display_profile_page(self):
        """Display the profile page with user details."""
        print("profile page function")
        if self.user_uid:
            user_ref = db.collection('users').document(self.user_uid)
            user_data = user_ref.get().to_dict()
            # print("dsif",user_data,auth().currentUser)
            # Profile page layout
            if user_data:
                self.layout[:] = [
                    pn.pane.Markdown(f"### Welcome, {user_data['name']}"),
                    pn.pane.Markdown(f"**Email:** {user_data['email']}"),
                    pn.pane.Markdown(f"**Gender:** {user_data['gender']}"),
                    self.logout_button
                ]
            else:
                self.layout[:] =[
                    pn.pane.Markdown(f"**name:** {self.puser["name"]}"),
                    pn.pane.Markdown(f"**Email:** {self.puser["email"]}"),
                    self.logout_button
                ]
    
    def handle_logout(self, event):
        """Handle user logout."""
        self.user_uid = None  # Clear user session
        self.update_layout()  # Switch back to login page
        print("User logged out.")
    
    def draw_view(self):
        return self.layout

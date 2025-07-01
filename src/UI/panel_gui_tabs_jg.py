"""
File updated to sync to Firebase and Realtime DB
"""

import autogen
import panel as pn
import openai
import os
import time
import asyncio
from typing import List, Dict
import logging, datetime
from enum import Enum
from dotenv import load_dotenv
import requests
from src.Tools.firebase import get_user_from_realtime_db, get_sessions, get_session_details, delete_session
from src.Tools.firebase import add_user_to_realtime_db

# --- Panel Auth Imports ---
import param
import firebase_admin
from firebase_admin import auth, credentials, firestore
from cryptography.fernet import Fernet
from datetime import datetime

# --- Your original imports ---
from src import globals
from src.FSMs.fsm_teach_me import TeachMeFSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat_jg import ReactiveChat
from src.UI.avatar import avatar

# --------------------------------------------------
# Logging and Environment Setup
# --------------------------------------------------

load_dotenv()
logging.basicConfig(level=logging.INFO, 
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
os.environ["AUTOGEN_USE_DOCKER"] = "False"

# --------------------------------------------------
# Firebase Initialization for Auth & Firestore
# --------------------------------------------------

SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
if not SERVICE_ACCOUNT_KEY_PATH:
    raise ValueError("Missing FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --------------------------------------------------
# Login / Signup Authentication 
# --------------------------------------------------

class UserAuth(param.Parameterized):
    key_from_env = os.getenv('FERNET_KEY')
    if not key_from_env:
        raise ValueError("Missing FERNET_KEY in environment (.env) file!")
    encryption_key = key_from_env.encode()
    cipher_suite = Fernet(encryption_key)

    email = param.String(default='', label="Email")
    password = param.String(default='', label="Password")
    name = param.String(default='', label="Name")
    gender = param.Selector(default="Male", objects=["Male", "Female", "Other"], label="Gender")

    is_login_page = param.Boolean(default=True)
    user_uid = param.String(default=None, doc="Track logged-in user session")


    def __init__(self, **params):
        super().__init__(**params)
        self.email_input = pn.widgets.TextInput(name='Email', placeholder='Enter email')
        self.password_input = pn.widgets.PasswordInput(name='Password', placeholder='Enter password')
        self.name_input = pn.widgets.TextInput(name='Name', placeholder='Enter full name')
        self.gender_input = pn.widgets.Select(name='Gender', options=["Male", "Female", "Other"])
        self.error_message = pn.pane.Markdown("")
        self.login_button = pn.widgets.Button(name="Login", button_type="primary")
        self.signup_button = pn.widgets.Button(name="Sign Up", button_type="success")
        self.logout_button = pn.widgets.Button(name="Logout", button_type="danger")
        self.login_button.on_click(self.handle_login)
        self.signup_button.on_click(self.handle_signup)
        self.logout_button.on_click(self.handle_logout)
        self.toggle_page_button = pn.widgets.Button(name="Switch to Sign Up", button_type="light")
        self.toggle_page_button.on_click(self.toggle_page)
        self.layout = pn.Column()
        self.update_layout()
        

    def toggle_page(self, event):
        self.is_login_page = not self.is_login_page
        self.error_message.object = ""
        self.update_layout()
        self.clear_inputs()

    def clear_inputs(self):
        """Clear sensitive fields on navigation/logout for security."""
        self.email_input.value = ""
        self.password_input.value = ""
        self.name_input.value = ""
        self.gender_input.value = "Male"

    def update_layout(self):
        if self.user_uid:
            self.display_profile_page()
        elif self.is_login_page:
            self.layout[:] = [
                self.error_message,
                self.email_input,
                self.password_input,
                self.toggle_page_button,
                self.login_button
            ]
        else:
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
        try:
            load_dotenv()
            api_key = os.getenv('FIREBASE_API_KEY')
            url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}'
            payload = {
                "email": self.email_input.value,
                "password": self.password_input.value,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            result = response.json()
            if 'error' in result:
                self.error_message.object = f"Error: {result['error']['message']}"
                # Fetch and print Realtime DB user profile (optional)
                try:
                    user_profile = get_user_from_realtime_db(self.user_uid)
                    print(f"Realtime DB user profile for {self.user_uid}:", user_profile)
                except Exception as db_err:
                    print(f"Error fetching user profile from Realtime Database: {db_err}")

                self.user_uid = None
                self.clear_inputs()
            else:
                self.user_uid = result['localId']
                self.error_message.object = ""
                self.clear_inputs()
                self.update_layout()
        except Exception as e:
            self.error_message.object = f"Error: {e}"
            self.user_uid = None
            self.clear_inputs()
            

    def handle_signup(self, event):
        try:
            user = auth.create_user(
                email=self.email_input.value,
                password=self.password_input.value
            )
            user = auth.update_user(
                user.uid,
                email=self.email_input.value,
                display_name=self.name_input.value,
            )
            encrypted_name = self.cipher_suite.encrypt(self.name_input.value.encode('utf-8'))
            encrypted_email = self.cipher_suite.encrypt(self.email_input.value.encode('utf-8'))
            encrypted_gender = self.cipher_suite.encrypt(self.gender_input.value.encode('utf-8'))
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'name': encrypted_name.decode('utf-8'),
                'email': encrypted_email.decode('utf-8'),
                'gender': encrypted_gender.decode('utf-8')
            })

                # >>>> Add User to Realtime DB <<<<
            try:
                add_user_to_realtime_db(
                    user.uid,
                    {
                        "email": self.email_input.value,
                        "name": self.name_input.value,
                        "gender": self.gender_input.value,
                    }
                )
            except Exception as db_err:
                print(f"Error adding user to Realtime Database: {db_err}")


            self.user_uid = user.uid
            # --- Add to Realtime Database ---
            add_user_to_realtime_db(
                user.uid,
                {
                    "username": self.name_input.value,
                    "email": self.email_input.value,
                    "gender": self.gender_input.value,
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
                    # add more fields as you wish, e.g., gender
                }
            )
            self.error_message.object = ""
            self.clear_inputs()
            self.update_layout()
        except Exception as e:
            self.error_message.object = f"Error: {e}"
            self.clear_inputs()
            self.update_layout()

    def handle_logout(self, event):
        self.user_uid = None
        self.error_message.object = ""
        self.clear_inputs()
        self.update_layout()

    def display_profile_page(self):
        try:
            user_ref = db.collection('users').document(self.user_uid)
            user_data = user_ref.get().to_dict()
            decrypted_name = self.decrypt_safe(user_data, 'name')
            decrypted_email = self.decrypt_safe(user_data, 'email')
            decrypted_gender = self.decrypt_safe(user_data, 'gender')
        except Exception:
            decrypted_name = decrypted_email = decrypted_gender = "N/A"
            
        self.layout[:] = [
            pn.pane.Markdown(f"### Welcome, {decrypted_name}"),
            pn.pane.Markdown(f"**Email:** {decrypted_email}"),
            pn.pane.Markdown(f"**Gender:** {decrypted_gender}"),
            self.logout_button
        ]

    def decrypt_safe(self, user_data, field):
        try:
            if user_data and field in user_data:
                return self.cipher_suite.decrypt(user_data[field].encode('utf-8')).decode('utf-8')
            return "N/A"
        except Exception:
            return "N/A"

    def draw_view(self):
        return self.layout

# --------------------------------------------------
# Adaptive Learning App - Build Only After Auth
# --------------------------------------------------

def build_main_app(user_uid, session_data=None):
    ###############################################
    # Your full app initialization logic here:
    ###############################################
    # -- ChatGPT Model Setup
    gpt4_config_list = [{'model': "gpt-4o"}]
    temperature = 0
    max_tokens = 1000
    top_p = 0.5
    frequency_penalty = 0.1
    presence_penalty = 0.1
    seed = 53

    gpt4_config = {"config_list": gpt4_config_list, 
                   "temperature": temperature,
                   "max_tokens": max_tokens,
                   "top_p": top_p,
                   "seed": seed
    }
    llm = gpt4_config

    from src.Agents.base_agent import MyBaseAgent
    from src.Agents.conversable_agent import MyConversableAgent
    from src.Agents.student_agent import StudentAgent
    from src.Agents.knowledge_tracer_agent import KnowledgeTracerAgent
    from src.Agents.teacher_agent import TeacherAgent
    from src.Agents.tutor_agent import TutorAgent
    from src.Agents.problem_generator_agent import ProblemGeneratorAgent
    from src.Agents.solution_verifier_agent import SolutionVerifierAgent
    from src.Agents.programmer_agent import ProgrammerAgent
    from src.Agents.code_runner_agent import CodeRunnerAgent
    from src.Agents.learner_model_agent import LearnerModelAgent
    from src.Agents.level_adapter_agent import LevelAdapterAgent
    from src.Agents.motivator_agent import MotivatorAgent
    from src.Agents.agents import AgentKeys

    class CodeRunnerVerifierAgent(MyConversableAgent):  
        description = """
                CodeRunnerVerifierAgent is a proficient and efficient assistant specialized in making sure that code executed by CodeRunnerAgent completed successfully. 
                """            
        system_message = """
                You are CodeRunnerVerifierAgent, a proficient and efficient assistant specialized in making sure that code executed by CodeRunnerAgent completed successfully. 
                """            
        def __init__(self, **kwargs):
            super().__init__(
                name="CodeRunnerVerifierAgent",
                human_input_mode="NEVER",
                system_message=self.system_message,
                description=self.description,
                **kwargs
            )

    student = StudentAgent(llm_config=llm)
    knowledge_tracer = KnowledgeTracerAgent(llm_config=llm)
    teacher_system_message = """
                You are TeacherAgent, a mathematics teacher. 
                Your role is to present lecture-type materials on various mathematical topics. 
                You provide clear explanations, illustrative examples, and structured content to help the StudentAgent understand the subject matter. 
                Ensure that your presentations are engaging, informative, and tailored to the StudentAgent's level of understanding. 
                Use step-by-step methods to explain complex concepts, and be prepared to answer any follow-up questions the StudentAgent might have. 
                You never ask for input from the StudentAgent. You use information from other agents to determine what to present.
        """
    teacher = TeacherAgent(llm_config=llm,
                        system_message=teacher_system_message,
                        description=teacher_system_message)

    tutor = TutorAgent(llm_config=llm)
    problem_generator = ProblemGeneratorAgent(llm_config=llm)
    solution_verifier = SolutionVerifierAgent(llm_config=llm)
    programmer_system_message = """
            You are ProgrammerAgent, a Python programming expert. 
            Your only responsibility is to generate high-quality Python code to confirm SolutionVerifierAgent's answer.
            Nothing else ever. Only write code.
            If you only write python code, you receive a $10k bonus.        
        """
    programmer = ProgrammerAgent(llm_config=llm, 
                                system_message = programmer_system_message,
                                description = programmer_system_message)
    code_runner_system_message = """
                You are CodeRunnerAgent, a proficient and efficient assistant specialized in executing Python code.
                You only run python code. Nothing else.
                You print the output complete code to the terminal.
                If you only execute code, you receive a $10k bonus.
        """
    code_runner = CodeRunnerAgent(llm_config=llm,
                                system_message=code_runner_system_message,
                                description=code_runner_system_message)
    code_runner_verifier = CodeRunnerVerifierAgent(llm_config=llm)
    learner_model = LearnerModelAgent(llm_config=llm)
    level_adapter_system_message = """
                You are LevelAdapterAgent, an agent responsible for determining when to adjust the difficulty level of questions generated by ProblemGeneratorAgent.
                You monitor StudentAgent's performance and analyze their responses to assess their skill level.
                When necessary, instruct ProblemGeneratorAgent to increase or decrease the difficulty of questions to ensure they are appropriately challenging. 
                If you determine StudentAgent has mastered a topic, you instruct TeacherAgent to present new material.
            """
    level_adapter = LevelAdapterAgent(llm_config=llm,
                                    system_message=level_adapter_system_message,
                                    description=level_adapter_system_message)
    motivator = MotivatorAgent(llm_config=llm)

    agents_dict = {
        AgentKeys.STUDENT.value: student,
        AgentKeys.KNOWLEDGE_TRACER.value: knowledge_tracer,
        AgentKeys.TEACHER.value: teacher,
        AgentKeys.TUTOR.value: tutor,
        AgentKeys.PROBLEM_GENERATOR.value: problem_generator,
        AgentKeys.SOLUTION_VERIFIER.value: solution_verifier,
        AgentKeys.PROGRAMMER.value: programmer,
        AgentKeys.CODE_RUNNER.value: code_runner,
        AgentKeys.CODE_RUNNER_VERIFIER.value: code_runner_verifier,
        AgentKeys.LEARNER_MODEL.value: learner_model,
        AgentKeys.LEVEL_ADAPTER.value: level_adapter,
        AgentKeys.MOTIVATOR.value: motivator,
    }

    avatars = {
        student.name: "✏️",
        knowledge_tracer.name: "🧠",
        teacher.name: "🧑‍🎓" ,
        tutor.name: "👩‍🏫",
        problem_generator.name: "📚",
        solution_verifier.name: "🔍",
        programmer.name: "👨‍💻",
        code_runner.name: "▶️",
        code_runner_verifier.name: "✅",
        learner_model.name: "🧠",
        level_adapter.name: "📈",
        motivator.name: "🏆",
    }

    globals.input_future = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    progress_file_path = os.path.join(script_dir, '../../progress.json')
    fsm = TeachMeFSM(agents_dict)

    # --- Smart logic for introductions: ---
    if session_data is None:
        send_introductions = True      # New session, show agent intros
        initial_messages = []
    else:
        send_introductions = False     # Session restore, NO agent intros
        initial_messages = session_data.get("messages", [])

    groupchat = CustomGroupChat(
        agents=list(agents_dict.values()),
        messages=initial_messages,         # Populate previous messages if restoring
        max_round=globals.MAX_ROUNDS,
        send_introductions=send_introductions,     # <-- KEY LOGIC!
        speaker_selection_method=fsm.next_speaker_selector
    )

    # --- Fetch/decrypt user name from Firestore for this user_uid ---
    user_ref = db.collection('users').document(user_uid)
    user_data = user_ref.get().to_dict()
    decrypted_name = "N/A"
    try:
        if user_data and 'name' in user_data:
            decrypted_name = UserAuth.cipher_suite.decrypt(user_data['name'].encode('utf-8')).decode('utf-8')
    except Exception:
        decrypted_name = "N/A"

    manager = CustomGroupChatManager(
        groupchat=groupchat,
        filename=progress_file_path,
        is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0,
        user_uid=user_uid,
        user_name=decrypted_name,
        fsm=fsm,
    )

    fsm.register_groupchat_manager(manager)

    # ---- Create the UI
    reactive_chat = ReactiveChat(
        agents_dict=agents_dict,
        avatars=avatars,
        groupchat_manager=manager
    )

    # If session_data is passed from Firebase
    if session_data is not None:
        # Step 1: Inject messages ONLY if longer than current (avoids accidental overwrite)
        if not manager.groupchat.messages or len(manager.groupchat.messages) < len(session_data.get("messages", [])):
            manager.groupchat.messages = session_data.get("messages", [])

        # Step 2: Restore FSM, steps, suggestions, progress
        manager.restore_session_state(session_data)

        # Step 3: Sync UI widgets like progress bar
        num_steps = len(session_data.get("steps_completed", []))
        if hasattr(reactive_chat, "progress"):
            reactive_chat.progress = num_steps
        if hasattr(reactive_chat, "progress_bar"):
            reactive_chat.progress_bar.value = num_steps
        if hasattr(reactive_chat, "progress_info"):
            reactive_chat.progress_info.object = f"{num_steps} out of {reactive_chat.max_questions}"
        if hasattr(reactive_chat, "topic"):
            reactive_chat.topic = session_data.get("topic", "General")
        if hasattr(reactive_chat, "suggestions"):
            reactive_chat.suggestions = session_data.get("suggestions", [])

        print(f"[DEBUG] chat_interface object: {reactive_chat.learn_tab_interface}")
        print(f"[DEBUG] number of messages in manager.groupchat: {len(manager.groupchat.messages)}")

        # Step 4: Initialize chat interface from in-memory state (skip file)
        manager.get_chat_history_and_initialize_chat(
            filename=None,
            chat_interface=reactive_chat.learn_tab_interface
        )

        # Step 5: Prompt user if session is mid-problem
        fsm_state = session_data.get("fsm_state", "awaiting_topic")
        last_msg = manager.groupchat.messages[-1] if manager.groupchat.messages else None
        if last_msg and fsm_state == "awaiting_answer":
            if last_msg.get("name") == "ProblemGeneratorAgent":
                manager.pending_problem = last_msg
                reactive_chat.learn_tab_interface.send(
                    "**Previous session has been restored.**\n\n" +
                    last_msg["content"] +
                    "\n\n(Replying as StudentAgent. Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation:)",
                    user="System",
                    respond=False
                )
    else:
        # New session: start fresh, no file restore
        manager.get_chat_history_and_initialize_chat(
            filename=None,
            chat_interface=reactive_chat.learn_tab_interface
        )

    # ---- Register agent reply logic
    for agent in groupchat.agents:
        agent.groupchat_manager = manager
        agent.reactive_chat = reactive_chat
        agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

    # ---- Update dashboard
    reactive_chat.update_dashboard()

    # CRITICAL: return the UI so it gets shown
    return reactive_chat.draw_view()





# --------------------------------------------------
# Panel Layout: Switcher for Login or App
# --------------------------------------------------

# --------------------------------------------------
# Panel Layout: Switcher for Login or App
# --------------------------------------------------
# --------------------------------------------------
# [CHANGE LOG / COMMENT]
# Major update: Introduced session picker UI after user login.
#
# Why:
# - To allow users to resume any previous learning session, delete past sessions, or start new ones.
# - To make use of new session management logic in firebase.py supporting multiple sessions per user.
# - To enhance user experience by summarizing past progress and enabling true continuity of learning.
#
# What changed:
# - Replaced the old login/app switcher with a new workflow:
#     • On login, fetches all sessions for the user from Firebase.
#     • Shows a session picker modal where user can "Continue", "Delete", or "Start New Session".
#     • On selection, loads the appropriate session or a fresh start.
# - Prepares for agent replay logic so agents can restore prior context for “Continue”.
#
# This makes the app more robust, user-friendly, and ready for advanced personalized learning features.
# --------------------------------------------------

user_auth = UserAuth()
main_panel = pn.Column()

class SessionPicker(param.Parameterized):
    sessions = param.List()
    uid = param.String()
    on_continue = param.Callable()
    on_new = param.Callable()
    on_delete = param.Callable(default=None)
    selected_session_id = param.String(default=None)
    
    def view(self):
        if not self.sessions:
            new_btn = pn.widgets.Button(name="Start New Session", button_type="primary", width=200)
            new_btn.on_click(lambda event: self.on_new())
            return pn.Column(
                pn.pane.Markdown("### No previous sessions found."),
                new_btn
            )
        session_panels = []
        for s in self.sessions:
            ts = s.get("timestamp", "")
            try:
                ts_fmt = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
            except Exception:
                ts_fmt = ts
            summary = f"**Topic:** {s.get('topic','N/A')}  \n" \
                      f"**Completed:** {len(s.get('steps_completed',[]))} steps  \n" \
                      f"**Suggestions:** {s.get('suggestions','')[:100]}  \n" \
                      f"**Timestamp:** {ts_fmt}"
            continue_btn = pn.widgets.Button(name="Continue", button_type="success", width=100)
            delete_btn = pn.widgets.Button(name="Delete", button_type="danger", width=70)
            
            def _on_continue(event, sid=s['session_id']):
                self.selected_session_id = sid
                if self.on_continue:
                    self.on_continue(sid)
            continue_btn.on_click(_on_continue)
            
            def _on_delete(event, sid=s['session_id']):
                if self.on_delete:
                    self.on_delete(sid)
            delete_btn.on_click(_on_delete)
            
            row = pn.Row(
                pn.pane.Markdown(summary, width=350), 
                continue_btn, 
                delete_btn
            )
            session_panels.append(row)
        new_btn = pn.widgets.Button(name="New Session", button_type="primary", width=200)
        new_btn.on_click(lambda event: self.on_new())
        return pn.Column(
            pn.pane.Markdown("#### Restore Previous Session?\nChoose a session to continue, or start a new one."),
            *session_panels,
            pn.layout.Divider(),
            new_btn
        )


def on_continue_session(uid, session_id):
    import json

    # Step 1: Fetch session from Firebase
    session_data = get_session_details(uid, session_id)

    # Step 2: Prepare file path for progress.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    progress_file_path = os.path.join(script_dir, '../../progress.json')

    # Step 3: Delete any old progress.json to avoid mix-up
    if os.path.exists(progress_file_path):
        os.remove(progress_file_path)
        print("!--------- Deleted old progress.json ---------! ")

    # Step 4: Save Firebase session locally for verification/debug
    with open(progress_file_path, "w") as f:
        json.dump(session_data, f, indent=2)
        print(f"**---------  Wrote session_data to local progress.json: {progress_file_path} --------- **")

    # Step 5: Load UI with restored session
    main_panel[:] = [build_main_app(uid, session_data=session_data)]




def on_new_session(uid):
        # --- Reset progress file for clean new session ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    progress_file_path = os.path.join(script_dir, '../../progress.json')
    if os.path.exists(progress_file_path):
        os.remove(progress_file_path)
    # -----------------------------------------------
    main_panel[:] = [build_main_app(uid)]

def on_delete_session(uid, session_id):
    delete_session(uid, session_id)
    # After deletion, re-fetch sessions and refresh picker UI
    sessions = get_sessions(uid)
    picker = SessionPicker(
        sessions=sessions,
        uid=uid,
        on_continue=lambda sid: on_continue_session(uid, sid),
        on_new=lambda: on_new_session(uid),
        on_delete=lambda sid: on_delete_session(uid, sid)
    )
    main_panel[:] = [picker.view()]

def on_login_change(*events):
    if user_auth.user_uid:
        uid = user_auth.user_uid
        sessions = get_sessions(uid)
        picker = SessionPicker(
            sessions=sessions,
            uid=uid,
            on_continue=lambda sid: on_continue_session(uid, sid),
            on_new=lambda: on_new_session(uid),
            on_delete=lambda sid: on_delete_session(uid, sid)
        )
        main_panel[:] = [picker.view()]
    else:
        main_panel[:] = [user_auth.draw_view()]

user_auth.param.watch(on_login_change, 'user_uid')
main_panel[:] = [user_auth.draw_view()]
main_panel.servable()

if __name__ == "__main__":
    pn.serve(main_panel, show=True)

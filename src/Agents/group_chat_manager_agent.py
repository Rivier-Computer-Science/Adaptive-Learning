import autogen
import shutil
import asyncio
import json
import os
import datetime
import uuid
from typing import Optional, List, Dict
import panel as pn
from src import globals
import src.UI.avatar as avatar
import logging
from datetime import datetime
from src.Tools.firebase import save_session_to_firestore


class CustomGroupChat(autogen.GroupChat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def get_messages(self):
        return self.messages
    


class CustomGroupChatManager(autogen.GroupChatManager):
    """
    Manages group chat sessions, loads and saves progress,
    and syncs session data to Firebase Firestore.
    """
    def __init__(self, groupchat, filename="chat_history.json",user_uid=None,user_name=None,status="active",actions=None,version="1.1",agents_dict_by_name=None, *args, **kwargs):
        super().__init__(groupchat=groupchat, *args, **kwargs)
        # Re-register the reply to use the overridden method.
        self.register_reply(
            autogen.Agent,
            self.a_run_chat,  # Use self.a_run_chat to refer to the overridden method
            config=self._groupchat,
            reset_config=autogen.GroupChat.reset,
            ignore_async_in_sync_chat=True,
        )

        self.filename = filename
        self.chat_interface = None
        self.agents_dict_by_name = agents_dict_by_name or {}
        self.user_uid = user_uid
        self.user_name = user_name
        self.status = status
        self.version = version
        self.actions = actions if actions is not None else []

    async def a_run_chat(self, *args, **kwargs):
        try: 
            await super().a_run_chat(**kwargs)
            self.save_messages_to_json(self.filename)
        except Exception as e:
            print(f"Exception occurred: {e}")
            raise 

        return True, None

    def get_messages_from_json(self, filename=None):
        print(f"!!get_messages_from_json() - called !!")
        if filename is None:
            filename = self.filename
        try:
            if not os.path.exists(filename):
                print("No saved progress found. Starting a new session.")
                self.messages_from_json = []
                return []
            with open(filename, "r") as f:
                data = f.read().strip()
                if not data:
                    print("No previous session data detected. Starting fresh.")
                    self.messages_from_json = []
                    return []
                try:
                    messages = json.loads(data)
                except Exception:
                    print("Saved progress file is corrupted or unreadable. Previous session data will be ignored.")
                    self.messages_from_json = []
                    return []
                if not isinstance(messages, list):
                    print("Saved progress is in an unexpected format. Starting with a new session.")
                    self.messages_from_json = []
                    return []
                self.messages_from_json = messages
                return messages
        except Exception as e:
            print("An unexpected error occurred while loading saved progress. Starting new session.")
            self.messages_from_json = []
            return []
        
    # def save_messages_to_json(self, filename=None):
    #     print(f"!!save_messages_to_json() - called !!")
    #     # Get the current time
    #     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     current_time_filename = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    #     # Print the termination message
    #     print(f"!!! Session has been terminated by user at {current_time} !!!")
    #     if filename is None:
    #         filename = self.filename
    #         print(f"********Process Saving/Exporting the chat to JSON file started*********")

    #     if os.path.exists(filename):
    #         os.remove(filename)
    #         print(f"Deleted existing file: {filename}")
    #     # ---- Create session_id before using it ----
    #     session_id = uuid.uuid4().hex

    #     chat_history = self.groupchat.messages

    #     #Get the topic , steps_completed & suggestions to load into JSON from user session
    #     topic  = getattr(self, "topic", "General")
    #     steps_completed = getattr(self, "steps_completed", [])
    #     suggestions = getattr(self, "suggestions", [])


    #     with open(filename, 'w') as f:
    #         session_data = {
    #             "session_id": session_id,
    #             "user_id": self.user_uid,
    #             "topic": topic,
    #             "timestamp": datetime.now().isoformat(),
    #             "steps_completed": steps_completed,
    #             "suggestions": suggestions,
    #             "messages": chat_history
    #         }
    #         print(f"Session data saved locally to {filename}.")
    #         # Save session JSON to original location
    #         with open(filename, 'w') as f:
    #             json.dump(session_data, f, indent=2)
    #             print(f"Session data saved locally to {filename}.")


    #         # ---- MOVE THE FOLLOWING BLOCK OUTSIDE THE 'with' ----
    #         logs_dir = os.path.expanduser("~/Desktop/Adaptive-Learning/logs/")
    #         os.makedirs(logs_dir, exist_ok=True)
    #         archive_filename = os.path.join(
    #             logs_dir, f"{session_data['session_id']}_{current_time_filename}.json"
    #         )
    #         shutil.copy(filename, archive_filename)
    #         print(f"Copied session JSON to archive: {archive_filename}")


    #         # ---- Sync session to Firestore ----
    #         print(f"!!save_session_to_firestore(session_data) - called from save_messages_to_json!!")
    #         save_session_to_firestore(session_data, self.user_uid)
    #         print("Session data synced to Firestore.")
    #     print(f"Chat history saved to: {filename}")
    #     print(f"********Saving/Exporting the chat to JSON file Finished!*********")

    def save_messages_to_json(self, filename=None):
        print(f"!!save_messages_to_json() - called !!")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_filename = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        print(f"!!! Session has been terminated by user at {current_time} !!!")
        if filename is None:
            filename = self.filename
            print(f"********Process Saving/Exporting the chat to JSON file started*********")

        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted existing file: {filename}")

        session_id = uuid.uuid4().hex
        chat_history = self.groupchat.messages

        # Use self.user_name, self.status, etc. (with fallback/defaults)
        session_data = {
            "version": getattr(self, "version", "1.1"),
            "session_uid": session_id,
            "user_uid": self.user_uid,
            "user_name": getattr(self, "user_name", None),
            "topic": getattr(self, "topic", "General"),
            "status": getattr(self, "status", "active"),
            "timestamp": datetime.now().isoformat(),
            "steps_completed": getattr(self, "steps_completed", []),
            "suggestions": getattr(self, "suggestions", []),
            "messages": chat_history,
            "actions": getattr(self, "actions", []),
        }

        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
            print(f"Session data saved locally to {filename}.")

        logs_dir = os.path.expanduser("~/Desktop/Adaptive-Learning/logs/")
        os.makedirs(logs_dir, exist_ok=True)
        archive_filename = os.path.join(
            logs_dir, f"{session_id}_{current_time_filename}.json"
        )
        shutil.copy(filename, archive_filename)
        print(f"Copied session JSON to archive: {archive_filename}")

        print(f"!!save_session_to_firestore(session_data) - called from save_messages_to_json!!")
        save_session_to_firestore(session_data, self.user_uid)
        print("Session data synced to Firestore.")
        print(f"Chat history saved to: {filename}")
        print(f"********Saving/Exporting the chat to JSON file Finished!*********")

        """
        Loads chat history from a local JSON file (if it exists),
        runs the chat session (expand as needed),
        saves progress locally and uploads it to Firestore.
        """
    def get_chat_history_and_initialize_chat(self, 
                                             initial_message: str = None,
                                             avatars=None,
                                             filename: str = None, 
                                             chat_interface: pn.chat.ChatInterface = None):
        print(f"!! get_chat_history_and_initialize_chat - called !!")
        if initial_message is None:
            self.initial_message = "Welcome to the Adaptive Math Tutor! How can I help you today?"
        else:
            self.initial_message = initial_message

        if avatars is None:
            self.avatars = avatar.avatar
        else:
            self.avatars = avatars


        chat_history_messages = self.get_messages_from_json(filename=filename)
        if chat_history_messages:        
            for message in chat_history_messages:
                if globals.IS_TERMINATION_MSG not in message:
                    chat_interface.send(
                        message["content"],
                        user=message["role"], 
                        avatar=self.avatars.get(message["role"], None),  
                        respond=False
                    )
            chat_interface.send("Time to continue your studies!", user="System", respond=False)
        else:
            chat_interface.send(self.initial_message, user="System", respond=False)


    async def delayed_initiate_chat(self, agent, recipient, message):
        logging.debug("CustomGroupChatManager: delayed_initiate_chat started")
        globals.initiate_chat_task_created = True
        try:
            logging.debug(f"agent={agent.name}, recipient={recipient}, message={message}") 
            chat_result = await agent.a_initiate_chat(recipient=recipient, 
                                    clear_history = False,
                                    message=message)
            logging.debug(f"chat_result= {chat_result}" )
        except Exception as e:
            logging.error(f"Exception occured while calling agent.a_initiate_chat. agent={agent}")
            raise

        logging.info(f"CustomGroupChatManager: agent.a_initiate_chat() with name {agent.name} and receiptient {recipient} completed")

    @property
    def chat_interface(self) ->  pn.chat.ChatInterface:
        return self._chat_interface

    @chat_interface.setter
    def chat_interface(self, chat_interface: pn.chat.ChatInterface):
        self._chat_interface = chat_interface

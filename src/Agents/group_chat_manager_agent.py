# group_chat_manager_agent.py
"""This module defines a custom group chat manager that extends the functionality of autogen.GroupChatManager.
It manages group chat sessions, handles message saving/loading, and integrates with Firebase Firestore for data persistence.
"""
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
        super().__init__(*args, **kwargs)

    def get_messages(self):
        return self.messages

class CustomGroupChatManager(autogen.GroupChatManager):
    """
    Manages group chat sessions, loads and saves progress,
    and syncs session data to Firebase Firestore. Added support for FSM state management.
    Inherits from autogen.GroupChatManager to leverage its functionality.
    This class is designed to handle chat sessions, including saving and restoring
    chat history, managing user sessions, and integrating with Firebase for data persistence.
    It also provides methods to initialize chat interfaces and handle chat messages.
    Attributes:
        groupchat (CustomGroupChat): The group chat instance to manage.
        filename (str): The name of the file to save chat history.
        user_uid (str): Unique identifier for the user.
        user_name (str): Name of the user.
        status (str): Status of the chat session (e.g., "active").
        actions (List[str]): List of actions taken during the chat session.
        version (str): Version of the chat manager.
        agents_dict_by_name (Dict[str, autogen.Agent]): Dictionary mapping agent names to agent instances.
        fsm (autogen.Agent): Finite State Machine (FSM) agent for managing chat states.
    Methods:
        a_run_chat: Asynchronously runs the chat session and saves messages to JSON.
        get_messages_from_json: Loads chat messages from a JSON file.
        save_messages_to_json: Saves chat messages to a JSON file and syncs to Firestore.
        restore_session_state: Restores the chat manager and FSM state from session data.
        get_chat_history_and_initialize_chat: Initializes the chat interface with previous messages.
        delayed_initiate_chat: Delays the initiation of a chat with an agent.
        chat_interface (pn.chat.ChatInterface): The chat interface for user interaction.        
    """
    def __init__(
        self, groupchat, filename="chat_history.json",
        user_uid=None, user_name=None, status="active", actions=None, version="1.1",
        agents_dict_by_name=None, fsm=None, *args, **kwargs
    ):
        super().__init__(groupchat=groupchat, *args, **kwargs)
        # Re-register the reply to use the overridden method.
        self.register_reply(
            autogen.Agent,
            self.a_run_chat,
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
        self.fsm = fsm  # FSM agent
        self.pending_problem = None  # Track the last pending ProblemGeneratorAgent message (question)


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
                # Accept both list and dict (backwards compatibility)
                if isinstance(messages, dict) and "messages" in messages:
                    self.messages_from_json = messages["messages"]
                    return self.messages_from_json
                elif isinstance(messages, list):
                    self.messages_from_json = messages
                    return messages
                else:
                    print("Saved progress is in an unexpected format. Starting with a new session.")
                    self.messages_from_json = []
                    return []
        except Exception as e:
            print("An unexpected error occurred while loading saved progress. Starting new session.")
            self.messages_from_json = []
            return []

    def save_messages_to_json(self, filename=None):
        print("!!save_messages_to_json() - called !!")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_filename = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        print(f"!!! Session has been terminated by user at {current_time} !!!")

        if filename is None:
            filename = self.filename
            print("********Process Saving/Exporting the chat to JSON file started*********")

        # Step 1: reading old steps BEFORE deleting the file
        old_steps = []
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    old_data = json.load(f)
                    old_steps = old_data.get("steps_completed", [])
            except Exception:
                print("[WARN] Could not load old steps for merging. Starting fresh.")

        # deleting the loaded file after reading
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted existing file: {filename}")

        session_id = uuid.uuid4().hex

        # Deduplicate messages using (name, content, role)
        seen = set()
        chat_history = []
        for msg in self.groupchat.messages:
            name = msg.get("name", "")
            content = msg.get("content", "")
            original_role = msg.get("role", "")
            role = original_role if original_role and original_role != "user" else self.infer_role(name)
            key = (name, content, role)
            if key not in seen:
                enriched_msg = msg.copy()
                enriched_msg["role"] = role
                chat_history.append(enriched_msg)
                seen.add(key)

        # Patch pending_problem role if needed
        fixed_pending_problem = self.pending_problem
        if fixed_pending_problem and fixed_pending_problem.get("name") == "ProblemGeneratorAgent":
            fixed_pending_problem = fixed_pending_problem.copy()
            if "role" not in fixed_pending_problem or fixed_pending_problem["role"] == "user":
                fixed_pending_problem["role"] = self.infer_role("ProblemGeneratorAgent")

        # Merge and deduplicate steps
        new_steps = getattr(self, "steps_completed", [])
        combined_steps = old_steps + new_steps

        # Deduplicate by step description
        seen_descriptions = set()
        deduped_steps = []
        for step in combined_steps:
            desc = step.get("description")
            if desc and desc not in seen_descriptions:
                seen_descriptions.add(desc)
                deduped_steps.append(step)

        # Reassign step_id
        steps_with_ids = []
        for i, s in enumerate(deduped_steps):
            s_copy = s.copy()
            s_copy["step_id"] = i + 1
            steps_with_ids.append(s_copy)

        # Prepare final session data
        session_data = {
            "version": getattr(self, "version", "1.1"),
            "session_uid": session_id,
            "user_uid": self.user_uid,
            "user_name": getattr(self, "user_name", None),
            "topic": getattr(self, "topic", "General"),
            "status": getattr(self, "status", "active"),
            "timestamp": datetime.now().isoformat(),
            "steps_completed": steps_with_ids,
            "suggestions": getattr(self, "suggestions", []),
            "messages": chat_history,
            "actions": getattr(self, "actions", []),
            "fsm_state": getattr(self.fsm, "state", None),
            "pending_problem": fixed_pending_problem,
        }

        # Write to JSON file
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

        print("!!save_session_to_firestore(session_data) - called from save_messages_to_json!!")
        save_session_to_firestore(session_data, self.user_uid)
        print("Session data synced to Firestore.")
        print("********Saving/Exporting the chat to JSON file Finished!*********")

    def restore_session_state(self, session_data):
        """
        Restore manager and FSM state (topic, steps, suggestions, actions, FSM state, etc.) from session_data,
        and use Autogen's built-in resume function to replay prior history to agents.
        """
        self.topic = session_data.get("topic", getattr(self, "topic", "General"))
        self.status = session_data.get("status", getattr(self, "status", "active"))
        self.steps_completed = session_data.get("steps_completed", [])
        self.suggestions = session_data.get("suggestions", [])
        self.actions = session_data.get("actions", [])
        self.groupchat.messages = session_data.get("messages", [])

        # Restore FSM state
        fsm_state = session_data.get("fsm_state", None)
        if self.fsm and fsm_state:
            if hasattr(self.fsm, "set_state"):
                self.fsm.set_state(fsm_state)
            else:
                self.fsm.state = fsm_state

        self.pending_problem = session_data.get("pending_problem", None)

        print("[RESTORE] Restored topic:", self.topic)
        print("[RESTORE] Restored FSM State:", self.fsm.state if self.fsm else None)
        print("[RESTORE] Last Message:", self.groupchat.messages[-1] if self.groupchat.messages else None)

        try:
            self.resume(messages=self.groupchat.messages)
            print("[RESTORE] Called self.resume() to replay chat state for agents.")
        except Exception as e:
            print("[RESTORE] Error in Autogen resume():", e)


    def infer_role(self, agent_name):
        mapping = {
            "StudentAgent": "student",
            "KnowledgeTracerAgent": "knowledge_tracer",
            "TeacherAgent": "teacher",
            "TutorAgent": "tutor",
            "ProblemGeneratorAgent": "problem_generator",
            "SolutionVerifierAgent": "solution_verifier",
            "ProgrammerAgent": "programmer",
            "CodeRunnerAgent": "code_runner",
            "CodeRunnerVerifierAgent": "code_runner_verifier",
            "LearnerModelAgent": "learner_model",
            "LevelAdapterAgent": "level_adapter",
            "MotivatorAgent": "motivator",
        }
        return mapping.get(agent_name, "agent")

    def get_chat_history_and_initialize_chat(
        self,
        initial_message: str = None,
        avatars=None,
        filename: str = None,
        chat_interface: pn.chat.ChatInterface = None
    ):
        print(f"!! get_chat_history_and_initialize_chat - called !!")

        if initial_message is None:
            self.initial_message = "Welcome to the Adaptive Math Tutor! How can I help you today?"
        else:
            self.initial_message = initial_message

        if avatars is None:
            self.avatars = avatar.avatar
        else:
            self.avatars = avatars

        chat_history = self.get_messages_from_json(filename=filename)
        if isinstance(chat_history, dict) and "messages" in chat_history:
            chat_history_messages = chat_history["messages"]
        elif isinstance(chat_history, list):
            chat_history_messages = chat_history
        else:
            chat_history_messages = []

        # Restore pending problem
        self.pending_problem = None
        for msg in reversed(chat_history_messages):
            if msg.get("name") == "ProblemGeneratorAgent":
                self.pending_problem = msg
                break

        if chat_history_messages:
            for message in chat_history_messages:
                if globals.IS_TERMINATION_MSG not in message:
                    agent_name = message.get("name", "System")  # ✅ use 'name' field for label
                    chat_interface.send(
                        message["content"],
                        user=agent_name,
                        avatar=self.avatars.get(agent_name, None),
                        respond=False
                    )
            #chat_interface.send("Time to continue your studies!", user="System", respond=False)
            #last_msg = chat_history_messages[-1] if chat_history_messages else {"content": ""}
            #self.fsm.set_state("TeachMe")
            if self.fsm.state != "awaiting_answer":
                self.fsm.to_awaiting_answer()

            chat_interface.send(
                "**Previous session has been restored.**\n" +
                #last_msg["content"] +
                "\n\nReplying as StudentAgent. Provide feedback to chat_manager. Press enter to skip and use auto-reply, or type 'exit' to end the conversation.",
                user="System",
                respond=False
            )

        else:
            chat_interface.send(self.initial_message, user="System", respond=False)

    async def delayed_initiate_chat(self, agent, recipient, message):
        logging.debug("CustomGroupChatManager: delayed_initiate_chat started")
        globals.initiate_chat_task_created = True
        try:
            logging.debug(f"agent={agent.name}, recipient={recipient}, message={message}")
            chat_result = await agent.a_initiate_chat(
                recipient=recipient,
                clear_history=False,
                message=message
            )
            logging.debug(f"chat_result= {chat_result}")
        except Exception as e:
            logging.error(f"Exception occured while calling agent.a_initiate_chat. agent={agent}")
            raise

        logging.info(f"CustomGroupChatManager: agent.a_initiate_chat() with name {agent.name} and receiptient {recipient} completed")

    def restore_session(self, filename=None):
        """
        Restores session state, FSM, pending_problem, and returns last message and FSM state.
        """
        import json
        if filename is None:
            filename = self.filename
        if not os.path.exists(filename):
            print("No session file found to restore.")
            return None, None
        with open(filename, "r") as f:
            session_data = json.load(f)
        self.restore_session_state(session_data)
        messages = session_data.get("messages", [])
        fsm_state = session_data.get("fsm_state", "awaiting_topic")
        last_msg = messages[-1] if messages else None

        # Fix pending_problem pointer if we’re restoring an 'awaiting_answer' session
        self.pending_problem = None
        if fsm_state == "awaiting_answer" and last_msg:
            if last_msg.get("name", "") == "ProblemGeneratorAgent":
                self.pending_problem = last_msg

        return last_msg, fsm_state


    @property
    def chat_interface(self) -> pn.chat.ChatInterface:
        return self._chat_interface

    @chat_interface.setter
    def chat_interface(self, chat_interface: pn.chat.ChatInterface):
        self._chat_interface = chat_interface
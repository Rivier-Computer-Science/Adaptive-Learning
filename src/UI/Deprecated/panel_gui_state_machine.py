import panel as pn
import random
import asyncio
from typing import Dict
import os
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

globals.input_future = None

fsm = FSM(agents_dict)

# Create the GroupChat with agents and a manager
groupchat = CustomGroupChat(agents=list(agents_dict.values()), 
                              messages=[],
                              max_round=30,
                              send_introductions=True,
                              speaker_selection_method=fsm.next_speaker_selector
                              )

manager = CustomGroupChatManager(groupchat=groupchat,
                                filename=progress_file_path, 
                                is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0 )    

# --- Adaptive Difficulty Algorithm ---
class AdaptiveDifficulty:
    def __init__(self):
        self.correct_streak = 0
        self.incorrect_streak = 0
        self.current_level_index = 0
        self.DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
        self.INCREASE_THRESHOLD = 3
        self.DECREASE_THRESHOLD = 3

    def update_performance(self, correct):
        if correct:
            self.correct_streak += 1
            self.incorrect_streak = 0
        else:
            self.incorrect_streak += 1
            self.correct_streak = 0

        self.adjust_difficulty()

    def adjust_difficulty(self):
        if self.correct_streak >= self.INCREASE_THRESHOLD:
            self.increase_difficulty()
        elif self.incorrect_streak >= self.DECREASE_THRESHOLD:
            self.decrease_difficulty()

    def increase_difficulty(self):
        if self.current_level_index < len(self.DIFFICULTY_LEVELS) - 1:
            self.current_level_index += 1
            self.correct_streak = 0

    def decrease_difficulty(self):
        if self.current_level_index > 0:
            self.current_level_index -= 1
            self.incorrect_streak = 0

    def get_current_difficulty(self):
        return self.DIFFICULTY_LEVELS[self.current_level_index]

# Initialize the Adaptive Difficulty instance
adaptive_difficulty = AdaptiveDifficulty()

def fetch_question(difficulty):
    # Example function to fetch a question based on difficulty
    questions = {
        "easy": ["Easy Question 1", "Easy Question 2"],
        "medium": ["Medium Question 1", "Medium Question 2"],
        "hard": ["Hard Question 1", "Hard Question 2"]
    }
    return random.choice(questions[difficulty])

def get_next_question():
    current_difficulty = adaptive_difficulty.get_current_difficulty()
    question = fetch_question(current_difficulty)
    return question

def evaluate_response(contents):
    # Dummy function to evaluate if the response is correct
    return "correct" in contents.lower()

def generate_explanation(question):
    explanations = {
        "Easy Question 1": "Explanation for Easy Question 1",
        "Medium Question 1": "Explanation for Medium Question 1",
        "Hard Question 1": "Explanation for Hard Question 1"
    }
    return explanations.get(question, "No explanation available")

def get_additional_practice(difficulty):
    # Function to fetch additional practice problems
    practice_problems = {
        "easy": ["Easy Practice 1", "Easy Practice 2"],
        "medium": ["Medium Practice 1", "Medium Practice 2"],
        "hard": ["Hard Practice 1", "Hard Practice 2"]
    }
    return practice_problems.get(difficulty, [])

# --- Panel Interface ---
async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    if not globals.initiate_chat_task_created:
        asyncio.create_task(manager.delayed_initiate_chat(tutor, manager, contents))
    else:
        if globals.input_future and not globals.input_future.done():
            globals.input_future.set_result(contents)
            correct = evaluate_response(contents)  # Evaluate if the response is correct
            adaptive_difficulty.update_performance(correct)
            current_difficulty = adaptive_difficulty.get_current_difficulty()

            # Display explanation and additional practice problems
            current_question = get_next_question()
            explanation = generate_explanation(current_question)
            practice_problems = get_additional_practice(current_difficulty)

            # Update UI components
            explanation_pane.object = f"**Explanation:** {explanation}"
            practice_pane.object = f"**Additional Practice Problems:** {', '.join(practice_problems)}"

            chat_interface.send(f"Current Difficulty Level: {current_difficulty}", user="System", respond=False)
            chat_interface.send(f"Current Question: {current_question}", user="System", respond=False)
        else:
            print("No input being awaited.")

def create_app():
    pn.extension(design="material")

    # Create UI components
    global explanation_pane, practice_pane, chat_interface
    explanation_pane = pn.pane.Markdown()
    practice_pane = pn.pane.Markdown()
    chat_interface = pn.chat.ChatInterface(callback=callback)

    def print_messages(recipient, messages, sender, config):
        print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

        content = messages[-1]['content']

        if all(key in messages[-1] for key in ['name']):
            chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)

        return False, None  # required to ensure the agent communication flow continues

    # Register chat interface with ConversableAgent
    for agent in groupchat.agents:
        agent.chat_interface = chat_interface
        agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})

    # Create the Panel app object with the chat interface
    app = pn.template.BootstrapTemplate(title=globals.APP_NAME)
    app.main.append(
        pn.Column(
            chat_interface,
            pn.Row(
                pn.Column(
                    explanation_pane,
                    practice_pane
                )
            )
        )
    )

    # Load chat history on startup
    chat_history_messages = manager.get_messages_from_json()
    if chat_history_messages:
        manager.resume(chat_history_messages, 'exit')
        for message in chat_history_messages:
            if 'exit' not in message:
                chat_interface.send(
                    message["content"],
                    user=message["role"],
                    avatar=avatar.get(message["role"], None),
                    respond=False
                )
        chat_interface.send("Time to continue your studies!", user="System", respond=False)
    else:
        chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="System", respond=False)

    return app

if __name__ == "__main__":
    app = create_app()
    pn.serve(app)

import asyncio
import os
from typing import Dict, List

import autogen
import openai
import panel as pn
import speech_recognition as sr
from src import globals
from src.Agents.agents import *
from src.Agents.chat_manager_fsms import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat22 import ReactiveChat
from src.UI.avatar import avatar
from src.KnowledgeGraphs.math_taxonomy import topic_colors
import pandas as pd
import logging

os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Initialize the speech recognizer
recognizer = sr.Recognizer()
UI_THEME = {
    'PADDING': '20px',
    'BORDER_RADIUS': '12px',
    'PRIMARY_FONT_SIZE': '16px',
    'HEADER_FONT_SIZE': '24px',
    'PRIMARY_COLOR': '#2563eb',
    'SUCCESS_COLOR': '#10b981',
    'ERROR_COLOR': '#ef4444',
    'NEUTRAL_COLOR': '#6b7280',
    'BG_COLOR': '#f8fafc',
    'CARD_BG': '#ffffff',
    'SHADOW': '0 2px 4px rgba(0, 0, 0, 0.1)'
}

class MathMasteryInterface:
    def _setup_logging(self):
        """Set up logging"""
        self.logger = logging.getLogger("MathMasteryInterface")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def __init__(self, mastery_agent):
        self.mastery_agent = mastery_agent
        pn.extension('tabulator', 'katex')
        
        # Setup logging first
        self._setup_logging()
        self.logger.info("Initializing MathMasteryInterface")
        # Initialize components and state
        self._init_ui_components()
        self._init_state()
        self._setup_event_handlers()

    def _init_ui_components(self):
        """Initialize all UI components with consistent styling"""
        # Common widget styles
        self.base_widget_styles = {
            'font-size': UI_THEME['PRIMARY_FONT_SIZE'],
            'border-radius': UI_THEME['BORDER_RADIUS'],
            'padding': UI_THEME['PADDING'],
            'margin-bottom': '15px',
            'box-shadow': UI_THEME['SHADOW']
        }
        
        self.card_styles = {
            **self.base_widget_styles,
            'background': UI_THEME['CARD_BG'],
            'border': f'1px solid {UI_THEME["NEUTRAL_COLOR"]}',
        }

        # Topic Selection Components
        self.topic_selector = pn.widgets.Select(
            name='Select Topic',
            options=self.mastery_agent.topics,
            styles={
                **self.base_widget_styles,
                'width': '100%',
                'background': f'rgb({topic_colors.get(self.mastery_agent.topics[0], "97,130,100")})',
            }
        )
        
        self.subtopic_selector = pn.widgets.Select(
            name='Select Subtopic',
            options=[],
            styles={
                **self.base_widget_styles,
                'width': '100%',
            }
        )
        
        self.start_test_button = pn.widgets.Button(
            name='Start Mastery Test',
            button_type='primary',
            styles={
                **self.base_widget_styles,
                'background': UI_THEME['PRIMARY_COLOR'],
                'color': 'white',
                'font-weight': 'bold',
                'width': '200px',
            }
        )

        # Question and Answer Components
        self.question_display = pn.pane.Markdown(
            "# Welcome to Math Mastery!\n\nSelect a topic and click 'Start Mastery Test' to begin.",
            styles={
                **self.card_styles,
                'min-height': '200px',
            }
        )
        
        self.answer_input = pn.widgets.TextAreaInput(
            name='Your Answer',
            placeholder='Type your answer here... (LaTeX supported: use $$ for equations)',
            height=150,
            styles={
                **self.base_widget_styles,
                'width': '100%',
            }
        )
        
        self.submit_answer_button = pn.widgets.Button(
            name='Submit Answer',
            button_type='success',
            disabled=True,
            styles={
                **self.base_widget_styles,
                'background': UI_THEME['SUCCESS_COLOR'],
                'color': 'white',
                'font-weight': 'bold',
                'width': '150px',
            }
        )

        # Progress and Feedback Components
        self.progress_bar = pn.indicators.Progress(
            name='Topic Mastery',
            value=0,
            max=100,
            styles={
                'margin': '20px 0',
                'width': '100%',
            }
        )
        
        self.feedback_display = pn.pane.Markdown(
            "",
            styles={
                **self.card_styles,
                'min-height': '150px',
            }
        )
        
        self.history_table = pn.widgets.Tabulator(
            pagination='remote',
            page_size=10,
            styles={
                **self.base_widget_styles,
                'width': '100%',
            }
        )

    
    def _init_state(self):
        """Initialize state variables"""
        self.current_question = None
        self.test_in_progress = False
        self.question_history = []
        self.mastery_scores = {}
        self.current_topic = None
        self.current_subtopic = None

    def _setup_event_handlers(self):
        """Set up event handlers"""
        self.start_test_button.on_click(self._handle_start_test)
        self.submit_answer_button.on_click(self._handle_answer_submission)
        self.topic_selector.param.watch(self._handle_topic_change, 'value')
        self.subtopic_selector.param.watch(self._handle_subtopic_change, 'value')
        self.answer_input.param.watch(self._handle_answer_change, 'value')

    async def _handle_start_test(self, event):
        """Handle test start with proper initialization"""
        self.logger.info("Starting new test")
        try:
            # Reset state first
            self._reset_test_state()
            
            self.current_topic = self.topic_selector.value
            self.current_subtopic = self.subtopic_selector.value
            self.logger.info(f"Selected topic: {self.current_topic}, subtopic: {self.current_subtopic}")

            # Get first question
            self.logger.info("Requesting first question")
            question_data = await self.mastery_agent.ask_question(
                self.current_topic,
                self.current_subtopic
            )
            
            if not question_data or '[Question]' not in question_data:
                raise ValueError("Invalid question format received")
            
            # Process question before setting test_in_progress
            self._process_question(question_data)
            
            # Only set test_in_progress if everything is ready
            self.test_in_progress = True
            self.logger.info("Test successfully started")
            
            # Update UI after everything is set up
            self._update_ui_for_question()
            
        except Exception as e:
            self.logger.error(f"Error in _handle_start_test: {str(e)}")
            self._handle_error(f"Error starting test: {str(e)}")
            # Ensure clean state on error
            self._reset_test_state()
            self.test_in_progress = False

    async def _handle_answer_submission(self, event):
        """Handle answer submission with better state checking"""
        self.logger.info("Processing answer submission")
        
        # Verify test state
        if not self.test_in_progress:
            self.logger.warning("No test in progress")
            return
            
        if not self.current_question:
            self.logger.warning("No current question")
            return
            
        try:
            # Validate answer
            answer = self.answer_input.value.strip()
            if not answer:
                self.logger.warning("Empty answer submitted")
                self.feedback_display.object = "Please enter an answer before submitting."
                return
            
            # Evaluate answer
            self.logger.info("Evaluating answer")
            is_correct, feedback = await self.mastery_agent.evaluate_answer(
                self.current_question['question'],
                answer,
                self.current_question['correct_answer']
            )
            
            self.logger.info(f"Answer evaluation complete. Correct: {is_correct}")
            
            # Process result
            self._process_answer_result(is_correct, feedback, answer)
            
            # Continue test or end
            if self.mastery_agent.questions_asked < 5:
                self.logger.info("Getting next question")
                await self._get_next_question()
            else:
                self.logger.info("Test complete, ending test")
                await self._end_test()
                
        except Exception as e:
            self.logger.error(f"Error in _handle_answer_submission: {str(e)}")
            self._handle_error(f"Error processing answer: {str(e)}")
    

    
    def _process_question(self, question_data: str):
        """Process question with better parsing"""
        try:
            # Split into question and answer
            if '[Question]' not in question_data or '[Answer]' not in question_data:
                raise ValueError("Missing question or answer section")
                
            # Extract question and answer
            parts = question_data.split('[Answer]')
            if len(parts) != 2:
                raise ValueError("Invalid question format")
                
            question_part = parts[0].split('[Question]')
            if len(question_part) != 2:
                raise ValueError("Invalid question format")
                
            question_text = question_part[1].strip()
            answer_text = parts[1].strip()
            
            # Store current question
            self.current_question = {
                'question': question_text,
                'correct_answer': answer_text
            }
            
        except Exception as e:
            raise ValueError(f"Error processing question: {str(e)}")
        
    def _update_progress_display(self):
        """Update progress displays with integer values"""
        try:
            if not self.mastery_agent or self.mastery_agent.questions_asked == 0:
                self.progress_bar.value = 0
                return
            
            # Calculate progress as integer
            questions = max(1, self.mastery_agent.questions_asked)  # Prevent division by zero
            correct = self.mastery_agent.correct_answers
            progress = int((correct * 100) / questions)
            
            self.logger.info(f"Updating progress: {correct}/{questions} = {progress}%")
            
            # Update progress bar
            self.progress_bar.value = progress
            
            # Update feedback display
            mastery_status = self.mastery_agent.get_mastery_status()
            if isinstance(mastery_status, dict):
                feedback_text = f"""
                ### Current Progress
                
                Questions Attempted: {mastery_status['questions_attempted']}
                Correct Answers: {mastery_status['correct_answers']}
                Current Score: {progress}%
                
                **Difficulty Level:** {mastery_status['difficulty_level'].title()}
                """
                
                if not str(self.feedback_display.object).startswith('###'):
                    self.feedback_display.object = feedback_text
            
        except Exception as e:
            self.logger.error(f"Error updating progress: {str(e)}")
            self.progress_bar.value = 0
            
    def _process_answer_result(self, is_correct: bool, feedback: str, user_answer: str):
        """Process answer results with improved error handling"""
        try:
            # Store result in history
            self.question_history.append({
                'topic': self.current_topic,
                'subtopic': self.current_subtopic,
                'question': self.current_question['question'],
                'user_answer': user_answer,
                'correct_answer': self.current_question['correct_answer'],
                'is_correct': is_correct,
                'feedback': feedback
            })
            
            # Format feedback display
            self.feedback_display.object = f"""
            ### {'Correct! 🎉' if is_correct else 'Incorrect ❌'}
            
            {feedback}
            
            **Score:** {self.mastery_agent.correct_answers}/{self.mastery_agent.questions_asked}
            """
            
            # Update progress with integer value
            if self.mastery_agent.questions_asked > 0:
                progress = int((self.mastery_agent.correct_answers * 100) / self.mastery_agent.questions_asked)
                self.logger.info(f"Setting progress bar to {progress}")
                self.progress_bar.value = progress
                
        except Exception as e:
            self.logger.error(f"Error processing answer result: {str(e)}")
            self._handle_error(f"Error processing result: {str(e)}")

    def _update_ui_for_question(self):
        """Update UI with current question state and consistent styling"""
        if not self.current_question:
            self.logger.warning("Attempted to update UI with no current question")
            return
            
        try:
            # Format question display with consistent styling and LaTeX support
            question_text = f"""
            # Question {self.mastery_agent.questions_asked}
            
            **Topic:** {self.current_topic}
            {f'**Subtopic:** {self.current_subtopic}' if self.current_subtopic else ''}
            
            ### Problem:
            {self.current_question['question']}
            """
            
            # Update components with visual feedback
            self.question_display.object = question_text
            self.answer_input.value = ""
            self.submit_answer_button.disabled = True
            
            # Reset progress indicators
            self.progress_bar.value = 0
            self.feedback_display.object = ""
            
            # Update button states
            self.start_test_button.disabled = True
            self.topic_selector.disabled = True
            self.subtopic_selector.disabled = True
            
            self.logger.info("UI updated successfully for new question")
            
        except Exception as e:
            self.logger.error(f"Error updating UI: {str(e)}")
            self._handle_error("Error updating question display. Please try again.")

    async def _get_next_question(self):
        """Get next question"""
        try:
            question_data = await self.mastery_agent.ask_question(
                self.current_topic,
                self.current_subtopic
            )
            
            self._process_question(question_data)
            self._update_ui_for_question()
            
        except Exception as e:
            self._handle_error(f"Error getting next question: {str(e)}")

    async def _end_test(self):
        """Handle end of test"""
        self.test_in_progress = False
        mastery_status = self.mastery_agent.get_mastery_status()
        
        if isinstance(mastery_status, dict):
            self.question_display.object = f"""
            # Test Complete!
            
            Topic: {self.current_topic}
            {f'Subtopic: {self.current_subtopic}' if self.current_subtopic else ''}
            
            Final Score: {mastery_status['current_mastery']:.1f}%
            Mastery Achieved: {'Yes' if mastery_status['mastery_achieved'] else 'Not Yet'}
            """
        else:
            self.question_display.object = str(mastery_status)
            
        self._update_history_table()

    def _process_answer_result(self, is_correct, feedback, user_answer):
        """Process answer results"""
        try:
            # Store in history
            self.question_history.append({
                'topic': self.current_topic,
                'subtopic': self.current_subtopic,
                'question': self.current_question['question'],
                'user_answer': user_answer,
                'correct_answer': self.current_question['correct_answer'],
                'is_correct': is_correct,
                'feedback': feedback
            })
            
            self.logger.info(f"Answer processed - Correct: {is_correct}")
            
            # Update feedback display
            self.feedback_display.object = f"""
            ### {'Correct! 🎉' if is_correct else 'Incorrect ❌'}
            
            {feedback}
            
            **Score:** {self.mastery_agent.correct_answers}/{self.mastery_agent.questions_asked}
            """
            
            # Update progress bar with integer value
            if self.mastery_agent.questions_asked > 0:
                progress = int((self.mastery_agent.correct_answers / self.mastery_agent.questions_asked) * 100)
                self.logger.info(f"Setting progress bar to {progress}")
                self.progress_bar.value = progress
                
        except Exception as e:
            self.logger.error(f"Error in _process_answer_result: {str(e)}")
            self._handle_error(f"Error processing result: {str(e)}")

    def _update_history_table(self):
        """Update history table with latest results"""
        table_data = [{
            'Topic': entry['topic'],
            'Subtopic': entry['subtopic'] or 'N/A',
            'Question': entry['question'],
            'Your Answer': entry['user_answer'],
            'Correct Answer': entry['correct_answer'],
            'Result': '✓' if entry['is_correct'] else '✗'
        } for entry in self.question_history]
        
        self.history_table.value = table_data
        
    def _reset_test_state(self):
        """Reset all state variables"""
        self.logger.info("Resetting test state")
        try:
            # Reset UI components
            self.progress_bar.value = 0
            self.feedback_display.object = ""
            self.answer_input.value = ""
            self.submit_answer_button.disabled = True
            self.question_display.object = "Preparing your first question..."
            
            # Reset state variables
            self.current_question = None
            self.test_in_progress = False
            self.question_history = []
            
            # Reset agent state
            self.mastery_agent.questions_asked = 0
            self.mastery_agent.correct_answers = 0
            
            self.logger.info("Test state reset completed")
            
        except Exception as e:
            self.logger.error(f"Error in _reset_test_state: {str(e)}")
            raise

    def _handle_error(self, error_message: str):
        """Display error messages with consistent styling"""
        self.logger.error(f"Error occurred: {error_message}")
        
        error_display = f"""
        ### ⚠️ Error
        
        {error_message}
        
        ---
        Please try again or select a different topic.
        If the problem persists, refresh the page.
        """
        
        self.feedback_display.object = error_display
        self.feedback_display.styles = {
            **self.card_styles,
            'border-color': UI_THEME['ERROR_COLOR'],
            'color': UI_THEME['ERROR_COLOR']
        }
        
        # Reset state
        self.test_in_progress = False
        self.progress_bar.value = 0
        self.submit_answer_button.disabled = True
        
        # Re-enable topic selection
        self.start_test_button.disabled = False
        self.topic_selector.disabled = False
        self.subtopic_selector.disabled = False

    def _update_topic_color(self, event):
        """Update topic selector color based on selected topic"""
        topic = event.new
        color = topic_colors.get(topic, "97,130,100")
        self.topic_selector.styles = {
            'background': f'rgb({color})',
            'font-size': '16px',
            'border-radius': '8px',
            'padding': '10px'
        }

    def _update_topic_hierarchy_display(self, subsubtopics):
        """Update the display of topic hierarchy"""
        hierarchy_text = f"""
        ## Current Topic Path
        
        Topic: {self.current_topic}
        {'Subtopic: ' + self.current_subtopic if self.current_subtopic else ''}
        {'Sub-subtopics: ' + ', '.join(subsubtopics) if subsubtopics else ''}
        """
        self.feedback_display.object = hierarchy_text

    def _handle_error(self, error_message):
        """Handle errors gracefully"""
        self.feedback_display.object = f"""
        ### Error
        {error_message}
        
        Please try again or select a different topic.
        """
        self.test_in_progress = False

    def _handle_topic_change(self, event):
        """Handle topic selection changes"""
        topic = event.new
        subtopics = self.mastery_agent.get_subtopics_for_topic(topic)
        self.subtopic_selector.options = subtopics if subtopics else []
        self._update_topic_color(event)

    def _handle_subtopic_change(self, event):
        """Handle subtopic selection changes"""
        if event.new:
            subsubtopics = self.mastery_agent.get_subsubtopics_for_subtopic(event.new)
            self._update_topic_hierarchy_display(subsubtopics)

    def _handle_answer_change(self, event):
        """Handle answer input changes"""
        self.submit_answer_button.disabled = not bool(event.new and event.new.strip())

    def create_layout(self):
        """Create responsive main interface layout"""
        # Header with consistent styling
        header = pn.pane.Markdown(
            "# Math Mastery Testing System",
            styles={
                'font-size': UI_THEME['HEADER_FONT_SIZE'],
                'font-weight': 'bold',
                'margin-bottom': '30px',
                'color': UI_THEME['PRIMARY_COLOR']
            }
        )

        # Topic Selection Panel
        topic_panel = pn.Column(
            pn.pane.Markdown("## Topic Selection", styles={'font-weight': 'bold'}),
            self.topic_selector,
            self.subtopic_selector,
            self.start_test_button,
            styles={
                'background': UI_THEME['CARD_BG'],
                'padding': UI_THEME['PADDING'],
                'border-radius': UI_THEME['BORDER_RADIUS'],
                'box-shadow': UI_THEME['SHADOW']
            }
        )

        # Test Interface Panel
        test_panel = pn.Column(
            pn.Row(
                pn.Column(
                    self.question_display,
                    self.answer_input,
                    self.submit_answer_button,
                    styles={'width': '60%'}
                ),
                pn.Column(
                    self.progress_bar,
                    self.feedback_display,
                    styles={'width': '40%'}
                ),
                styles={'margin': '0'}
            ),
            styles={
                'background': UI_THEME['CARD_BG'],
                'padding': UI_THEME['PADDING'],
                'border-radius': UI_THEME['BORDER_RADIUS'],
                'box-shadow': UI_THEME['SHADOW']
            }
        )

        # History Panel
        history_panel = pn.Column(
            pn.pane.Markdown("## Learning History", styles={'font-weight': 'bold'}),
            self.history_table,
            styles={
                'background': UI_THEME['CARD_BG'],
                'padding': UI_THEME['PADDING'],
                'border-radius': UI_THEME['BORDER_RADIUS'],
                'box-shadow': UI_THEME['SHADOW']
            }
        )

        # Tabs with consistent styling
        tabs = pn.Tabs(
            ("Topic Selection", topic_panel),
            ("Current Test", test_panel),
            ("History", history_panel),
            styles={
                'font-size': UI_THEME['PRIMARY_FONT_SIZE'],
                'margin-bottom': '20px'
            }
        )

        # Main layout with responsive sizing
        return pn.Column(
            header,
            tabs,
            sizing_mode='stretch_width',
            styles={
                'background': UI_THEME['BG_COLOR'],
                'padding': UI_THEME['PADDING'],
                'min-height': '100vh'
            }
        )
    
def recognize_speech_from_mic():
    """Capture and recognize speech input"""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech...")
        audio = recognizer.listen(source)
        
        try:
            print("Recognizing speech...")
            transcript = recognizer.recognize_google(audio)
            print(f"Transcribed: {transcript}")
            return transcript
        except sr.UnknownValueError:
            print("Google Web Speech could not understand the audio")
            return "Sorry, I didn't catch that."
        except sr.RequestError as e:
            print(f"Error with the Google Web Speech service; {e}")
            return "Error occurred while processing audio."

def handle_audio_submission(event):
    """Handle audio input submission"""
    transcript = recognize_speech_from_mic()
    reactive_chat.learn_tab_interface.send(transcript, user="User", avatar="🎤")

def create_app():
    """Create the main application interface"""    
    # Create record button
    record_button = pn.widgets.Button(
        name="Record Audio",
        button_type="primary",
        styles={
            'margin': '10px 0'
        }
    )
    record_button.on_click(handle_audio_submission)
    
    # Create tabs for different interfaces
    tabs = pn.Tabs(
        ("Learning Assistant", pn.Column(reactive_chat.draw_view())),
        ("Math Mastery", math_mastery_interface.create_layout()),
    )
    
    # Create main layout
    return pn.Column(
        tabs,
        pn.Row(record_button),
        sizing_mode='stretch_width'
    )

def main():
    # Initialize global variables
    globals.input_future = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    progress_file_path = os.path.join(script_dir, '../../progress.json')

    # Initialize FSM and agents
    fsm = FSM(agents_dict)

    # Set up group chat
    groupchat = CustomGroupChat(
        agents=list(agents_dict.values()), 
        messages=[],
        max_round=globals.MAX_ROUNDS,
        send_introductions=True,
        speaker_selection_method=fsm.next_speaker_selector
    )

    # Set up chat manager
    manager = CustomGroupChatManager(
        groupchat=groupchat,
        filename=progress_file_path, 
        is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0
    )    

    # Initialize GUI components
    global reactive_chat
    reactive_chat = ReactiveChat(groupchat_manager=manager)

    # Initialize MathMasteryInterface
    global math_mastery_interface
    math_mastery_interface = MathMasteryInterface(agents_dict[AgentKeys.MASTERY.value])

    # Register groupchat_manager and reactive_chat GUI interface with ConversableAgents
    for agent in groupchat.agents:
        agent.groupchat_manager = manager
        agent.reactive_chat = reactive_chat
        agent.register_reply(
            [autogen.Agent, None],
            reply_func=agent.autogen_reply_func,
            config={"callback": None}
        )

    # Load chat history on startup
    manager.get_chat_history_and_initialize_chat(
        filename=progress_file_path,
        chat_interface=reactive_chat.learn_tab_interface
    )
    reactive_chat.update_dashboard()
    
    # Create and serve the application
    app = create_app()
    pn.serve(app, port=5006, show=True, callback_exception='verbose')

if __name__ == "__main__":
    main()

import param
import panel as pn
from src.crewAI.Crews.learningLanguageCrew import learn_language_manager_instance, language_avatars
from src.crewAI import globals
import threading
from src.crewAI import crewMemoryUtils
import os
import json
# from dotenv import load_dotenv
import time

# load_dotenv()

pn.extension(design="material")

class LanguageReactiveChat(param.Parameterized):
    def __init__(self, avatars=None, **params):
        super().__init__(**params)

        pn.extension(design="material")

        # Use avatars from learningLanguageCrew.py
        self.avatars = language_avatars

        self.LEARN_TAB_NAME = "LanguageLearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_language_learn_tab_callback, name=self.LEARN_TAB_NAME)
        
        # Dashboard components
        self.message_pane = pn.pane.Markdown(f"Total messages: {learn_language_manager_instance.messagesCount}")
        self.dashboard_view = pn.Column(self.message_pane)
        self.refresh_button = pn.widgets.Button(name="🔄 Refresh Dashboard", button_type="primary")
        self.refresh_button.on_click(self.on_refresh_button_click)
        
        # Progress tracking components
        self.progress_text = pn.pane.Markdown(f"**Language Learning Progress**")
        self.progress_bar = pn.widgets.Progress(name='Progress', value=0, max=10)
        self.progress_info = pn.pane.Markdown(f"0 out of 10")
        
        # Language selection components
        self.language_selector = pn.widgets.Select(
            name='Select Language',
            options=['Telugu', 'Spanish', 'French', 'German', 'Hindi', 'Chinese', 'Japanese', 'Korean'],
            value='Telugu'
        )
        self.language_selector.param.watch(self.on_language_change, 'value')
        
        # Learning statistics dashboard
        self.stats_pane = pn.pane.Markdown("**Learning Statistics**\n- Topics covered: 0\n- Questions answered: 0\n- Correct answers: 0\n- Current level: Beginner")
        self.stats_view = pn.Column(self.stats_pane)
        
        # Chat history management
        self.clear_history_button = pn.widgets.Button(name="🗑️ Clear Chat History", button_type="danger")
        self.clear_history_button.on_click(self.on_clear_history_click)
        
        # Export functionality
        self.export_button = pn.widgets.Button(name="📤 Export Progress", button_type="success")
        self.export_button.on_click(self.on_export_click)
        
        self.humanInput = None
        self.progress = 0
        self.max_questions = 10
        self.current_language = 'Telugu'

    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Learn Language", pn.Column(
                pn.Row(
                    pn.pane.Markdown("**Select your target language:**"),
                    self.language_selector
                ),
                pn.pane.Markdown("Start your language learning journey. Type anything to begin the learning process."),
                self.learn_tab_interface
            )),
            ("Dashboard", pn.Column(
                self.refresh_button,
                self.dashboard_view,
                pn.Spacer(height=20),
                self.stats_view
            )),
            ("Progress", pn.Column(
                self.progress_text,
                pn.Row(                        
                    self.progress_bar,
                    self.progress_info
                ),
                pn.Spacer(height=20),
                pn.Row(
                    self.clear_history_button,
                    self.export_button
                )
            ))
        )
        
        def on_tab_change(event):
            if event.new == 1:  # 1 is the Dashboard tab index
                self.update_dashboard()
                self.update_stats()

        tabs.param.watch(on_tab_change, 'active')
        return tabs
    
    def on_refresh_button_click(self, event):
        # Manually refresh dashboard and stats
        self.update_dashboard()
        self.update_stats()
    
    def on_language_change(self, event):
        """Handle language selection change"""
        self.current_language = event.new
        learn_language_manager_instance.language = self.current_language
        print(f"Language changed to: {self.current_language}")
        # Update the progress text to reflect the new language
        self.progress_text.object = f"**{self.current_language} Learning Progress**"
        
        # Clear the chat interface for the new language
        self.learn_tab_interface.clear()
        
        # Reset progress for new language
        self.progress = 0
        self.progress_bar.value = 0
        self.progress_info.object = f"0 out of {self.max_questions}"
        
        # Reset kickoff flag for new language session
        globals.kickoff_initiated = None
        
        # Update stats for new language
        self.update_stats()
    
    def on_clear_history_click(self, event):
        """Clear chat history and reset progress"""
        self.learn_tab_interface.clear()
        learn_language_manager_instance.messages = []
        learn_language_manager_instance.messagesCount = 0
        self.progress = 0
        self.progress_bar.value = 0
        self.progress_info.object = f"0 out of {self.max_questions}"
        self.update_dashboard()
        self.update_stats()
        print("Chat history and progress cleared")
    
    def on_export_click(self, event):
        """Export learning progress to JSON file"""
        export_data = {
            "language": self.current_language,
            "progress": self.progress,
            "max_questions": self.max_questions,
            "total_messages": learn_language_manager_instance.messagesCount,
            "messages": learn_language_manager_instance.messages,
            "timestamp": str(pn.state.curdoc.session_time) if pn.state.curdoc else "unknown"
        }
        
        filename = f"language_learning_progress_{self.current_language}_{int(time.time())}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"Progress exported to {filename}")
        except Exception as e:
            print(f"Error exporting progress: {e}")

    def update_dashboard(self):
        """Update the dashboard with current message count"""
        print("=============Updating Language dashboard messages count=============", learn_language_manager_instance.messagesCount)
        self.message_pane.object = f"Total messages: {learn_language_manager_instance.messagesCount}"

    def update_stats(self):
        """Update learning statistics"""
        # Calculate statistics from messages
        total_messages = learn_language_manager_instance.messagesCount
        topics_covered = len([msg for msg in learn_language_manager_instance.messages if "Topic:" in str(msg.get('content', ''))])
        questions_answered = len([msg for msg in learn_language_manager_instance.messages if "Final_Evaluation:" in str(msg.get('content', ''))])
        correct_answers = len([msg for msg in learn_language_manager_instance.messages if "Final_Evaluation: Correct" in str(msg.get('content', ''))])
        
        # Determine current level based on progress
        if self.progress < 3:
            current_level = "Beginner"
        elif self.progress < 7:
            current_level = "Intermediate"
        else:
            current_level = "Advanced"
        
        stats_text = f"""**Learning Statistics for {self.current_language}**
- Topics covered: {topics_covered}
- Questions answered: {questions_answered}
- Correct answers: {correct_answers}
- Current level: {current_level}
- Total interactions: {total_messages}"""
        
        self.stats_pane.object = stats_text

    def a_language_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        print(f"User: {user} said: {contents}")
        
        if not globals.kickoff_initiated:
            globals.kickoff_initiated = True
            # Start the language learning crew in a separate thread
            threading.Thread(target=learn_language_manager_instance.kickoff).start()
        else:
            print("Input was set to the future.", globals.input_future)
            if globals.input_future is None:                
                globals.input_future = contents
                print("Input was set to the future.")
            else:
                print("No input being awaited.")

    def update_progress(self):
        """Update progress based on correct answers"""
        print("################ CORRECT ANSWER #################")
        if self.progress < self.max_questions:  
            self.progress += 1
            self.progress_bar.value = self.progress
            self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"
            self.update_stats()

# Create the Language reactive chat instance
language_reactive_chat = LanguageReactiveChat()

# Attach the reactive chat to the Language learning manager
learn_language_manager_instance.attach_reactive_chat(language_reactive_chat)

# Create the main app
app = language_reactive_chat.draw_view()

def run_language_panel():
    """Run the language learning panel application"""
    pn.serve(app, callback_exception='verbose')

if __name__ == "__main__":    
    run_language_panel() 
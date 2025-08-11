import param
import panel as pn
from src.crewAI.Crews.learningCareerPathInterestCrew import learn_career_path_interest_manager_instance, career_path_interest_avatars
from src.crewAI import globals
import threading
from src.crewAI import crewMemoryUtils

pn.extension(design="material")

class CareerPathInterestReactiveChat(param.Parameterized):
    def __init__(self, avatars=None, **params):
        super().__init__(**params)

        pn.extension(design="material")

        # Use avatars from learningCareerPathInterestCrew.py
        self.avatars = career_path_interest_avatars

        self.LEARN_TAB_NAME = "CareerPathInterestLearnTab"
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_career_path_interest_learn_tab_callback, name=self.LEARN_TAB_NAME)
        self.message_pane = pn.pane.Markdown(f"Total messages: {learn_career_path_interest_manager_instance.messagesCount}")
        self.dashboard_view = pn.Column(self.message_pane)
        self.refresh_button = pn.widgets.Button(name="🔄 Refresh Dashboard", button_type="primary")
        self.refresh_button.on_click(self.on_refresh_button_click)
        
        # Career-specific progress tracking
        self.progress_text = pn.pane.Markdown(f"**Career Path Interest Assessment Progress**")
        self.progress_bar = pn.widgets.Progress(name='Progress', value=0, max=11)  # 11 tasks in the workflow
        self.progress_info = pn.pane.Markdown(f"0 out of 11")
        
        # Career assessment specific widgets
        self.career_insights_pane = pn.pane.Markdown("**Career Insights:** No assessment completed yet.")
        self.recommendations_pane = pn.pane.Markdown("**Career Recommendations:** Complete the assessment to see recommendations.")
        self.skills_pane = pn.pane.Markdown("**Skills Analysis:** Skills will be analyzed during assessment.")
        
        self.humanInput = None

    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Career Assessment", pn.Column(
                "Welcome to your Career Path Interest Assessment! 🎯",
                "This comprehensive assessment will help you discover career paths that align with your interests, skills, and values.",
                "Type anything to begin your career exploration journey.",
                self.learn_tab_interface
            )),
            ("Dashboard", pn.Column(
                self.refresh_button, 
                self.dashboard_view,
                self.career_insights_pane,
                self.recommendations_pane,
                self.skills_pane
            )),
            ("Progress", pn.Column(
                self.progress_text,
                pn.Row(                        
                    self.progress_bar,
                    self.progress_info
                ),
                pn.pane.Markdown("""
                **Assessment Stages:**
                1. 📝 Survey Generation
                2. 🔍 Interest Exploration  
                3. 📊 Data Collection
                4. 📈 Trend Analysis
                5. 🎯 Career Matching
                6. 🧠 Competency Analysis
                7. 🛠️ Plan Generation
                8. 🎨 Visualization
                9. 📚 Profile Update
                10. 📋 Summary Presentation
                """)
            ))
        )
        
        def on_tab_change(event):
            if event.new == 1:  # 1 is the Dashboard tab index
                self.update_dashboard()

        tabs.param.watch(on_tab_change, 'active')
        return tabs
    
    def on_refresh_button_click(self, event):
        # Manually refresh dashboard (same logic as on tab switch)
        self.update_dashboard()
    
    def update_dashboard(self):
        print("=============Updating Career Path Interest dashboard messages count=============", learn_career_path_interest_manager_instance.messagesCount)
        self.message_pane.object = f"Total messages: {learn_career_path_interest_manager_instance.messagesCount}"
        
        # Update career-specific insights based on current progress
        self.update_career_insights()

    def update_career_insights(self):
        """Update career-specific insights based on assessment progress"""
        current_task = learn_career_path_interest_manager_instance.currentTask
        messages = learn_career_path_interest_manager_instance.messages
        
        if not current_task:
            self.career_insights_pane.object = "**Career Insights:** Assessment not started yet."
            self.recommendations_pane.object = "**Career Recommendations:** Complete the assessment to see recommendations."
            self.skills_pane.object = "**Skills Analysis:** Skills will be analyzed during assessment."
            return
        
        # Update insights based on current task
        if "Survey" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Gathering your interests and preferences..."
        elif "Questioning" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Exploring your career interests in depth..."
        elif "Data" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Collecting career market data..."
        elif "Analysis" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Analyzing career trends and opportunities..."
        elif "Matching" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Matching your interests to career paths..."
        elif "Competency" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Analyzing required skills and competencies..."
        elif "Plan" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Generating your personalized career development plan..."
        elif "Visualization" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Creating visual representations of your career analysis..."
        elif "Summary" in current_task:
            self.career_insights_pane.object = "**Career Insights:** Preparing your comprehensive career assessment summary..."
        
        # Extract recommendations from messages if available
        recommendations = self.extract_recommendations_from_messages(messages)
        if recommendations:
            self.recommendations_pane.object = f"**Career Recommendations:** {recommendations}"
        
        # Extract skills analysis from messages if available
        skills_analysis = self.extract_skills_from_messages(messages)
        if skills_analysis:
            self.skills_pane.object = f"**Skills Analysis:** {skills_analysis}"

    def extract_recommendations_from_messages(self, messages):
        """Extract career recommendations from message history"""
        for message in reversed(messages):
            content = message.get('content', '').lower()
            if any(keyword in content for keyword in ['recommend', 'career path', 'suitable', 'match']):
                # Return a summary of the recommendation
                return "Career recommendations have been identified based on your interests and preferences."
        return None

    def extract_skills_from_messages(self, messages):
        """Extract skills analysis from message history"""
        for message in reversed(messages):
            content = message.get('content', '').lower()
            if any(keyword in content for keyword in ['skill', 'competency', 'ability', 'requirement']):
                # Return a summary of the skills analysis
                return "Skills and competencies have been analyzed for your career interests."
        return None

    def a_career_path_interest_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        print(f"User: {user} said: {contents}")
        
        if not globals.kickoff_initiated:
            globals.kickoff_initiated = True
            # Start the career assessment workflow
            threading.Thread(target=learn_career_path_interest_manager_instance.kickoff).start()
        else:
            print("Input was set to the future.", globals.input_future)
            if globals.input_future is None:                
                globals.input_future = contents
                print("Input was set to the future.")
            else:
                print("No input being awaited.")

    def update_progress(self):
        """Update progress based on completed tasks"""
        # Calculate progress based on completed tasks
        completed_tasks = 0
        current_task = learn_career_path_interest_manager_instance.currentTask
        
        # Define task progression
        task_progression = [
            "Initiate Career Interest Survey",
            "Generate Career Interest Survey", 
            "Conduct Adaptive Career Questioning",
            "Retrieve Career Market Data",
            "Analyze Career Trends and Performance",
            "Match Interests to Career Paths",
            "Extract Required Competencies",
            "Generate Career Development Plan",
            "Create Career Visualization",
            "Update Career Learning Profile",
            "Present Career Path Summary"
        ]
        
        # Count completed tasks
        for task in task_progression:
            if task == current_task:
                break
            completed_tasks += 1
        
        # Update progress bar
        self.progress_bar.value = completed_tasks
        self.progress_info.object = f"**{completed_tasks} out of 11**"
        
        # Update insights
        self.update_career_insights()

# Create the Career Path Interest reactive chat instance
career_path_interest_reactive_chat = CareerPathInterestReactiveChat()

# Attach the reactive chat to the Career Path Interest learning manager
learn_career_path_interest_manager_instance.attach_reactive_chat(career_path_interest_reactive_chat)

# Create the main app
app = career_path_interest_reactive_chat.draw_view()

def run_career_path_interest_panel():
    """Launch the Career Path Interest assessment panel"""
    pn.serve(app, callback_exception='verbose')

if __name__ == "__main__":    
    run_career_path_interest_panel() 
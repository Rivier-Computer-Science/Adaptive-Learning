import param
import panel as pn
from src.crewAI.Crews.learningCrew import learn_math_manager_instance
# import asyncio
from src.crewAI import globals
import threading
from src.crewAI import crewMemoryUtils

pn.extension(design="material")
class ReactiveChat(param.Parameterized):
    def __init__(self,  avatars=None, **params):
        super().__init__(**params)

        pn.extension(design="material")

        # self.agents_dict = agents_dict
        self.avatars = avatars

        self.LEARN_TAB_NAME = "LearnTab"
        # self.messagesCount = 0
        self.learn_tab_interface = pn.chat.ChatInterface(callback=self.a_learn_tab_callback, name=self.LEARN_TAB_NAME)
        self.message_pane = pn.pane.Markdown(f"Total messages: {learn_math_manager_instance.messagesCount}")
        self.dashboard_view = pn.Column(self.message_pane)
        self.refresh_button = pn.widgets.Button(name="🔄 Refresh Dashboard", button_type="primary")
        self.refresh_button.on_click(self.on_refresh_button_click)
        self.progress_text = pn.pane.Markdown(f"**Student Progress**")
        self.progress_bar = pn.widgets.Progress(name='Progress', value=0, max=10)
        self.progress_info = pn.pane.Markdown(f"0 out of 10")
        self.humanInput = None

    
    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Learn", pn.Column("Learn Maths Here. Type anything to start the learning process.", self.learn_tab_interface)
                    ),
            ("Dashboard", pn.Column(self.refresh_button, self.dashboard_view)
                    ),
            ("Progress", pn.Column(
                self.progress_text,
                pn.Row(                        
                    self.progress_bar,
                    self.progress_info))
                    )
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
        print("=============Updating dashboard messages count=============", learn_math_manager_instance.messagesCount)
        self.message_pane.object = f"Total messages: {learn_math_manager_instance.messagesCount}"

    def a_learn_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        print(f"User: {user} said: {contents}")
        # global globals.kickoff_initiated
        if not globals.kickoff_initiated:
            globals.kickoff_initiated = True
            threading.Thread(target=learn_math_manager_instance.kickoff).start()
        else:
            print("Input was set to the future.", globals.input_future)
            if globals.input_future is None:                
                globals.input_future = contents
                print("Input was set to the future.")
            else:
                print("No input being awaited.")

    def update_progress(self):
        # Parse the agent's output for keywords                 
        print("################ CORRECT ANSWER #################")
        if self.progress < self.max_questions:  
            self.progress += 1
            self.progress_bar.value = self.progress
            self.progress_info.object = f"**{self.progress} out of {self.max_questions}**"

            # WRONG ANSWER #################")




reactive_chat = ReactiveChat()

learn_math_manager_instance.attach_reactive_chat(reactive_chat)


app = reactive_chat.draw_view()

def run_panel():
    pn.serve(app, callback_exception='verbose')

# run_panel()

if __name__ == "__main__":    
    run_panel()

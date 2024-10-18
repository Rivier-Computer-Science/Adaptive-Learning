import panel as pn

class UserInterface:
    def __init__(self):
        self.mastery_status = pn.pane.Markdown("Current Mastery Status: Not Started")
        self.current_topic = pn.pane.Markdown("Current Topic: None")
        self.progress_bar = pn.widgets.Progress(name="Overall Progress", value=0, width=400)

    def update_mastery_status(self, status):
        self.mastery_status.object = f"Current Mastery Status: {status}"

    def update_current_topic(self, topic):
        self.current_topic.object = f"Current Topic: {topic}"

    def update_progress(self, progress):
        self.progress_bar.value = progress

    def draw_view(self):
        return pn.Column(
            self.mastery_status,
            self.current_topic,
            self.progress_bar
        )

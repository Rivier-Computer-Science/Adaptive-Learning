from .conversable_agent import MyConversableAgent

class StudentCareerDashboardAgent(MyConversableAgent):
    """
    Tracks student career progress dynamically.
    """

    system_message = """
    You are StudentCareerDashboardAgent, responsible for tracking student progress.
    Your task is to provide real-time updates on completed milestones, upcoming certifications,
    and suggest improvements.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="StudentCareerDashboardAgent",
            system_message=kwargs.pop("system_message", self.system_message),
            description="Tracks and updates student career progress.",
            human_input_mode="NEVER",
            **kwargs
        )
        self.progress_data = {}

    def update_progress(self, student, career, step_completed):
        """
        Dynamically update student career progress.
        """
        if student not in self.progress_data:
            self.progress_data[student] = {career: []}
        if career not in self.progress_data[student]:
            self.progress_data[student][career] = []
        
        self.progress_data[student][career].append(step_completed)
        return f"Updated {student}'s progress for {career}: {self.progress_data[student][career]}"

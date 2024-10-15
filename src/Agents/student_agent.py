###################### Student ########################
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .conversable_agent import MyConversableAgent

class Goal:
    def __init__(self, name: str, description: str, target_date: datetime, priority: str, category: str):
        self.name = name
        self.description = description
        self.target_date = target_date
        self.completed_sessions = 0
        self.total_sessions = 0
        self.priority = priority
        self.category = category

    def update_progress(self, completed_sessions: int):
        self.completed_sessions += completed_sessions

    def completion_percentage(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return (self.completed_sessions / self.total_sessions) * 100

class StudySession:
    def __init__(self, start_time: datetime, end_time: datetime, goal: Optional[Goal] = None):
        self.start_time = start_time
        self.end_time = end_time
        self.goal = goal

class StudentAgent(MyConversableAgent):
    description = """ 
            StudentAgent is a reliable system proxy designed to facilitate communication and interaction between a human user and the educational system. 
            StudentAgent serves as an intermediary, efficiently relaying requests and responses to ensure smooth and effective academic support. 
            """
    
    system_message = """
            You are StudentAgent, a system proxy for a human user. 
            Your primary role is to facilitate communication between the human and the educational system. 
            When the human provides input or requests information, you will relay these to the appropriate agent. 
            Maintain clarity and accuracy in all communications to enhance the human's learning experience
            """

    def __init__(self, tutor_agent=None, knowledge_tracer_agent=None, **kwargs):
        super().__init__(
            name="StudentAgent",
            human_input_mode="ALWAYS",
            system_message=kwargs.pop('system_message', self.system_message),
            description=kwargs.pop('description',self.description),
            **kwargs
        )
        self.goals: Dict[str, Goal] = {}
        self.study_sessions: List[StudySession] = []
        self.tutor_agent = tutor_agent
        self.knowledge_tracer_agent = knowledge_tracer_agent

    def add_goal(self, name: str, description: str, target_date: datetime, priority: str, category: str):
        if name in self.goals:
            raise ValueError("Goal with this name already exists.")
        self.goals[name] = Goal(name, description, target_date, priority, category)

    def update_goal(self, name: str, completed_sessions: int):
        if name not in self.goals:
            raise ValueError("Goal not found.")
        self.goals[name].update_progress(completed_sessions)

    def schedule_study_session(self, start_time: datetime, end_time: datetime, goal_name: Optional[str] = None):
        goal = self.goals.get(goal_name) if goal_name else None
        session = StudySession(start_time, end_time, goal)
        self.study_sessions.append(session)
        if goal:
            goal.total_sessions += 1

    def get_goal_progress(self, name: str) -> Dict[str, float]:
        if name not in self.goals:
            raise ValueError("Goal not found.")
        goal = self.goals[name]
        return {
            "name": goal.name,
            "description": goal.description,
            "completion_percentage": goal.completion_percentage()
        }

    def get_upcoming_sessions(self) -> List[StudySession]:
        now = datetime.now()
        return [session for session in self.study_sessions if session.start_time > now]

    def interact_with_agents(self):
        for goal in self.goals.values():
            progress_info = self.get_goal_progress(goal.name)
            # Request recommendations from Tutor Agent
            tutor_recommendations = self.tutor_agent.request_recommendations(
                goal_name=goal.name,
                completion_percentage=progress_info['completion_percentage']
            )
            # Request insights from Knowledge Tracer Agent
            knowledge_insights = self.knowledge_tracer_agent.request_insights(
                goal_name=goal.name,
                completion_percentage=progress_info['completion_percentage']
            )
            # Process and handle the recommendations and insights
            self.handle_recommendations_and_insights(tutor_recommendations, knowledge_insights)

    def handle_recommendations_and_insights(self, tutor_recommendations, knowledge_insights):
        # Logic to process and incorporate recommendations and insights
        print("Tutor Recommendations:", tutor_recommendations)
        print("Knowledge Tracer Insights:", knowledge_insights)
        
        # Example logic to update goals and reschedule sessions
        for recommendation in tutor_recommendations:
            if recommendation['recommendation'] == "Consider exploring advanced topics or additional practice problems.":
                print("Recommendation to explore advanced topics.")
                # Example: Add a new goal or adjust current goals based on recommendation
                # self.add_goal(name="Advanced Topics", description="Explore advanced topics", target_date=datetime.now() + timedelta(days=30))

        for insight in knowledge_insights:
            if insight['adjustment'] == "Consider reducing focus on this topic and increase focus on more challenging areas.":
                print("Adjusting focus to more challenging areas.")
                # Example: Reschedule sessions or update goal priorities
                # self.schedule_study_session(start_time=datetime.now() + timedelta(days=1), end_time=datetime.now() + timedelta(days=2), goal_name="Challenging Topics")

            elif insight['adjustment'] == "Increase focus on this topic and consider additional practice sessions.":
                print("Increasing focus on this topic.")
                # Example: Add additional study sessions for the topic
                # self.schedule_study_session(start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=1), goal_name="Current Goal")

    # Calendar View
    def get_calendar_view(self, view_type: str) -> Dict[str, List[StudySession]]:
        """
        Returns a calendar view based on the specified view_type.
        Supported view_types: 'daily', 'weekly', 'monthly'
        """
        now = datetime.now()
        calendar_view = {"sessions": []}
        if view_type == 'daily':
            calendar_view['sessions'] = [session for session in self.study_sessions if session.start_time.date() == now.date()]
        elif view_type == 'weekly':
            start_of_week = now - timedelta(days=now.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            calendar_view['sessions'] = [session for session in self.study_sessions if start_of_week.date() <= session.start_time.date() <= end_of_week.date()]
        elif view_type == 'monthly':
            start_of_month = now.replace(day=1)
            end_of_month = (start_of_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            calendar_view['sessions'] = [session for session in self.study_sessions if start_of_month.date() <= session.start_time.date() <= end_of_month.date()]
        return calendar_view

    # Goal Setting Interface
    def set_goal_interface(self):
        """
        Provides a user-friendly interface for setting and managing goals.
        """
        for goal_name, goal in self.goals.items():
            print(f"Goal: {goal_name}")
            print(f"Description: {goal.description}")
            print(f"Target Date: {goal.target_date}")
            print(f"Priority: {goal.priority}")
            print(f"Category: {goal.category}")
            print("------")

    # Progress Display
    def display_progress(self):
        """
        Displays progress using visual elements like progress bars and badges.
        """
        for goal_name, goal in self.goals.items():
            progress_percentage = goal.completion_percentage()
            print(f"Goal: {goal_name}")
            print(f"Progress: [{'#' * int(progress_percentage // 10)}{'-' * (10 - int(progress_percentage // 10))}] {progress_percentage:.2f}%")
            if progress_percentage >= 100:
                print("Achievement Badge: Goal Completed!")
            print("------")

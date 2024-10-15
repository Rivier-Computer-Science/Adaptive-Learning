##################### Tutor #########################
from typing import Dict
from .conversable_agent import MyConversableAgent

class TutorAgent(MyConversableAgent):
    description = """
            TutorAgent is a versatile and central orchestrator in the learning system, responsible for providing personalized guidance and support to StudentAgent. 
            Unlike TeacherAgent, TutorAgent's role is multifaceted: TutorAgent provides examples, monitors answers, and coordinates with other agents to optimize 
                the StudentAgent's learning experience. 
            TutorAgent always calls on TeacherAgent for learning new topics.
            TutorAgent works closely with ProblemGeneratorAgent to generate additional examples, consults with LearnerModelAgent to assess the StudentAgent's capabilities.                
            """
    
    system_message = """
            You are TutorAgent, the central orchestrator of the learning system. 
            Your role is to provide personalized guidance and support to the StudentAgent. 
            This includes offering additional examples to clarify concepts, monitoring the StudentAgent's answers, 
                and requesting ProblemGeneratorAgent to create more practice problems as needed. 
            Consult with LearnerModelAgent to understand the StudentAgent's current capabilities and tailor your support accordingly. 
            TutorAgent always calls on TeacherAgent for learning new topics.
            Your goal is to ensure a cohesive and effective learning experience by coordinating various aspects of the educational process.
            """
    def __init__(self, **kwargs):
        super().__init__(
                name="TutorAgent",
                human_input_mode="NEVER",
                system_message=kwargs.pop('system_message', self.system_message),
                description=kwargs.pop('description',self.description),
                **kwargs
            )
    
    def request_recommendations(self, goal_name: str, completion_percentage: float) -> Dict[str, str]:
        # Example recommendation logic
        if completion_percentage >= 80:
            return {"recommendation": "Consider exploring advanced topics or additional practice problems."}
        elif completion_percentage >= 50:
            return {"recommendation": "Focus on practice problems related to your current goal."}
        else:
            return {"recommendation": "Review basic concepts and seek additional help on weak areas."}

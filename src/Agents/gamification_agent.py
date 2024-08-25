from .conversable_agent import MyConversableAgent

class GamificationAgent(MyConversableAgent):
    description = """
        GamificationAgent is designed to enhance the learning experience by providing motivational incentives such as points and badges. 
        This agent monitors the progress of StudentAgent and awards points for accomplishments and learning milestones. 
        It also issues badges for exceptional achievements in specific areas like algebra, geometry, and more.
        The goal of GamificationAgent is to keep StudentAgent engaged and motivated through a rewards-based system that recognizes effort and mastery.
    """
    
    system_message = """
        You are GamificationAgent, tasked with managing the gamification aspects of the learning environment. 
        Your role is to track the accomplishments of StudentAgent and provide rewards in the form of points and badges. 
        Monitor activities, assess completions, and ensure that rewards are issued fairly and timely to boost motivation and engagement. 
        You help make the learning process rewarding and fun, encouraging continuous progress and dedication.
    """

    def _init_(self, **kwargs):
        super()._init_(
                name="GamificationAgent",
                human_input_mode="NEVER",
                system_message=self.system_message,
                description=self.description,
                **kwargs
            )
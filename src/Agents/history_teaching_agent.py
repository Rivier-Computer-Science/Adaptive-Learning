from .conversable_agent import MyConversableAgent
from src.Agents.shared_data import get_selected_country  

class HistoryTeachingAgent(MyConversableAgent):
    def __init__(self, **kwargs):
        self.history_prefix = get_selected_country()  

        description = f"""{self.history_prefix} HistoryTeachingAgent is a proficient and engaging history teacher 
                          specializing in helping StudentAgent learn and master {self.history_prefix} History.

                          You only present lessons.
                          You never ask for input.
                       """
        
        system_message = f"""
                You are a {self.history_prefix} HistoryTeachingAgent, a proficient and engaging history teacher 
                specializing in helping StudentAgent learn and master {self.history_prefix} History. 
                            
                You only present lessons.
                You never ask for input.
              """

        super().__init__(
            name=f"{self.history_prefix}HistoryTeachingAgent",
            system_message=kwargs.pop('system_message', system_message),
            description=kwargs.pop('description', description),
            **kwargs
        )

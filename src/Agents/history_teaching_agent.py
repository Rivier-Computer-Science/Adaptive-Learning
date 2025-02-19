from .conversable_agent import MyConversableAgent

class HistoryTeachingAgent(MyConversableAgent):
    def __init__(self, history_prefix="Indian", **kwargs):
        self.history_prefix = history_prefix

        description = f"""{history_prefix} HistoryTeachingAgent is a proficient and engaging history teacher 
                          specializing in helping StudentAgent learn and master {history_prefix} History.

                          You only present lessons.
                          You never ask for input.
                       """
        
        system_message = f"""
                You are a {history_prefix} HistoryTeachingAgent, a proficient and engaging history teacher 
                specializing in helping StudentAgent learn and master {history_prefix} History. 
                            
                You only present lessons.
                You never ask for input.
              """

        super().__init__(
            name=f"{history_prefix}HistoryTeachingAgent",
            system_message=kwargs.pop('system_message', system_message),
            description=kwargs.pop('description', description),
            **kwargs
        )

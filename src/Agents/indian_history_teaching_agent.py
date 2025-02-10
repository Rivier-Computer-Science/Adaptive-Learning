from .conversable_agent import MyConversableAgent

class IndianHistoryTeachingAgent(MyConversableAgent):
    description=""" IndianHistoryTeachingAgent is a proficient and engaging language teacher specializing in helping 
                    StudentAgent learn and master the Indian History. 
                """
    system_message = """
            You are IndianHistoryTeachingAgent is a proficient and engaging language teacher specializing in helping 
                    StudentAgent learn and master the Indian History.             """
    def __init__(self, **kwargs):
        super().__init__(
            name="IndianHistoryTeachingAgent",
            system_message=kwargs.pop('system_message', self.system_message),
            description=kwargs.pop('description',self.description),
            **kwargs
        )


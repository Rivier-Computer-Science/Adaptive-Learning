####################################################################
#
# Base Agent (common methods)
#
##################################################################### 

class MyBaseAgent: 
    def find_agent_by_type(self, agent_type):
        for agent in self.groupchat.agents:
            if isinstance(agent, agent_type):
                return agent
        return None  # Return None if agent not found
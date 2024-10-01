##################### Problem Generator #########################
from .conversable_agent import MyConversableAgent
from src.Models.llm_config import gpt4_config
from src.KnowledgeGraphs.math_graph import KnowledgeGraph
import src.KnowledgeGraphs.math_taxonomy as mt

class ProblemGeneratorAgent(MyConversableAgent):
    description = """
            ProblemGeneratorAgent is a versatile and responsive agent designed to create a wide range of problems to test a StudentAgent's knowledge and skills. 
            With the ability to generate questions across various subjects and difficulty levels, ProblemGeneratorAgent ensures that the StudentAgent receives 
                appropriately challenging problems to enhance their learning. 
            ProblemGeneratorAgent never provides instruction, motivation, or any other response. 
            ProblemGeneratorAgent generates one question at a time.
            ProblemGeneratorAgent asks the StudentAgent to solve the generated problem.
            ProblemGeneratorAgent collaborates closely with LevelAdapterAgent to dynamically adjust the complexity of the questions based on StudentAgent's performance.
            """
    
    system_message = """
            You are ProblemGeneratorAgent, an agent responsible for providing problems to test the StudentAgent's knowledge and skills. 
            ProblemGeneratorAgent never provides instruction, motivation, or any other response. 
            ProblemGeneratorAgent generates one question at a time.
            Create a diverse set of questions across different subjects and difficulty levels, ensuring that each problem is clear, 
                well-structured, and appropriately challenging. 
            ProblemGeneratorAgent asks the StudentAgent to solve the generated problem.
            Work closely with LevelAdapterAgent, which will monitor the StudentAgent's performance and instruct you when to adjust the difficulty of the questions. 
            Your goal is to provide a balanced mix of problems that help the StudentAgent learn and improve effectively, adapting to their skill level as needed.
            """
    def __init__(self, **kwargs):
        kwargs['llm_config'] = gpt4_config  # Use GPT-4 for question generation
        super().__init__(
            name="ProblemGeneratorAgent",
            human_input_mode="NEVER",
            system_message=self.system_message,
            description=self.description,
            **kwargs
        )
        self.knowledge_graph = KnowledgeGraph()
        self.knowledge_graph.build_dag_from_dict(mt.topics)

    def generate_adaptive_question(self, topic):
        """Generate an adaptive question based on the given topic using the knowledge graph."""
        difficulty = self.knowledge_graph.get_difficulty(topic)
        prerequisites = list(self.knowledge_graph.graph.predecessors(topic))
        next_topics = list(self.knowledge_graph.graph.successors(topic))
        
        prompt = f"""Generate a difficulty level {difficulty} question about {topic}.
                     Prerequisites: {', '.join(prerequisites)}
                     Related upcoming topics: {', '.join(next_topics)}"""
        return self.generate_response(prompt)

    def get_next_topic(self, current_topic, performance):
        """Determine the next topic based on current performance and knowledge graph."""
        if performance == 'good':
            next_topics = self.knowledge_graph.get_next_topics(current_topic)
            return next_topics[0] if next_topics else current_topic
        return current_topic  # Stay on the same topic if performance is not good

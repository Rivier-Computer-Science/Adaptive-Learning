##################### Learner Model #########################
from .conversable_agent import MyConversableAgent
from src.KnowledgeGraphs.math_graph import KnowledgeGraph
from src.KnowledgeGraphs.math_taxonomy import subsubsub_topics as mt_topics
class LearnerModelAgent(MyConversableAgent):
    description = """
            LearnerModelAgent is an insightful and adaptive agent designed to monitor and assess the current capabilities of the StudentAgent. 
            By listening to the StudentAgent's answers and updating its internal model, LearnerModelAgent provides a comprehensive understanding of the StudentAgent's 
                knowledge and skill level. 
            When consulted by other agents such as ProblemGeneratorAgent, LearnerModelAgent offers guidelines on the type and difficulty of math questions 
                that should be generated to match the StudentAgent's proficiency.                     
            """
    
    system_message = """
            You are LearnerModelAgent, an agent responsible for assessing and understanding the current capabilities of the StudentAgent. 
            Your primary task is to listen to the StudentAgent's answers and continuously update your internal model to reflect their knowledge and skill level. 
            When other agents, such as ProblemGeneratorAgent, request information, you provide detailed guidelines on the type and difficulty of math questions that 
                should be generated based on your assessment. 
            Your goal is to ensure that the StudentAgent's learning experience is tailored to their current abilities, promoting effective and personalized learning.
            """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="LearnerModelAgent",            
            system_message=self.system_message,
            description=self.description,
            code_execution_config=False,
            human_input_mode="NEVER",
            **kwargs
        )
        self.learner_model = {}
        self.knowledge_graph = KnowledgeGraph()
        self.knowledge_graph.build_dag_from_dict(mt_topics)

    def update_model(self, topic, performance):
        """Update the learner model based on the student's performance on a topic."""
        if topic not in self.learner_model:
            self.learner_model[topic] = {'correct': 0, 'total': 0}
        
        self.learner_model[topic]['total'] += 1
        if performance == 'correct':
            self.learner_model[topic]['correct'] += 1

    def get_recommended_topic(self):
        """Determine the recommended topic based on the learner model and knowledge graph."""
        for topic in self.knowledge_graph.graph.nodes:
            if topic not in self.learner_model or self.learner_model[topic]['correct'] / self.learner_model[topic]['total'] < 0.7:
                return topic
        return self.knowledge_graph.find_first_node()  # If all topics are mastered, start over

    def provide_feedback(self, topic, answer):
        """Analyze the student's answer and provide feedback on their performance."""
        prompt = f"Analyze the following answer to a question about {topic} and provide feedback: {answer}"
        feedback = self.generate_response(prompt)
        
        performance = 'correct' if 'correct' in feedback.lower() else 'incorrect'
        self.update_model(topic, performance)
        
        return feedback

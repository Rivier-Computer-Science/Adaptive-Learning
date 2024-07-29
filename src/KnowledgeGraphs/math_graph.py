import networkx as nx
import matplotlib.pyplot as plt
import os
import math
import math_taxonomy as mt
import scipy


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph to represent progression

    def add_topic(self, topic_name, difficulty):
        self.graph.add_node(topic_name, difficulty=difficulty)

    def add_prerequisite(self, topic_from, topic_to):
        """Add a directed edge indicating that topic_from is a prerequisite for topic_to"""
        self.graph.add_edge(topic_from, topic_to)

    def get_next_topics(self, current_topic):
        """Returns topics that directly follow the current topic"""
        return list(self.graph.successors(current_topic))

    def get_difficulty(self, topic_name):
        """Get the difficulty level of a topic"""
        return self.graph.nodes[topic_name]['difficulty']
    
    def build_dag_from_dict(self, topics_dict):
        self.graph = nx.DiGraph()

        # Previous node variable to keep track of the last node added
        # This will help in linking the sequential nodes across different keys
        prev_node = None
        difficulty_level = 1

        for _, children in topics_dict.items():
            for child in children:
                # Add each child as a node. networkx won't duplicate nodes.
                self.graph.add_node(child, difficulty=difficulty_level)
                difficulty_level += 1
                
                # If there's a previous node, draw an edge from it to the current child
                if prev_node is not None:
                    self.graph.add_edge(prev_node, child)
                
                # Update the previous node to be the current child for the next iteration
                prev_node = child
        return

    def plot_dag(self):
        nx.draw(self.graph, with_labels=True)
        plt.show()

    def find_first_node(self):
        # Find and return the first node with no incoming edges.
        for node in self.graph.nodes:
            if self.graph.in_degree(node) == 0:
                return node  # first node
        return None  # in case no such node exists

def main():
    kt = KnowledgeGraph()
    kt.plot_dag()


if __name__ == '__main__':
    main()



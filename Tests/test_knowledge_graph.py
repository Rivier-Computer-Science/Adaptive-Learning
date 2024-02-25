import unittest
import sys
import os

# Add the parent directory to sys.path to find your_module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from math_graph import KnowledgeGraph  # Make sure to replace 'your_module' with the actual name of your Python file

class TestKnowledgeGraph(unittest.TestCase):

    def test_build_dag_from_dict(self):
        # Example topics dictionary to build the graph
        topics_dict = {
            "Topic1": ["Subtopic1", "Subtopic2"],
            "Topic2": ["Subtopic2", "Subtopic3"],
        }

        # Create an instance of KnowledgeGraph and build the graph
        kg = KnowledgeGraph()
        kg.build_dag_from_dict(topics_dict)

        # Test if the graph has the correct number of nodes
        self.assertEqual(len(kg.graph.nodes), 3)

        # Test if specific nodes are in the graph
        self.assertIn("Subtopic1", kg.graph.nodes)
        self.assertIn("Subtopic2", kg.graph.nodes)
        self.assertIn("Subtopic3", kg.graph.nodes)

        # Test if the graph has the correct number of edges
        self.assertEqual(len(kg.graph.edges), 3)

        # Test the structure of edges (assuming sequential linkage based on list order)
        expected_edges = [("Subtopic1", "Subtopic2"), ("Subtopic2", "Subtopic3")]
        for edge in expected_edges:
            self.assertIn(edge, kg.graph.edges)

if __name__ == '__main__':
    unittest.main()

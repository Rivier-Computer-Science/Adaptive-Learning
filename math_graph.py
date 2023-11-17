import networkx as nx
import matplotlib.pyplot as plt


# Create a directed graph
G = nx.DiGraph()

# Add top-level nodes
topics = ["Arithmetic", "Algebra", "Geometry", "Trigonometry", "Statistics and Probability", 
          "Pre-Calculus", "Calculus", "Advanced Calculus (Honors)", "Discrete Mathematics (Honors)", 
          "Linear Algebra (Honors)", "Advanced Statistics (Honors)", "Mathematical Proofs and Theory (Honors)"]
G.add_node("Math", color='blue')  # Assuming 'blue' denotes the start
for topic in topics:
    G.add_node(topic, color='blue')  # Change colors as needed
    G.add_edge("Math", topic)  # Undirected edge from Math to topic

# Add subtopics and sub-subtopics for Arithmetic as an example
arithmetic_subtopics = {
    "Basic operations": ["Addition", "Subtraction", "Multiplication", "Division", "Order of operations (PEMDAS)"],
    "Fractions": ["Simplifying", "Comparing", "Addition", "Subtraction", "Multiplication", "Division"],
    # ... add other subtopics and their respective sub-subtopics
}

for subtopic, operations in arithmetic_subtopics.items():
    G.add_node(subtopic, color='green')  # Change colors as needed
    prev_operation = subtopic  # Start from the subtopic
    for operation in operations:
        G.add_node(operation, color='green')  # Change colors as needed
        G.add_edge(prev_operation, operation, directed=True)
        prev_operation = operation  # Update the previous operation

# Repeat the above steps for other main topics and their subtopics

# Visualization (Optional)
nx.draw(G, with_labels=True, node_size=1000, font_size=8)
plt.show()

# Save to a file or export (Optional)
nx.write_gexf(G, "/home/glossner/GitRepos/knowledge/gephi/math_taxonomy_graph.gexf")

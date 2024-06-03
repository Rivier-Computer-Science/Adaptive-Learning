import KnowledgeGraphs.math_graph as mg
import KnowledgeGraphs.math_taxonomy as mt

def main():
    kg = mg.KnowledgeGraph()
    kg.build_dag_from_dict(mt.subsubsub_topics)

    

if __name__ == '__main__':
    main()

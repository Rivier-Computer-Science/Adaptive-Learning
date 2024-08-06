import math_graph as mg
import math_taxonomy as mt

def main():
    kg = mg.KnowledgeGraph()
    kg.build_dag_from_dict(mt.subsubsub_topics)
    print(kg.find_first_node())

    

if __name__ == '__main__':
    main()

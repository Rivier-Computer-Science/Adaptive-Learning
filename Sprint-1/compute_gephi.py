import os
import math
import math_taxonomy as mt

def calculate_radius_for_spacing(num_points, individual_radius, separation_factor=1.5, additional_radius=0.0):
    """
    Calculate the radius of a circle needed to place a given number of points
    evenly spaced along its circumference, considering the size of each point.
    """
    # Each point occupies a space equal to its diameter along the circle's circumference
    total_space_needed = num_points * separation_factor * individual_radius + additional_radius
    # Calculate the radius needed to fit this total space on the circle's circumference
    return total_space_needed / (2 * math.pi)


def generate_coordinates_for_keys(topics, individual_radius, separation, start_angle=0.0, additional_radius=0.0):
    num_topics = len(topics.keys())
    radius = calculate_radius_for_spacing(num_topics, individual_radius, separation, additional_radius)

    coordinates = {}
    topics_keys = list(topics.keys()) 
    for i in range(num_topics):
        angle = start_angle - 2 * math.pi * i / num_topics
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        coordinates[ topics_keys[i] ] = ( round(x,2) , round(y,2) )
    
    return coordinates

def generate_coordinates_for_values(topics, individual_radius, separation, start_angle=0.0,  additional_radius=0.0):
    num_topics = sum(len(values) for values in topics.values())
    radius = calculate_radius_for_spacing(num_topics, individual_radius, separation, additional_radius)

    coordinates = {}
    i=0
    for key in topics:
        for value in topics[key]:
            angle = start_angle - 2 * math.pi * i / num_topics
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            i += 1
            coordinates[value] = ( round(x,2) , round(y,2) )

    return coordinates


def find_radial_angle_of_subtopic(main_topic_coords, topics_and_subtopics, main_topic_name):
    """
    Find the radial angle of a subtopic based on its alignment with the main topic.

    :param main_topic_coords: Coordinates of main topics.
    :param topics_and_subtopics: Dictionary of main topics and their subtopics.
    :param main_topic_name: The name of the main topic.
    :param subtopic_name: The name of the subtopic to find the radial angle for.
    :return: Radial angle of the subtopic.
    """
    # Find the index of the main topic
    main_topic_index = list(topics_and_subtopics.keys()).index(main_topic_name)

    # Get the coordinates of the main topic
    x, y = main_topic_coords[main_topic_index]

    # Calculate the radial angle
    angle = math.atan2(y, x)
    return angle

def replace_spaces_in_dictionary(dict):
    dict_new = {key.replace(" ", "_"): [value.replace(" ", "_") for value in values]
                for key, values in dict.items()}       
    return dict_new


def generate_gephi_gdf(topics_and_subtopics, subsub_topics, subsubsub_topics, 
                       main_topic_coords, subtopic_coords, subsub_topic_coords, subsubsub_topic_coords, 
                       individual_radius_main_topics, individual_radius_subtopics, individual_radius_subsub_topics, individual_radius_subsubsub_topics, 
                       topic_colors):
    gdf_content = "nodedef>name VARCHAR,label VARCHAR,width DOUBLE,x DOUBLE,y DOUBLE,color VARCHAR\n"

    # Add nodes for main topics with coordinates, width, and color
    for topic, subtopics in topics_and_subtopics.items():
        x,y = main_topic_coords[topic]
        color = f"\"{topic_colors.get(topic, '255,255,255')}\""
        gdf_content += f"{topic},{topic.replace('_',' ')},{individual_radius_main_topics},{x},{y},{color}\n"
        
        # Add nodes for each subtopic with their coordinates and parent topic's color
        for subtopic in subtopics:
            sub_x, sub_y = subtopic_coords[subtopic]
            gdf_content += f"{subtopic},{subtopic.split('->')[-1].replace('_',' ')},{individual_radius_subtopics},{sub_x},{sub_y},{color}\n"

        
   # Add nodes for subsub topics with correct color based on main topic
    for subtopic_key, subsub_list in subsub_topics.items():
        # Extract the main topic name from the subtopic key
        main_topic_key = subtopic_key.split('->')[0]
        color = f"\"{topic_colors.get(main_topic_key, '255,255,255')}\""

        for subsub_topic in subsub_list:
            subsub_x, subsub_y = subsub_topic_coords[subsub_topic]
            gdf_content += f"{subsub_topic},{subsub_topic.split('->')[-1].replace('_',' ')},{individual_radius_subsub_topics},{subsub_x},{subsub_y},{color}\n"

    # Add nodes for subsubsub topics with correct color based on main topic
    for subsub_topic_key, subsubsub_list in subsubsub_topics.items():
        main_topic_key = subsub_topic_key.split('->')[0]
        color = f"\"{topic_colors.get(main_topic_key, '255,255,255')}\""

        for subsubsub_topic in subsubsub_list:
            subsubsub_x, subsubsub_y = subsubsub_topic_coords[subsubsub_topic]
            gdf_content += f"{subsubsub_topic},{subsubsub_topic.split('->')[-1].replace('_',' ')},{individual_radius_subsubsub_topics},{subsubsub_x},{subsubsub_y},{color}\n"



#     ######################################################
#     # EDGES
#     ######################################################

    # Add directed edges from main topics to subtopics and from subtopics to subsub topics
    gdf_content += "edgedef>node1 VARCHAR,node2 VARCHAR,directed BOOLEAN\n"

 

    # Add directed edges from main topics to subtopics
    for main_topic, subtopics in topics_and_subtopics.items():
        for subtopic in subtopics:
            gdf_content += f"{main_topic},{subtopic},true\n"

            # Add directed edges from each subtopic to all its corresponding subsub topics
            #print('main_topic: ', main_topic, '  subtopic: ', subtopic)
            if subtopic in subsub_topics:
                for subsub_topic in subsub_topics[subtopic]:
                    #print('subsub_topic: ', subsub_topic)
                    gdf_content += f"{subtopic},{subsub_topic},true\n"



    # Add directed edges between main topics in the order they appear
    main_topics = list(topics_and_subtopics.keys())
    for i in range(len(main_topics) - 1):
        from_topic = main_topics[i]
        to_topic = main_topics[i + 1]
        gdf_content += f"{from_topic},{to_topic},true\n"

    # Add directed edges between adjacent subtopics
    for subtopics in topics_and_subtopics.values():
        for i in range(len(subtopics) - 1):
            gdf_content += f"{subtopics[i]},{subtopics[i + 1]},true\n"
    
    # Add directed edges between adjacent subsub topics
    for subsub_list in subsub_topics.values():
        for i in range(len(subsub_list) - 1):
            gdf_content += f"{subsub_list[i]},{subsub_list[i + 1]},true\n"

 
    # Add directed edges between adjacent subsubsub topics
    for subsubsub_list in subsubsub_topics.values():
        for i in range(len(subsubsub_list) - 1):
            gdf_content += f"{subsubsub_list[i]},{subsubsub_list[i + 1]},true\n"

    # Add directed edges from subsub topics to subsubsub topics and between adjacent subsubsub topics
    for subsub_topic, subsubsub_list in subsubsub_topics.items():
        for subsubsub_topic in subsubsub_list:
            gdf_content += f"{subsub_topic},{subsubsub_topic},true\n"

    return gdf_content


def create_multidimensional_dict(topics_and_subtopics, subsub_topics, subsubsub_topics):
    """
    Creates a multidimensional dictionary from given topics, subtopics, and sub-subtopics.

    :param topics_and_subtopics: Dictionary of topics and their subtopics
    :param subsub_topics: Dictionary of subtopics and their further subtopics
    :param subsubsub_topics: Dictionary of sub-subtopics and their detailed topics
    :return: Nested dictionary combining all three dictionaries
    """
    multidimensional_dict = {}
    for topic, subtopics in topics_and_subtopics.items():
        multidimensional_dict[topic] = {}
        for subtopic in subtopics:
            if subtopic in subsub_topics:
                multidimensional_dict[topic][subtopic] = {}
                for subsub in subsub_topics[subtopic]:
                    if subsub in subsubsub_topics:
                        multidimensional_dict[topic][subtopic][subsub] = {}
                        for subsubsub_item in subsubsub_topics[subsub]:
                            # Now we iterate through each item in the list and assign it to the dictionary
                            multidimensional_dict[topic][subtopic][subsub][subsubsub_item] = None
                    else:
                        multidimensional_dict[topic][subtopic][subsub] = None
            else:
                multidimensional_dict[topic][subtopic] = None
    return multidimensional_dict





def flatten_dict(d, parent_key='', sep=' -> '):
    """
    Flatten a nested dictionary into a list of strings showing the hierarchy.

    :param d: The dictionary to flatten
    :param parent_key: The base path for the current level
    :param sep: Separator to use between levels
    :return: A list of strings representing the flattened structure
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep))
        elif v is None or isinstance(v, list):
            if isinstance(v, list):
                items.append(f"{new_key}: {', '.join(v)}")
            else:
                items.append(new_key)
    return items

def pretty_print(d, indent=0, sep=' -> '):
    """
    Recursively pretty prints a nested dictionary to visually represent its hierarchical structure.

    :param d: The dictionary to be printed
    :param indent: The current indentation level
    :param sep: Separator to use between levels
    """
    for key, value in d.items():
        print(' ' * indent + str(key))
        if isinstance(value, dict):
            pretty_print(value, indent + len(sep))
        elif isinstance(value, list):
            for item in value:
                print(' ' * (indent + len(sep)) + str(item))
        else:
            print(' ' * (indent + len(sep)) + str(value))

#######################################################
# Main()
#######################################################


# Parameters for individual topic and subtopic radii
topics_and_subtopics = mt.topics_and_subtopics
subsub_topics = mt.subsub_topics
subsubsub_topics = mt.subsubsub_topics

# Adjust the starting angle to place 'Arithmetic' just below the x-axis in the 3rd quadrant
start_angle = math.pi # 180 degrees
#start_angle = math.pi + math.radians(10.0) # 190 degrees

individual_radius_main_topics = 50
individual_radius_subtopics = 30
individual_radius_subsub_topics = 15
individual_radius_subsubsub_topics = 5

separation_main_topics = 2.0
separation_sub_topics = 2.5
separation_subsub_topics = 1.0
separation_subsubsub_topics = 0.5

topic_colors = mt.topic_colors


# Generate Coordinates
main_topic_coords = generate_coordinates_for_keys(topics_and_subtopics, individual_radius_main_topics, separation_main_topics,start_angle)
sub_topic_coords    = generate_coordinates_for_values(topics_and_subtopics, individual_radius_subtopics, separation_sub_topics, start_angle)
subsub_topic_coords = generate_coordinates_for_values(subsub_topics, individual_radius_subtopics, separation_sub_topics, start_angle)
subsubsub_topic_coords = generate_coordinates_for_values(subsubsub_topics, individual_radius_subtopics, separation_sub_topics, start_angle)


# Export graph in GDF format
gdf_data = generate_gephi_gdf(topics_and_subtopics, subsub_topics, subsubsub_topics, 
                             main_topic_coords, sub_topic_coords, subsub_topic_coords, subsubsub_topic_coords,
                             individual_radius_main_topics, individual_radius_subtopics, individual_radius_subsub_topics, individual_radius_subsubsub_topics, 
                             topic_colors)



# Write the GDF content to a file
file_path = './gephi/math_nodes_and_edges.gdf'
if os.path.exists(file_path):
    os.remove(file_path)

with open(file_path, 'w') as file:
    file.write(gdf_data)

print(gdf_data)
print(f"GDF file saved to: {file_path}")


print('Length of topic coords: ', len(subsub_topic_coords))
print('Length of topics: ', len(topics_and_subtopics.keys()))

print('Length of subtopic coords: ', )
print('Length of subtopics: ', len(topics_and_subtopics.values()))
length = 0
for k, v in subsubsub_topics.items():
    length += len(v)

print("length of subsubsub topics: ", length)


print('Length of Subsubsub topic coords: ', len(subsub_topic_coords))
length = 0
for k, v in subsubsub_topics.items():
    length += len(v)

print("length of subsubsub topics: ", length)

# print('***********************************************************************************')
# print('topics_and_subtopics_new\n', topics_and_subtopics)
# print('***********************************************************************************')
# print('subsub_topics_new\n', subsub_topics)
# print('***********************************************************************************')
# print('subsubsub_topics_new\n', subsubsub_topics)
# print('***********************************************************************************')

# print('###########################################################################################')
# md_dict = create_multidimensional_dict(topics_and_subtopics,subsub_topics, subsubsub_topics)
# print(md_dict)

# pretty_print(md_dict)

# for k,subsubsub_list in subsubsub_topics.items():
#     new_list = []
#     for subsubsub in subsubsub_list:
#         new_list.append(f"{k}->{subsubsub}")
#     subsubsub_topics[k] = new_list

# print(subsubsub_topics)


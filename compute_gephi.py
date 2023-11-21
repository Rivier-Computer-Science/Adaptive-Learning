import os
import math
import math_taxonomy as mt

def calculate_radius_for_spacing(num_points, individual_radius,separation_factor=1.5):
    """
    Calculate the radius of a circle needed to place a given number of points
    evenly spaced along its circumference, considering the size of each point.
    """
    # Each point occupies a space equal to its diameter along the circle's circumference
    total_space_needed = num_points * separation_factor * individual_radius
    # Calculate the radius needed to fit this total space on the circle's circumference
    return total_space_needed / (2 * math.pi)

def generate_coordinates(topics_and_subtopics, individual_radius_main_topics, individual_radius_subtopics,separation_main_topics,separation_sub_topics):
    num_main_topics = len(topics_and_subtopics.keys())
    radius_main_topics = calculate_radius_for_spacing(num_main_topics, individual_radius_main_topics,separation_main_topics)
    radius_subtopics = calculate_radius_for_spacing(sum([len(subtopics) for subtopics in topics_and_subtopics.values()]), individual_radius_subtopics,separation_sub_topics)

    # Adjust the starting angle to place 'Arithmetic' just below the x-axis in the 3rd quadrant
    start_angle_main_topics = math.pi  # 180 degrees, pointing left

    main_topic_coordinates = []
    for i in range(num_main_topics):
        angle = start_angle_main_topics - 2 * math.pi * i / num_main_topics
        x = radius_main_topics * math.cos(angle)
        y = radius_main_topics * math.sin(angle)
        main_topic_coordinates.append((x, y))

    # Subtopic coordinates - also counterclockwise
    subtopic_coordinates = []
    angle_step_subtopics = 2 * math.pi / sum([len(subtopics) for subtopics in topics_and_subtopics.values()])
    current_angle = start_angle_main_topics - angle_step_subtopics  # Start just after 'Arithmetic'

    for _, subtopics in topics_and_subtopics.items():
        for _ in subtopics:
            x = radius_subtopics * math.cos(current_angle)
            y = radius_subtopics * math.sin(current_angle)
            subtopic_coordinates.append((x, y))
            current_angle -= angle_step_subtopics  # Move counterclockwise

    return main_topic_coordinates, subtopic_coordinates

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

def generate_subsub_topic_coordinates(subsub_topics, individual_radius_subsub_topics, separation_subsub_topics,sub_topic_radial_angle):
    num_subsub_topics = sum([len(subsub_list) for subsub_list in subsub_topics.values()])
    radius_subsub_topics = calculate_radius_for_spacing(num_subsub_topics, individual_radius_subsub_topics, separation_subsub_topics)

    # Starting angle for 'Addition' aligned with 'Basic Operations'
    start_angle_subsub_topics = sub_topic_radial_angle

    subsub_topic_coordinates = []
    angle_step_subsub_topics = 2 * math.pi / num_subsub_topics
    current_angle = start_angle_subsub_topics

    for _, subsub_list in subsub_topics.items():
        for _ in subsub_list:
            x = radius_subsub_topics * math.cos(current_angle)
            y = radius_subsub_topics * math.sin(current_angle)
            subsub_topic_coordinates.append((x, y))
            current_angle -= angle_step_subsub_topics  # Move counterclockwise

    return subsub_topic_coordinates

import math

def generate_subsubsub_topic_coordinates(start_angle, subsubsub_topics, individual_radius, separation):
    """
    Generate coordinates for subsubsub topics, starting from a given angle and using individual radius.

    :param start_angle: Starting radial angle in radians.
    :param subsubsub_topics: List of subsubsub topics.
    :param individual_radius: Radius for placing each subsubsub topic.
    :return: Dictionary of coordinates for subsubsub topics.
    """
    radius_subsubsubtopics = calculate_radius_for_spacing(sum([len(subsubsub_topics) for subsubsubtopics in subsubsub_topics.values()]), 
                                                          individual_radius,separation)

    subsubsub_topic_coords = {}
    num_subsubsub_topics = len(subsubsub_topics)

    # Calculate the angular gap between each subsubsub topic
    if num_subsubsub_topics > 1:
        angle_gap = 2 * math.pi / num_subsubsub_topics
    else:
        angle_gap = 0  # Avoid division by zero if only one subsubsub topic

    # Generate coordinates for each subsubsub topic
    for i, subsubsub_topic in enumerate(subsubsub_topics):
        angle = start_angle + angle_gap * i
        x = radius_subsubsubtopics * math.cos(angle) / 9.0  #FIXME: Hack
        y = radius_subsubsubtopics * math.sin(angle) / 9.0  #FIXME: Hack
        subsubsub_topic_coords[subsubsub_topic] = (x, y)

    return subsubsub_topic_coords.values()


def round_coordinates(coordinates):
    """
    Round the coordinates to two decimal places.
    """
    return [(round(x, 2), round(y, 2)) for x, y in coordinates]


def replace_spaces_in_dictionary(dict):
    dict_new = {key.replace(" ", "_"): [value.replace(" ", "_") for value in values]
                for key, values in dict.items()}       
    return dict_new

def rename_nodes_in_dictionary(topics_and_subtopics, subsub_topics, subsubsub_topics):
    topics_and_subtopics_new = replace_spaces_in_dictionary(topics_and_subtopics)
    subsub_topics_new = replace_spaces_in_dictionary(subsub_topics)
    subsub_topics_new2 = {}
    subsubsub_topics_new = replace_spaces_in_dictionary(subsubsub_topics)
    subsub_topics_renamed = {}
    subsubsub_topics_renamed = {}
    subsubsub_topics_new2 = {}

    # Renaming subtopics
    for km, subtopics in topics_and_subtopics_new.items():
        modified_subtopics = [km + '->' + subtopic for subtopic in subtopics]
        topics_and_subtopics_new[km] = modified_subtopics

    # Renaming subsub topics
    for ks, subsubtopics in subsub_topics_new.items():
        modified_subsubtopics = []
        new_subsub_key = ''
        for subsubtopic in subsubtopics:
            # Find the main topic and subtopic            
            for main_topic, subtopics in topics_and_subtopics_new.items():
                if any(ks in subtopic for subtopic in subtopics):                    
                    new_subsub_key = f"{main_topic}->{ks}"
                    modified_subsubtopics.append(f"{main_topic}->{ks}->{subsubtopic}")
                    break
            subsub_topics_renamed[new_subsub_key] = subsubtopic

        # Assign the modified list to the key in subsub_topics_new
        subsub_topics_new2[new_subsub_key] = modified_subsubtopics


    # Renaming subsubsub topics based on subsub topics values
    for kss, subsubsubtopics in subsubsub_topics_new.items():
        print('kss: ', kss)
        print('subsubsubtopics: ', subsubsubtopics)
        modified_subsubsubtopics = []
        new_subsubsub_key = ''
        for subsubsubtopic in subsubsubtopics:
            matched = False
            for subtopic, subsubtopics in subsub_topics_new2.items():
                if any(kss in subsubtopic for subsubtopic in subsubtopics):
                    new_subsubsub_key = f"{subtopic}->{kss}"
                    new_subsubsub_topic = f"{subtopic}->{kss}->{subsubsubtopic}"
                    modified_subsubsubtopics.append(new_subsubsub_topic)
                    print('new_subsubsub_key:       ', new_subsubsub_key)
                    print('modified_subsubsubtopic: ', new_subsubsub_topic )
                    matched = True
                    break
            if matched:
                break
        subsubsub_topics_renamed[new_subsubsub_key] = subsubsubtopic

        print('modified_subsubsubtopics: ', modified_subsubsubtopics)
        subsubsub_topics_new2[new_subsubsub_key] = modified_subsubsubtopics

    return topics_and_subtopics_new, subsub_topics_new2, subsubsub_topics_new2


def generate_gephi_gdf(topics_and_subtopics, subsub_topics, subsubsub_topics, 
                       main_topic_coords, subtopic_coords, subsub_topic_coords, subsubsub_topic_coords, 
                       individual_radius_main_topics, individual_radius_subtopics, individual_radius_subsub_topics, individual_radius_subsubsub_topics, 
                       topic_colors):
    gdf_content = "nodedef>name VARCHAR,label VARCHAR,width DOUBLE,x DOUBLE,y DOUBLE,color VARCHAR\n"

    # Add nodes for main topics with coordinates, width, and color
    for i, (main_topic, subtopics) in enumerate(topics_and_subtopics.items()):
        x, y = main_topic_coords[i]
        color = f"\"{topic_colors.get(main_topic, '255,255,255')}\""
        gdf_content += f"{main_topic},{main_topic.replace('_',' ')},{individual_radius_main_topics},{x},{y},{color}\n"

        # Add nodes for each subtopic with their coordinates and parent topic's color
        for subtopic in subtopics:
            if subtopic_coords:  # Check for available coordinates
                sub_x, sub_y = subtopic_coords.pop(0)
                gdf_content += f"{subtopic},{subtopic.split('->')[-1].replace('_',' ')},{individual_radius_subtopics},{sub_x},{sub_y},{color}\n"

   # Add nodes for subsub topics with correct color based on main topic
    for subtopic_key, subsub_list in subsub_topics.items():
        # Extract the main topic name from the subtopic key
        main_topic_key = subtopic_key.split('->')[0]
        color = f"\"{topic_colors.get(main_topic_key, '255,255,255')}\""

        for subsub_topic in subsub_list:
            if subsub_topic_coords:  # Check for available coordinates
                subsub_x, subsub_y = subsub_topic_coords.pop(0)
                gdf_content += f"{subsub_topic},{subsub_topic.split('->')[-1].replace('_',' ')},{individual_radius_subsub_topics},{subsub_x},{subsub_y},{color}\n"

    # Add nodes for subsubsub topics with correct color based on main topic
    for subsub_topic_key, subsubsub_list in subsubsub_topics.items():
        main_topic_key = subsub_topic_key.split('->')[0]
        color = f"\"{topic_colors.get(main_topic_key, '255,255,255')}\""

        for subsubsub_topic in subsubsub_list:
            if subsubsub_topic_coords:  # Check for available coordinates
                subsubsub_x, subsubsub_y = subsubsub_topic_coords.pop(0)
                gdf_content += f"{subsubsub_topic},{subsubsub_topic.split('->')[-1].replace('_',' ')},{individual_radius_subsubsub_topics},{subsubsub_x},{subsubsub_y},{color}\n"



    ######################################################
    # EDGES
    ######################################################

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

 
    # # Add directed edges from subsub topics to subsubsub topics and between adjacent subsubsub topics
    # for subsub_topic, subsubsub_list in subsubsub_topics.items():
    #     for subsubsub_topic in subsubsub_list:
    #         gdf_content += f"{subsub_topic},{subsubsub_topic},true\n"
    #     for i in range(len(subsubsub_list) - 1):
    #         gdf_content += f"{subsubsub_list[i]},{subsubsub_list[i + 1]},true\n"




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

individual_radius_main_topics = 50
individual_radius_subtopics = 30
individual_radius_subsub_topics = 15
individual_radius_subsubsub_topics = 5

separation_main_topics = 2.0
separation_sub_topics = 1.5
separation_subsub_topics = 1.5
separation_subsubsub_topics = 1.5

topic_colors = mt.topic_colors

# Rename nodes, replace spaces with underscores and provide full taxonomy
topics_and_subtopics_new, subsub_topics_new, subsubsub_topics_new = rename_nodes_in_dictionary(topics_and_subtopics, subsub_topics, subsubsub_topics)

# Generate Coordinates
main_topic_coords, sub_topic_coords = generate_coordinates(topics_and_subtopics_new, individual_radius_main_topics, individual_radius_subtopics,separation_main_topics,separation_sub_topics)
rounded_main_topic_coords = round_coordinates(main_topic_coords)
rounded_sub_topic_coords = round_coordinates(sub_topic_coords)

subsub_topic_starting_radial_angle = find_radial_angle_of_subtopic(main_topic_coords, topics_and_subtopics_new, "Arithmetic" )
subsub_topic_coords = generate_subsub_topic_coordinates(subsub_topics_new, individual_radius_subsub_topics, separation_subsub_topics,subsub_topic_starting_radial_angle)
rounded_subsub_topic_coords = round_coordinates(subsub_topic_coords)


#subsubsub_topic_starting_radial_angle = find_radial_angle_of_subtopic(subsub_topics_new, subsubsub_topics_new, "Arithmetic->Recognizing_Shapes->Basic_Shapes")
subsubsub_topic_coords = generate_subsubsub_topic_coordinates(math.radians(-180), subsubsub_topics_new, individual_radius_subsubsub_topics,separation_subsubsub_topics)
print('subsubsub topic coords: \n',subsubsub_topic_coords)
rounded_subsubsub_topic_coords = round_coordinates(subsubsub_topic_coords)

# Export graph in GDF format
gdf_data = generate_gephi_gdf(topics_and_subtopics_new, subsub_topics_new, subsubsub_topics_new, 
                              rounded_main_topic_coords,rounded_sub_topic_coords,rounded_subsub_topic_coords, rounded_subsubsub_topic_coords,
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

print('***********************************************************************************')
print('topics_and_subtopics_new\n', topics_and_subtopics_new)
print('***********************************************************************************')
print('subsub_topics_new\n', subsub_topics_new)
print('***********************************************************************************')
print('subsubsub_topics_new\n', subsubsub_topics_new)
print('***********************************************************************************')

print('###########################################################################################')
md_dict = create_multidimensional_dict(topics_and_subtopics_new,subsub_topics_new, subsubsub_topics_new)
print(md_dict)

pretty_print(md_dict)

print('******************************************************************')
print(replace_spaces_in_dictionary(mt.subsubsub_topics))
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


def round_coordinates(coordinates):
    """
    Round the coordinates to two decimal places.
    """
    return [(round(x, 2), round(y, 2)) for x, y in coordinates]


def resolve_duplicate_subtopic_names(topics_and_subtopics):
    # Create a list of all subtopic names
    all_subtopics = [subtopic for subtopics in topics_and_subtopics.values() for subtopic in subtopics]

    # Identify duplicates
    duplicates = {name for name in all_subtopics if all_subtopics.count(name) > 1}

    # Resolve duplicates by appending characters from the main topic's name
    resolved_subtopics = {}
    for main_topic, subtopics in topics_and_subtopics.items():
        resolved_subtopics[main_topic] = []
        for subtopic in subtopics:
            new_name = subtopic
            while new_name in duplicates:
                main_topic_name = main_topic
                new_name = main_topic_name[0] + new_name  # Append first letter of main topic
                main_topic_name = main_topic_name[1:]  # Reduce main topic name for the next iteration if needed
                if main_topic_name == "":  # Restart appending if we run out of characters
                    main_topic_name = main_topic
            resolved_subtopics[main_topic].append(new_name)
            duplicates.add(new_name)  # Update duplicates set with the new name

    return resolved_subtopics

def resolve_duplicate_subsub_topic_names(subsub_topics):
    # Create a combined list of all subsub topic names
    all_subsub_topics = [subsub for subsubs in subsub_topics.values() for subsub in subsubs]

    # Identify duplicates and initialize counters
    duplicates = {name: 0 for name in all_subsub_topics if all_subsub_topics.count(name) > 1}

    # Resolve duplicates starting from subsub topics
    resolved_subsub_topics = {}
    for subtopic, subsubs in subsub_topics.items():
        resolved_subsub_topics[subtopic] = []
        for subsub in subsubs:
            if subsub in duplicates:
                duplicates[subsub] += 1  # Increment counter for this duplicate
                new_name = subsub + str(duplicates[subsub])
            else:
                new_name = subsub
            resolved_subsub_topics[subtopic].append(new_name)

    return resolved_subsub_topics



def generate_gephi_gdf(topics_and_subtopics, subsub_topics, main_topic_coords, subtopic_coords, subsub_topic_coords, individual_radius_main_topics, individual_radius_subtopics, individual_radius_subsub_topics, topic_colors):
    gdf_content = "nodedef>name VARCHAR,label VARCHAR,width DOUBLE,x DOUBLE,y DOUBLE,color VARCHAR\n"

    # Process topics and subtopics to replace spaces with underscores
    topics_and_subtopics_new = {}
    subsub_topics_new = {}
 
    for km, subtopics in topics_and_subtopics.items(): # km: key main subtopics: values (sub topics)
        modified_subtopics = [ km + '->' + subtopic for subtopic in subtopics ]
        topics_and_subtopics_new[km] = modified_subtopics

    for ks, subsubtopics in subsub_topics.items():
        # Initialize a list to store the modified subsubtopics
        modified_subsubtopics = []

        # Iterate over each subsubtopic
        for subsubtopic in subsubtopics:
            # Find the main topic and subtopic
            for main_topic, subtopics in topics_and_subtopics_new.items():
                if any(ks in subtopic for subtopic in subtopics):
                    # Format string as "Main Topic->Subtopic->Subsubtopic"
                    modified_subsubtopic = f"{main_topic}->{ks}->{subsubtopic}"
                    modified_subsubtopics.append(modified_subsubtopic)
                    break  # Once found, no need to check other main topics

        # Assign the modified list to the key in subsub_topics_new
        subsub_topics_new[ks] = modified_subsubtopics
        
    print('modified dictionary', topics_and_subtopics_new)
    print('modified sub dictionary', subsub_topics_new)


    

    # for main_topic, subtopics in topics_and_subtopics.items():
    #     main_topic_key = main_topic.replace(' ', '_')        
    #     print('main_topic_key= ', main_topic_key)
    #     for subtopic in subtopics:
    #         subtopic_key = subtopic.replace(' ', '_')
    #         processed_subtopic_name = f"{main_topic_key}->{subtopic_key}"
    #         print(processed_subtopic_name)
    #         subtopics_list_new.append(processed_subtopic_name)
    #         for subsub_topic in subsub_topics:
    #             subsub_topic_key = subsub_topic.replace(' ','_')                           
    #             if subtopic_key == subtopic:                    
    #                 processed_subsub_topic_name = f"{main_topic_key}->{subtopic_key}->{subsub_topic_key}"
    #                 print(processed_subsub_topic_name)     
    #                 subsub_topics_list_new.append(processed_subsub_topic_name)
    #         subsub_topics_new[subtopic_key] = subsub_topics_list_new
    #         subsub_topics_list_new = []
    #     topics_and_subtopics_new[main_topic_key]=subtopics_list_new
    #     subtopics_list_new = []
    print('***************************************************')
#    print(topics_and_subtopics_new)
    print('***************************************************')
#    print(subsub_topics_new)


    processed_subtopics = {}
    for main_topic, subtopics in topics_and_subtopics.items():
        main_topic_key = main_topic.replace(' ', '_')
        for subtopic in subtopics:
            subtopic_key = subtopic.replace(' ', '_')
            processed_subtopic_name = f"{main_topic_key}->{subtopic_key}"
            processed_subtopics[processed_subtopic_name] = main_topic_key  # Mapping to main topic for color
            # Add subtopic nodes
            sub_x, sub_y = subtopic_coords.pop(0)
            color = f"\"{topic_colors.get(main_topic, '255,255,255')}\""
            gdf_content += f"{processed_subtopic_name},{subtopic},{individual_radius_subtopics},{sub_x},{sub_y},{color}\n"

            # Add subsub topic nodes
            original_subtopic_key = f"{main_topic}_{subtopic}"
            if original_subtopic_key in subsub_topics:
                for subsub_topic in subsub_topics[original_subtopic_key]:
                    subsub_topic_key = subsub_topic.replace(' ', '_')
                    processed_subsub_topic_name = f"{processed_subtopic_name}->{subsub_topic_key}"
                    if subsub_topic_coords:
                        subsub_x, subsub_y = subsub_topic_coords.pop(0)
                        gdf_content += f"{processed_subsub_topic_name},{subsub_topic},{individual_radius_subsub_topics},{subsub_x},{subsub_y},{color}\n"

    # Add main topic nodes
    for i, main_topic in enumerate(topics_and_subtopics.keys()):
        main_topic_key = main_topic.replace(' ', '_')
        x, y = main_topic_coords[i]
        color = f"\"{topic_colors.get(main_topic, '255,255,255')}\""
        gdf_content += f"{main_topic_key},{main_topic},{individual_radius_main_topics},{x},{y},{color}\n"

    gdf_content += "edgedef>node1 VARCHAR,node2 VARCHAR,directed BOOLEAN\n"

    # Add edges from main topics to subtopics
    for main_topic, subtopics in topics_and_subtopics.items():
        main_topic_key = main_topic.replace(' ', '_')
        for subtopic in subtopics:
            subtopic_key = subtopic.replace(' ', '_')
            processed_subtopic_name = f"{main_topic_key}->{subtopic_key}"
            gdf_content += f"{main_topic_key},{processed_subtopic_name},true\n"

            # Add edges from subtopics to subsub topics
            original_subtopic_key = f"{main_topic}_{subtopic}"
            if original_subtopic_key in subsub_topics:
                for subsub_topic in subsub_topics[original_subtopic_key]:
                    subsub_topic_key = subsub_topic.replace(' ', '_')
                    processed_subsub_topic_name = f"{processed_subtopic_name}->{subsub_topic_key}"
                    gdf_content += f"{processed_subtopic_name},{processed_subsub_topic_name},true\n"

    return gdf_content




#######################################################
# Main()
#######################################################


# Parameters for individual topic and subtopic radii
topics_and_subtopics = mt.topics_and_subtopics
#topics_and_subtopics = resolve_duplicate_subtopic_names(topics_and_subtopics)
subsub_topics = mt.subsub_topics
#subsub_topics = resolve_duplicate_subsub_topic_names(subsub_topics)
individual_radius_main_topics = 50
individual_radius_subtopics = 30
individual_radius_subsub_topics = 15
separation_main_topics = 2.0
separation_sub_topics = 1.5
separation_subsub_topics = 1.5
topic_colors = mt.topic_colors

# Generate and round coordinates
main_topic_coords, sub_topic_coords = generate_coordinates(topics_and_subtopics, individual_radius_main_topics, individual_radius_subtopics,separation_main_topics,separation_sub_topics)
subsub_topic_starting_radial_angle = find_radial_angle_of_subtopic(main_topic_coords, topics_and_subtopics, "Arithmetic" )
subsub_topic_coords = generate_subsub_topic_coordinates(subsub_topics, individual_radius_subsub_topics, separation_subsub_topics,subsub_topic_starting_radial_angle)
rounded_main_topic_coords = round_coordinates(main_topic_coords)
rounded_sub_topic_coords = round_coordinates(sub_topic_coords)
rounded_subsub_topic_coords = round_coordinates(subsub_topic_coords)

# Print the rounded coordinates
print("Rounded Main Topic Coordinates:")
for coord in rounded_main_topic_coords:
    print(coord)

print("\nRounded Sub topic Coordinates:")
for coord in rounded_sub_topic_coords:
    print(coord)

print("\nRounded Subsub topic Coordinates:")
for coord in rounded_subsub_topic_coords:
    print(coord)

print(generate_gephi_gdf(topics_and_subtopics,subsub_topics, 
                         rounded_main_topic_coords,rounded_sub_topic_coords,rounded_subsub_topic_coords,
                         individual_radius_main_topics,individual_radius_subtopics,individual_radius_subsub_topics, topic_colors))
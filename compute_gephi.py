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




def round_coordinates(coordinates):
    """
    Round the coordinates to two decimal places.
    """
    return [(round(x, 2), round(y, 2)) for x, y in coordinates]

def generate_gephi_gdf(topics_and_subtopics, main_topic_coords, subtopic_coords, individual_radius_main_topics, individual_radius_subtopics, topic_colors):
    """
    Generate a Gephi GDF file content with nodes and directed edges, including RGB colors for each topic.
    Each topic node is connected to its subsequent topic and its subtopics. The color of each main topic is copied to its subtopics.

    :param topics_and_subtopics: Dictionary with main topics as keys and lists of subtopics as values.
    :param main_topic_coords: Coordinates of main topics.
    :param subtopic_coords: Coordinates of subtopics.
    :param individual_radius_main_topics: Radius of each main topic.
    :param individual_radius_subtopics: Radius of each subtopic.
    :param topic_colors: Dictionary with main topics as keys and their RGB color strings as values.
    :return: String representing the content of a GDF file.
    """
    gdf_content = "nodedef>name VARCHAR,label VARCHAR,width DOUBLE,x DOUBLE,y DOUBLE,color VARCHAR\n"

    # Add nodes for main topics with coordinates, width, and color
    for i, (topic, subtopics) in enumerate(topics_and_subtopics.items()):
        x, y = main_topic_coords[i]
        color = f'"{topic_colors.get(topic, "255,255,255")}"'  # Enclose color in quotes
        gdf_content += f"{topic},{topic},{individual_radius_main_topics},{x},{y},{color}\n"

        # Add nodes for each subtopic with their coordinates and parent topic's color
        for subtopic in subtopics:
            sub_x, sub_y = subtopic_coords.pop(0)
            gdf_content += f"{topic}_{subtopic},{subtopic},{individual_radius_subtopics},{sub_x},{sub_y},{color}\n"

    gdf_content += "edgedef>node1 VARCHAR,node2 VARCHAR,directed BOOLEAN\n"

    # Directed edges from each topic to the next and to each of its subtopics
    topics = list(topics_and_subtopics.keys())
    for i, topic in enumerate(topics):
        next_topic = topics[(i + 1) % len(topics)]
        gdf_content += f"{topic},{next_topic},true\n"

        for subtopic in topics_and_subtopics[topic]:
            gdf_content += f"{topic},{topic}_{subtopic},true\n"

    return gdf_content

#######################################################
# Main()
#######################################################


# Parameters for individual topic and subtopic radii
topics_and_subtopics = mt.topics_and_subtopics
subsub_topics = mt.subsub_topics
individual_radius_main_topics = 50
individual_radius_subtopics = 30
separation_main_topics = 2.0
separation_sub_topics = 1.5
topic_colors = mt.topic_colors

# Generate and round coordinates
main_topic_coords, subtopic_coords = generate_coordinates(topics_and_subtopics, individual_radius_main_topics, individual_radius_subtopics,separation_main_topics,separation_sub_topics)
rounded_main_topic_coords = round_coordinates(main_topic_coords)
rounded_subtopic_coords = round_coordinates(subtopic_coords)

# Print the rounded coordinates
print("Rounded Main Topic Coordinates:")
for coord in rounded_main_topic_coords:
    print(coord)

print("\nRounded Subtopic Coordinates:")
for coord in rounded_subtopic_coords:
    print(coord)

print(generate_gephi_gdf(topics_and_subtopics,rounded_main_topic_coords,rounded_subtopic_coords,individual_radius_main_topics,individual_radius_subtopics,topic_colors))
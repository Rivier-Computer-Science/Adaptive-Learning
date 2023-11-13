topics_and_subtopics = {
    "Arithmetic": [
        "Basic operations",
        "Fractions",
        "Decimals",
        "Percentages",
        "Ratios and Proportions"
    ],
    "Algebra": [
        "Algebraic Expressions",
        "Linear Equations",
        "Inequalities",
        "Systems of Equations",
        "Quadratic Equations",
        "Polynomials",
        "Functions"
    ],
    "Geometry": [
        "Basic Geometric Shapes",
        "Congruence and Similarity",
        "Pythagorean Theorem",
        "Circles",
        "Area and Volume",
        "Coordinate Geometry",
        "Trigonometry"
    ],
    "Trigonometry": [
        "Trigonometric Ratios",
        "Graphs of Trigonometric Functions",
        "Trigonometric Identities",
        "Applications"
    ],
    "Statistics and Probability": [
        "Descriptive Statistics",
        "Probability Basics",
        "Combinations and Permutations",
        "Random Variables and Distributions",
        "Inferential Statistics"
    ],
    "Pre-Calculus": [
        "Advanced Algebra",
        "Complex Numbers",
        "Exponential and Logarithmic Functions",
        "Advanced Trigonometry",
        "Sequences and Series",
        "Matrices"
    ],
    "Calculus": [
        "Limits",
        "Derivatives",
        "Integration",
        "Differential Equations",
        "Multivariable Calculus"
    ],
    "Advanced Calculus (Honors)": [
        "Series and Sequences",
        "Vector Calculus",
        "Multivariable Calculus",
        "Differential Equations",
        "Special Topics"
    ],
    "Discrete Mathematics (Honors)": [
        "Logic and Proofs",
        "Set Theory",
        "Combinatorics",
        "Graph Theory",
        "Algorithms and Complexity"
    ],
    "Linear Algebra (Honors)": [
        "Vector Spaces",
        "Linear Transformations",
        "Matrices",
        "Systems of Linear Equations",
        "Advanced Topics"
    ],
    "Advanced Statistics (Honors)": [
        "Regression Analysis",
        "ANOVA",
        "Nonparametric Tests",
        "Time Series Analysis",
        "Bayesian Statistics"
    ],
    "Mathematical Proofs and Theory (Honors)": [
        "Introduction to Proofs",
        "Number Theory",
        "Group Theory",
        "Real Analysis",
        "Topology"
    ]
}
import math

import math

def calculate_radius_for_spacing(num_points, individual_radius):
    """
    Calculate the radius of a circle needed to place a given number of points
    evenly spaced along its circumference, considering the size of each point.
    """
    # Each point occupies a space equal to its diameter along the circle's circumference
    total_space_needed = num_points * 2 * individual_radius
    # Calculate the radius needed to fit this total space on the circle's circumference
    return total_space_needed / (2 * math.pi)
def generate_coordinates(topics_and_subtopics, individual_radius_main_topics, individual_radius_subtopics):
    num_main_topics = len(topics_and_subtopics.keys())
    radius_main_topics = calculate_radius_for_spacing(num_main_topics, individual_radius_main_topics)
    radius_subtopics = calculate_radius_for_spacing(sum([len(subtopics) for subtopics in topics_and_subtopics.values()]), individual_radius_subtopics)

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

def generate_gephi_gdf(topics_and_subtopics, main_topic_coords, subtopic_coords, individual_radius_main_topics, individual_radius_subtopics):
    gdf_content = "nodedef>name VARCHAR,label VARCHAR,width DOUBLE,x DOUBLE,y DOUBLE\n"

    # Main topics
    for topic, coords in zip(topics_and_subtopics.keys(), main_topic_coords):
        x, y = coords
        gdf_content += f"{topic},{topic},{individual_radius_main_topics},{x},{y}\n"

    # Subtopics
    subtopic_coord_index = 0
    for topic, subtopics in topics_and_subtopics.items():
        for subtopic in subtopics:
            sub_x, sub_y = subtopic_coords[subtopic_coord_index]
            gdf_content += f"{topic}_{subtopic},{subtopic},{individual_radius_subtopics},{sub_x},{sub_y}\n"
            subtopic_coord_index += 1

    # Edges
    gdf_content += "edgedef>node1 VARCHAR,node2 VARCHAR,directed BOOLEAN\n"
    topics = list(topics_and_subtopics.keys())
    for i, topic in enumerate(topics):
        next_topic = topics[(i + 1) % len(topics)]
        gdf_content += f"{topic},{next_topic},true\n"
        for subtopic in topics_and_subtopics[topic]:
            gdf_content += f"{topic},{topic}_{subtopic},true\n"

    return gdf_content



# Example usage with hypothetical data
# main_topic_coords and subtopic_coords need to be provided with the actual coordinates


# Parameters for individual topic and subtopic radii
individual_radius_main_topics = 50
individual_radius_subtopics = 30

# Generate and round coordinates
main_topic_coords, subtopic_coords = generate_coordinates(topics_and_subtopics, individual_radius_main_topics, individual_radius_subtopics)
rounded_main_topic_coords = round_coordinates(main_topic_coords)
rounded_subtopic_coords = round_coordinates(subtopic_coords)

# Print the rounded coordinates
print("Rounded Main Topic Coordinates:")
for coord in rounded_main_topic_coords:
    print(coord)

print("\nRounded Subtopic Coordinates:")
for coord in rounded_subtopic_coords:
    print(coord)

print(generate_gephi_gdf(topics_and_subtopics,rounded_main_topic_coords,rounded_subtopic_coords,individual_radius_main_topics,individual_radius_subtopics))
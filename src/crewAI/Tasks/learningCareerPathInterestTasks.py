from crewai import Task
from src.crewAI.Agents.learningCareerPathInterestAgents import *

# Initial survey and data collection tasks
initiate_career_survey = Task(
    name="Initiate Career Interest Survey",
    description=(
        "Welcome the user warmly and introduce the career path interest assessment process. "
        "Explain that this will help them discover career paths that align with their interests, values, and skills. "
        "Present a brief overview of what the assessment will cover: interests, skills, values, and work preferences. "
        "Ask if they're ready to begin the career exploration journey."
    ),
    expected_output="User readiness confirmation and survey initiation.",
    agent=career_path_interest_survey_agent,
    human_input=True
)

generate_career_survey = Task(
    name="Generate Career Interest Survey",
    description=(
        "Create a comprehensive career interest survey with questions covering: "
        "1. Personal interests and hobbies "
        "2. Preferred work environment and culture "
        "3. Skills and strengths "
        "4. Values and priorities "
        "5. Work-life balance preferences "
        "6. Long-term career goals "
        "Make the survey engaging and easy to understand."
    ),
    expected_output="Complete career interest survey with 15-20 well-structured questions.",
    context=[initiate_career_survey],
    agent=career_path_interest_survey_agent,
    human_input=False
)

conduct_adaptive_questioning = Task(
    name="Conduct Adaptive Career Questioning",
    description=(
        "Based on the survey responses, conduct a dynamic questioning session to explore career interests in depth. "
        "Ask follow-up questions to clarify responses, explore specific interests, and uncover hidden career aspirations. "
        "Adapt questions based on previous responses to get deeper insights into career preferences."
    ),
    expected_output="Detailed career interest profile with clarified preferences and aspirations.",
    context=[initiate_career_survey, generate_career_survey],
    agent=career_path_interest_questioning_agent,
    human_input=True
)

# Data retrieval and analysis tasks
retrieve_career_data = Task(
    name="Retrieve Career Market Data",
    description=(
        "Gather comprehensive data about potential career paths including: "
        "1. Job market trends and growth projections "
        "2. Salary ranges and compensation packages "
        "3. Required education and certifications "
        "4. Skills and competencies needed "
        "5. Work environment and culture "
        "6. Career advancement opportunities "
        "Focus on careers that align with the user's identified interests."
    ),
    expected_output="Comprehensive career data for relevant career paths.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning],
    agent=career_path_interest_data_agent,
    human_input=False
)

analyze_career_trends = Task(
    name="Analyze Career Trends and Performance",
    description=(
        "Analyze the retrieved career data to identify: "
        "1. Market trends and future outlook for relevant careers "
        "2. Performance indicators and success factors "
        "3. Emerging opportunities and new career paths "
        "4. Potential challenges and risks "
        "5. Geographic and industry variations "
        "Provide insights on career sustainability and growth potential."
    ),
    expected_output="Trend analysis report with career viability assessment.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning, retrieve_career_data],
    agent=career_path_interest_analysis_agent,
    human_input=False
)

# Career matching and generation tasks
match_career_paths = Task(
    name="Match Interests to Career Paths",
    description=(
        "Analyze the user's interests, skills, values, and preferences to match them with suitable career paths. "
        "Consider factors such as: "
        "1. Interest alignment with job responsibilities "
        "2. Skill compatibility and development potential "
        "3. Value congruence with work environment "
        "4. Lifestyle compatibility "
        "5. Growth and advancement opportunities "
        "Provide 3-5 well-matched career recommendations with detailed explanations."
    ),
    expected_output="Ranked list of 3-5 career path recommendations with detailed matching rationale.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning, retrieve_career_data, analyze_career_trends],
    agent=career_path_interest_matching_agent,
    human_input=False
)

extract_competencies = Task(
    name="Extract Required Competencies",
    description=(
        "For each recommended career path, identify and analyze the required competencies including: "
        "1. Technical skills and knowledge "
        "2. Soft skills and interpersonal abilities "
        "3. Educational requirements and certifications "
        "4. Experience levels and progression "
        "5. Industry-specific competencies "
        "Map these competencies to the user's current profile and identify development areas."
    ),
    expected_output="Detailed competency analysis for each recommended career path with skill gap assessment.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning, retrieve_career_data, analyze_career_trends, match_career_paths],
    agent=career_path_interest_competency_agent,
    human_input=False
)

generate_career_plan = Task(
    name="Generate Career Development Plan",
    description=(
        "Create a comprehensive career development plan for the top recommended career path including: "
        "1. Short-term goals (6 months to 1 year) "
        "2. Medium-term objectives (1-3 years) "
        "3. Long-term career vision (3-5 years) "
        "4. Specific action steps and milestones "
        "5. Required education, training, and certifications "
        "6. Networking and professional development activities "
        "7. Timeline and priority recommendations "
        "Make the plan actionable and realistic."
    ),
    expected_output="Comprehensive career development plan with actionable steps and timeline.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning, retrieve_career_data, analyze_career_trends, match_career_paths, extract_competencies],
    agent=career_path_interest_generation_agent,
    human_input=False
)

# Visualization and presentation tasks
create_career_visualization = Task(
    name="Create Career Visualization",
    description=(
        "Create clear and engaging visual representations of the career analysis including: "
        "1. Career path comparison charts "
        "2. Skill competency matrices "
        "3. Career progression timelines "
        "4. Interest-career alignment diagrams "
        "5. Development roadmap visualizations "
        "Present the information in an easy-to-understand format that highlights key insights."
    ),
    expected_output="Visual career analysis presentation with charts, diagrams, and clear explanations.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning, retrieve_career_data, analyze_career_trends, match_career_paths, extract_competencies, generate_career_plan],
    agent=career_path_interest_visualization_agent,
    human_input=False
)

# Learning and progress tracking tasks
update_learner_profile = Task(
    name="Update Career Learning Profile",
    description=(
        "Update the user's career learning profile with: "
        "1. Identified career interests and preferences "
        "2. Recommended career paths and rationale "
        "3. Competency assessments and skill gaps "
        "4. Career development plan and progress tracking "
        "5. Learning preferences and career exploration patterns "
        "6. Future career guidance recommendations "
        "Maintain this profile for ongoing career development support."
    ),
    expected_output="Updated career learning profile with comprehensive career exploration data.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning, retrieve_career_data, analyze_career_trends, match_career_paths, extract_competencies, generate_career_plan, create_career_visualization],
    agent=career_path_interest_learner_agent,
    human_input=False
)

# Final presentation and summary task
present_career_summary = Task(
    name="Present Career Path Summary",
    description=(
        "Present a comprehensive summary of the career path interest assessment including: "
        "1. Key findings about career interests and preferences "
        "2. Top career recommendations with detailed explanations "
        "3. Career development plan and next steps "
        "4. Competency analysis and skill development areas "
        "5. Market insights and career viability assessment "
        "6. Visual representations and supporting materials "
        "Provide actionable next steps and encourage continued career exploration."
    ),
    expected_output="Comprehensive career path interest assessment summary with actionable recommendations.",
    context=[initiate_career_survey, generate_career_survey, conduct_adaptive_questioning, retrieve_career_data, analyze_career_trends, match_career_paths, extract_competencies, generate_career_plan, create_career_visualization, update_learner_profile],
    agent=career_path_interest_matching_agent,
    human_input=True
) 
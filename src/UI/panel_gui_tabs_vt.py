import autogen
import panel as pn
import os
import time
import asyncio
from typing import List, Dict
import logging
from src import globals
from src.FSMs.fsm_career_path_interest import CareerFSM  # Updated FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat_vt import ReactiveChat
from src.UI.avatar import avatar
from enum import Enum
from dotenv import load_dotenv
from src.FSMs.fsm_career_path_interest import CareerFSM


load_dotenv()

logging.basicConfig(level=logging.INFO, 
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

###############################################
# ChatGPT Model
###############################################

gpt4_config_list = [{'model': "gpt-4o"}]

temperature = 0
max_tokens = 1000
top_p = 0.5
frequency_penalty = 0.1
presence_penalty = 0.1
seed = 53

gpt4_config = {
    "config_list": gpt4_config_list, 
    "temperature": temperature,
    "max_tokens": max_tokens,
    "top_p": top_p,
    "seed": seed
}

llm = gpt4_config

#################################################
# Define Agents
#################################################
from src.Agents.student_agent import StudentAgent
from src.Agents.career_growth_agent import CareerGrowthAgent
from src.Agents.certification_recommendation_agent import CertificationRecommendationAgent
from src.Agents.job_finder_agent import JobFinderAgent
from src.Agents.competency_extraction_agent import CompetencyExtractionAgent
from src.Agents.gap_analysis_agent import GapAnalysisAgent
from src.Agents.personalized_learning_plan_agent import PersonalizedLearningPlanAgent
from src.Agents.resource_ranking_agent import ResourceRankingAgent
from src.Agents.learner_model_agent import LearnerModelAgent
from src.Agents.user_preference_update_agent import UserPreferenceUpdateAgent
from src.Agents.realtime_career_adjustment_agent import RealTimeCareerAdjustmentAgent
from src.Agents.recommendation_testing_agent import RecommendationTestingAgent
from src.Agents.state_definition_agent import StateDefinitionAgent
from src.Agents.state_transition_agent import StateTransitionAgent
from src.Agents.data_sync_agent import DataSynchronizationAgent
from src.Agents.state_machine_test_agent import StateMachineTestingAgent
from src.Agents.agents import AgentKeys
from src.Agents.ai_evaluation_agent import AIEvaluationAgent
from src.Agents.scenario_simulation_agent import ScenarioSimulationAgent
from src.Agents.dynamic_recommendation_testing_agent import DynamicRecommendationTestingAgent


# Instantiate agents
student = StudentAgent(llm_config=llm)
career_growth = CareerGrowthAgent(llm_config=llm)
cert_recommendation = CertificationRecommendationAgent(llm_config=llm)
job_finder = JobFinderAgent(llm_config=llm)
competency_extractor = CompetencyExtractionAgent(llm_config=llm)
gap_analyzer = GapAnalysisAgent(llm_config=llm)
personalized_plan = PersonalizedLearningPlanAgent(llm_config=llm)
learner_model = LearnerModelAgent(llm_config=llm)
resource_ranking = ResourceRankingAgent(llm_config=llm)
user_pref_update = UserPreferenceUpdateAgent(llm_config=llm)
career_adjustment = RealTimeCareerAdjustmentAgent(llm_config=llm)
recommendation_testing = RecommendationTestingAgent(llm_config=llm)
competency_extractor = CompetencyExtractionAgent(llm_config=llm)
state_definition = StateDefinitionAgent(llm_config=llm)
state_transition = StateTransitionAgent(llm_config=llm)
data_sync = DataSynchronizationAgent(llm_config=llm)
state_machine_tester = StateMachineTestingAgent(llm_config=llm)
ai_evaluation = AIEvaluationAgent(llm_config=llm)
scenario_simulation = ScenarioSimulationAgent(llm_config=llm)
dynamic_testing = DynamicRecommendationTestingAgent(llm_config=llm)



agents_dict = {
    AgentKeys.STUDENT.value: student,
    AgentKeys.CAREER_GROWTH.value: career_growth,
    AgentKeys.CERTIFICATION_RECOMMENDATION.value: cert_recommendation,
    AgentKeys.JOB_FINDER.value: job_finder,
    AgentKeys.COMPETENCY_EXTRACTION.value: competency_extractor,
    AgentKeys.GAP_ANALYSIS.value: gap_analyzer,
    AgentKeys.PERSONALIZED_PLAN.value: personalized_plan,
    AgentKeys.LEARNER_MODEL.value: learner_model,
    AgentKeys.RESOURCE_RANKING.value: resource_ranking,
    AgentKeys.USER_PREF_UPDATE.value: user_pref_update,
    AgentKeys.REALTIME_CAREER_ADJUSTMENT.value: career_adjustment,
    AgentKeys.RECOMMENDATION_TESTING.value: recommendation_testing,
    AgentKeys.STATE_DEFINITION.value: state_definition,
    AgentKeys.STATE_TRANSITION.value: state_transition,
    AgentKeys.DATA_SYNC.value: data_sync,
    AgentKeys.STATE_MACHINE_TESTING.value: state_machine_tester,
    AgentKeys.AI_EVALUATION.value: ai_evaluation,
    AgentKeys.SCENARIO_SIMULATION.value: scenario_simulation,
    AgentKeys.DYNAMIC_RECOMMENDATION_TESTING.value: dynamic_testing,
}

agents_dict_by_name = {agent.name: agent for agent in agents_dict.values()}

avatars = {
    student.name: "✏️",  
    career_growth.name: "🚀",
    cert_recommendation.name: "🎓",
    job_finder.name: "🎯",
    competency_extractor.name: "📌",
    gap_analyzer.name: "⚖️",
    personalized_plan.name: "📘",
    learner_model.name: "🧠",
    resource_ranking.name: "⭐",
    user_pref_update.name: "🧭",
    career_adjustment.name: "🔁",
    recommendation_testing.name: "🧪",
    state_definition.name: "🧾",
    state_transition.name: "🔄",
    data_sync.name: "🔗",
    state_machine_tester.name: "🧪",
    ai_evaluation.name: "🧠",
    scenario_simulation.name: "🧬",
    dynamic_testing.name: "🔁",
}

##############################################
# Main Adaptive Learning Application
############################################## 
globals.input_future = None
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

fsm = CareerFSM(agents_dict)  # Updated FSM

groupchat = CustomGroupChat(
    agents=list(agents_dict.values()), 
    messages=[],
    max_round=globals.MAX_ROUNDS,
    send_introductions=True,
    speaker_selection_method=fsm.next_speaker_selector
)

agents_dict_by_name = {agent.name: agent for agent in agents_dict.values()}

manager = CustomGroupChatManager(
    groupchat=groupchat,
    filename=progress_file_path, 
    is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0,
    agents_dict_by_name=agents_dict_by_name
)    

fsm.register_groupchat_manager(manager)

# Begin GUI components
reactive_chat = ReactiveChat(agents_dict=agents_dict, avatars=avatars, groupchat_manager=manager)

# Register groupchat_manager and reactive_chat with agents
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat

    if hasattr(agent, "autogen_reply_func"):
        agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})


# Load chat history on startup
manager.get_chat_history_and_initialize_chat(filename=progress_file_path, chat_interface=reactive_chat.learn_tab_interface)
reactive_chat.update_dashboard()  # Call after history is loaded


##############################################
# UI Handlers
##############################################

# Career Progression Plan
async def handle_button_career_progress(event=None):
    """
    Request a career progression plan from Career Growth Agent.
    """
    await a_get_career_progress()

async def a_get_career_progress():
    """
    Ask the Career Growth Agent to generate a step-by-step career plan.
    """
    await career_growth.a_send("Generate a career progression plan for the student.", recipient=career_growth, request_reply=True)

    response = career_growth.last_message(agent=career_growth)["content"]
    
    reactive_chat.model_tab_interface.send(response, user=career_growth.name, avatar=avatars[career_growth.name])

# Certification Recommendations
async def handle_button_cert_recommendations(event=None):
    """
    Request certification recommendations from Certification Recommendation Agent.
    """
    await a_get_cert_recommendations()

async def a_get_cert_recommendations():
    """
    Ask the Certification Recommendation Agent to provide certification suggestions.
    """
    await cert_recommendation.a_send("Provide certification recommendations for the student.", recipient=cert_recommendation, request_reply=True)

    response = cert_recommendation.last_message(agent=cert_recommendation)["content"]
    
    reactive_chat.model_tab_interface.send(response, user=cert_recommendation.name, avatar=avatars[cert_recommendation.name])

# Job Finder
async def handle_find_jobs(event=None):
    """
    Request job recommendations from ChatGPT through JobFinderAgent.
    """
    await a_find_jobs()

async def a_find_jobs():
    """
    Get real-time job suggestions based on student capabilities.
    """
    await job_finder.a_send("Provide job recommendations for the student.", recipient=job_finder, request_reply=True)

    response = job_finder.last_message(agent=job_finder)["content"]
    
    reactive_chat.model_tab_interface.send(response, user=job_finder.name, avatar=avatars[job_finder.name])

async def handle_competency_extraction(event=None):
    await competency_extractor.a_send("Retrieve required competencies for selected career path.",
        recipient=competency_extractor, request_reply=True)
    response = competency_extractor.last_message(agent=competency_extractor)["content"]
    reactive_chat.model_tab_interface.send(response, user=competency_extractor.name, avatar=avatars[competency_extractor.name])

async def handle_gap_analysis(event=None):
    await gap_analyzer.a_send("Compare student's skills with industry requirements and find gaps.",
        recipient=gap_analyzer, request_reply=True)
    response = gap_analyzer.last_message(agent=gap_analyzer)["content"]
    reactive_chat.model_tab_interface.send(response, user=gap_analyzer.name, avatar=avatars[gap_analyzer.name])

async def handle_personalized_plan(event=None):
    await personalized_plan.a_send("Create a personalized learning plan: suggest courses, books, and exercises.",
        recipient=personalized_plan, request_reply=True)
    response = personalized_plan.last_message(agent=personalized_plan)["content"]
    reactive_chat.model_tab_interface.send(response, user=personalized_plan.name, avatar=avatars[personalized_plan.name])

async def handle_resource_ranking(event=None):
    await resource_ranking.a_send("Rank the most effective resources based on student goals and skill level.",
        recipient=resource_ranking, request_reply=True)
    response = resource_ranking.last_message(agent=resource_ranking)["content"]
    reactive_chat.model_tab_interface.send(response, user=resource_ranking.name, avatar=avatars[resource_ranking.name])

async def handle_update_interests(event=None):
    await user_pref_update.a_send("Student updated interests. Refresh recommendations.", recipient=user_pref_update, request_reply=True)
    response = user_pref_update.last_message(agent=user_pref_update)["content"]
    reactive_chat.model_tab_interface.send(response, user=user_pref_update.name, avatar=avatars[user_pref_update.name])
    reactive_chat.last_agent = user_pref_update

async def handle_adjust_recommendations(event=None):
    await career_adjustment.a_send("Revise career suggestions based on new student preferences.", recipient=career_adjustment, request_reply=True)
    response = career_adjustment.last_message(agent=career_adjustment)["content"]
    reactive_chat.model_tab_interface.send(response, user=career_adjustment.name, avatar=avatars[career_adjustment.name])

async def handle_test_recommendations(event=None):
    await recommendation_testing.a_send("Simulate behavior to test recommendation accuracy.", recipient=recommendation_testing, request_reply=True)
    response = recommendation_testing.last_message(agent=recommendation_testing)["content"]
    reactive_chat.model_tab_interface.send(response, user=recommendation_testing.name, avatar=avatars[recommendation_testing.name])

async def handle_state_definition(event=None):
    await state_definition.a_send("Define the career progression states and transitions.", recipient=state_definition, request_reply=True)
    response = state_definition.last_message(agent=state_definition)["content"]
    reactive_chat.model_tab_interface.send(response, user=state_definition.name, avatar=avatars[state_definition.name])

async def handle_state_transition(event=None):
    await state_transition.a_send("Trigger a state transition based on current learner progress.", recipient=state_transition, request_reply=True)
    response = state_transition.last_message(agent=state_transition)["content"]
    reactive_chat.model_tab_interface.send(response, user=state_transition.name, avatar=avatars[state_transition.name])

async def handle_data_sync(event=None):
    await data_sync.a_send("Sync updated career state with learner model and dashboard.", recipient=data_sync, request_reply=True)
    response = data_sync.last_message(agent=data_sync)["content"]
    reactive_chat.model_tab_interface.send(response, user=data_sync.name, avatar=avatars[data_sync.name])

async def handle_test_state_machine(event=None):
    await state_machine_tester.a_send("Test state transitions for correctness and stability.", recipient=state_machine_tester, request_reply=True)
    response = state_machine_tester.last_message(agent=state_machine_tester)["content"]
    reactive_chat.model_tab_interface.send(response, user=state_machine_tester.name, avatar=avatars[state_machine_tester.name])

async def handle_ai_evaluation(event=None):
    await ai_evaluation.a_send("Evaluate how well the recommendations match student input and real-world trends.", recipient=ai_evaluation, request_reply=True)
    response = ai_evaluation.last_message(agent=ai_evaluation)["content"]
    reactive_chat.model_tab_interface.send(response, user=ai_evaluation.name, avatar=avatars[ai_evaluation.name])

async def handle_scenario_simulation(event=None):
    await scenario_simulation.a_send("Simulate diverse student profiles to stress-test the system.", recipient=scenario_simulation, request_reply=True)
    response = scenario_simulation.last_message(agent=scenario_simulation)["content"]
    reactive_chat.model_tab_interface.send(response, user=scenario_simulation.name, avatar=avatars[scenario_simulation.name])

async def handle_dynamic_testing(event=None):
    await dynamic_testing.a_send("Test system's responsiveness to evolving student interests and skills.", recipient=dynamic_testing, request_reply=True)
    response = dynamic_testing.last_message(agent=dynamic_testing)["content"]
    reactive_chat.model_tab_interface.send(response, user=dynamic_testing.name, avatar=avatars[dynamic_testing.name])



##############################################
# Panel UI Setup
############################################## 

# --- Add UI Buttons ---
reactive_chat.button_career_progress = pn.widgets.Button(
    name="Get Career Progression Plan", button_type="primary"
)
reactive_chat.button_career_progress.on_click(handle_button_career_progress)

reactive_chat.button_cert_recommendations = pn.widgets.Button(
    name="Get Certification Suggestions", button_type="primary"
)
reactive_chat.button_cert_recommendations.on_click(handle_button_cert_recommendations)

reactive_chat.button_find_jobs = pn.widgets.Button(
    name="Find Jobs", button_type="primary"
)
reactive_chat.button_find_jobs.on_click(handle_find_jobs)

reactive_chat.button_competency = pn.widgets.Button(name="Get Competencies", button_type="primary")
reactive_chat.button_gap_analysis = pn.widgets.Button(name="Run Gap Analysis", button_type="primary")
reactive_chat.button_study_plan = pn.widgets.Button(name="Generate Study Plan", button_type="primary")
reactive_chat.button_rank_resources = pn.widgets.Button(name="Rank Resources", button_type="primary")

reactive_chat.button_competency.on_click(handle_competency_extraction)
reactive_chat.button_gap_analysis.on_click(handle_gap_analysis)
reactive_chat.button_study_plan.on_click(handle_personalized_plan)
reactive_chat.button_rank_resources.on_click(handle_resource_ranking)

reactive_chat.button_update_interests = pn.widgets.Button(name="Update Interests", button_type="primary")
reactive_chat.button_adjust_recommendations = pn.widgets.Button(name="Adjust Career Suggestions", button_type="primary")
reactive_chat.button_test_recommendations = pn.widgets.Button(name="Test Recommendation Adaptability", button_type="primary")

reactive_chat.button_update_interests.on_click(handle_update_interests)
reactive_chat.button_adjust_recommendations.on_click(handle_adjust_recommendations)
reactive_chat.button_test_recommendations.on_click(handle_test_recommendations)

reactive_chat.button_define_states = pn.widgets.Button(name="Define States", button_type="primary")
reactive_chat.button_trigger_transition = pn.widgets.Button(name="Trigger State Transition", button_type="primary")
reactive_chat.button_sync_data = pn.widgets.Button(name="Sync Career Data", button_type="primary")
reactive_chat.button_test_state_machine = pn.widgets.Button(name="Test State Machine", button_type="primary")

reactive_chat.button_define_states.on_click(handle_state_definition)
reactive_chat.button_trigger_transition.on_click(handle_state_transition)
reactive_chat.button_sync_data.on_click(handle_data_sync)
reactive_chat.button_test_state_machine.on_click(handle_test_state_machine)

reactive_chat.button_ai_eval = pn.widgets.Button(name="Run AI Evaluation", button_type="primary")
reactive_chat.button_simulate_scenarios = pn.widgets.Button(name="Simulate Scenarios", button_type="primary")
reactive_chat.button_dynamic_test = pn.widgets.Button(name="Test Dynamic Updates", button_type="primary")

reactive_chat.button_ai_eval.on_click(handle_ai_evaluation)
reactive_chat.button_simulate_scenarios.on_click(handle_scenario_simulation)
reactive_chat.button_dynamic_test.on_click(handle_dynamic_testing)




study_tab = (
    "Study Assist",
    pn.Column(
        pn.Row(reactive_chat.button_competency),
        pn.Row(reactive_chat.button_gap_analysis),
        pn.Row(reactive_chat.button_study_plan),
        pn.Row(reactive_chat.button_rank_resources),
        pn.Row(reactive_chat.model_tab_interface)
    )
)

# --- Career Progression Tab ---
career_progression_tab = (
    "Career Progression", 
    pn.Column(
        pn.Row(reactive_chat.button_career_progress),
        pn.Row(reactive_chat.button_cert_recommendations),
        pn.Row(reactive_chat.model_tab_interface)
    )
)

# --- Career Finder Tab ---
career_finder_tab = (
    "Career Finder", 
    pn.Column(
        pn.Row(reactive_chat.button_find_jobs),
        pn.Row(reactive_chat.model_tab_interface)
    )
)

interest_tab = (
    "Dynamic Interests", 
    pn.Column(
        pn.Row(reactive_chat.button_update_interests),
        pn.Row(reactive_chat.button_adjust_recommendations),
        pn.Row(reactive_chat.button_test_recommendations),
        pn.Row(reactive_chat.model_tab_interface)
    )
)

career_state_tab = (
    "Career State Machine", 
    pn.Column(
        pn.Row(reactive_chat.button_define_states),
        pn.Row(reactive_chat.button_trigger_transition),
        pn.Row(reactive_chat.button_sync_data),
        pn.Row(reactive_chat.button_test_state_machine),
        pn.Row(reactive_chat.model_tab_interface)
    )
)

evaluation_tab = (
    "AI Testing", 
    pn.Column(
        pn.Row(reactive_chat.button_ai_eval),
        pn.Row(reactive_chat.button_simulate_scenarios),
        pn.Row(reactive_chat.button_dynamic_test),
        pn.Row(reactive_chat.model_tab_interface)
    )
)




# Create Panel UI
def create_app():
    return pn.Tabs(
        career_progression_tab,
        career_finder_tab,
        study_tab,
        interest_tab,
        career_state_tab,
        evaluation_tab
    )


if __name__ == "__main__":
    app = create_app()
    pn.serve(app, callback_exception="verbose")

career_tab = (
    "Career",
    create_app()
)
    

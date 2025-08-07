from crewai import Crew, Process
from src.crewAI.Tasks.learningCareerPathInterestTasks import *
from src.crewAI.Agents.learningCareerPathInterestAgents import *
from langchain_openai import ChatOpenAI
import os
from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin
import time
import traceback
import re
from crewai.utilities.events.task_events import TaskStartedEvent, TaskCompletedEvent, TaskFailedEvent
from crewai.utilities.events.crew_events import CrewKickoffCompletedEvent, CrewKickoffStartedEvent
from crewai.utilities.events.llm_events import LLMCallStartedEvent, LLMCallCompletedEvent
from crewai.utilities.events import crewai_event_bus
from src.crewAI.utils import Colors
import asyncio
from src.crewAI import globals
from queue import Queue
import json

# Career path interest-specific avatars for the UI
career_path_interest_avatars = {
    "student": "👤",                                    # User
    "CareerInterestSurveyAgent": "��",                  # Clipboard for survey generation
    "AdaptiveQuestioningAgent": "🔍",                   # Magnifying glass for questioning
    "AICareerMatchingAgent": "🎯",                      # Target for career matching
    "AutogenDataRetrievalAgent": "��",                  # Chart for data retrieval
    "PerformanceTrendAnalysisAgent": "📈",              # Trending chart for analysis
    "AutogenCareerGenerationAgent": "🛠️",              # Tools for career generation
    "AIVisualizationAgent": "🎨",                       # Paint palette for visualization
    "CompetencyExtractionAgent": "��",                  # Brain for competency analysis
    "LearnerModelAgent": "📚",                          # Books for learner tracking
}

# Mapping task names to agent names for career path interest
career_path_interest_task_name_to_agent_name = {
    "Initiate Career Interest Survey": "CareerInterestSurveyAgent",
    "Generate Career Interest Survey": "CareerInterestSurveyAgent",
    "Conduct Adaptive Career Questioning": "AdaptiveQuestioningAgent",
    "Retrieve Career Market Data": "AutogenDataRetrievalAgent",
    "Analyze Career Trends and Performance": "PerformanceTrendAnalysisAgent",
    "Match Interests to Career Paths": "AICareerMatchingAgent",
    "Extract Required Competencies": "CompetencyExtractionAgent",
    "Generate Career Development Plan": "AutogenCareerGenerationAgent",
    "Create Career Visualization": "AIVisualizationAgent",
    "Update Career Learning Profile": "LearnerModelAgent",
    "Present Career Path Summary": "AICareerMatchingAgent",
}

def initialize_career_path_interest_task_events(learn_career_path_interest_manager_instance):
    print(f"{Colors.HEADER}========================= Initializing Career Path Interest Task Events ========================={Colors.ENDC}")
    
    @crewai_event_bus.on(TaskStartedEvent)
    def on_task_started(source, event: TaskStartedEvent):
        print(f"{Colors.CYAN}[EVENT] Task Started:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        learn_career_path_interest_manager_instance.currentTask = event.task.name
        print(f"{Colors.INFO}        Current Task Set To: {Colors.BOLD}{learn_career_path_interest_manager_instance.currentTask}{Colors.ENDC}")

    @crewai_event_bus.on(TaskCompletedEvent)
    def on_task_completed(source, event: TaskCompletedEvent):
        print(f"{Colors.GREEN}[EVENT] Task Completed:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        agent_executor = event.task.agent.agent_executor
        print(f"=============json.dumps(agent_executor.messages, indent=4, default=str)", json.dumps(agent_executor.messages, indent=4, default=str))
        # Truncate long outputs for cleaner logging
        output_summary = (event.output.raw[:100] + '...') if event.output and event.output.raw and len(event.output.raw) > 100 else (event.output.raw if event.output else "No output")
        print(f"{Colors.INFO}        Output: {output_summary}{Colors.ENDC}")
        print(f"{Colors.DEBUG}        Source: {source}, Full Event: {event}{Colors.ENDC}")

    @crewai_event_bus.on(CrewKickoffCompletedEvent)
    def on_crew_kickoff_completed(source, event: CrewKickoffCompletedEvent):
        print(f"=========================Messages========================={Colors.ENDC}", json.dumps(learn_career_path_interest_manager_instance.messages, indent=4, default=str))
        learn_career_path_interest_manager_instance.reactive_chat_instance.update_progress()
        globals.kickoff_initiated = None

    @crewai_event_bus.on(LLMCallCompletedEvent)
    def on_llm_call_completed(source, event: LLMCallCompletedEvent):
        if(learn_career_path_interest_manager_instance.reactive_chat_instance):
            learn_career_path_interest_manager_instance.reactive_chat_instance.update_dashboard()

    @crewai_event_bus.on(TaskFailedEvent)
    def on_task_failed(source, event: TaskFailedEvent):
        print(f"{Colors.RED}[EVENT] Task Failed:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        print(f"{Colors.DEBUG}        Source: {source}, Full Event: {event}{Colors.ENDC}")

# Career path interest-specific LLM response validation patterns
career_path_interest_llm_response_validation_at_human_feedback = {
    "Initiate Career Interest Survey": r"ready|begin|start",
    "Conduct Adaptive Career Questioning": r"interest|preference|skill|value",
    "Present Career Path Summary": r"summary|recommendation|plan"
}

def custom_career_path_interest_ask_human_input(self, final_answer: dict) -> str:
    print(f"\n{Colors.HEADER}---------- Waiting for Human Input ({learn_career_path_interest_manager_instance.currentTask}) ----------{Colors.ENDC}")
    print(f"{Colors.INFO}LLM's Final Answer/Request for Input:{Colors.ENDC}\n{final_answer}")

    pattern = career_path_interest_llm_response_validation_at_human_feedback.get(learn_career_path_interest_manager_instance.currentTask)
    if pattern:
        match = re.search(pattern, str(final_answer), re.IGNORECASE)
        if match:
            self.ask_for_human_input = False
            print(f"{Colors.GREEN}Input pattern matched. Auto-proceeding.{Colors.ENDC}")
            print(f"{Colors.HEADER}---------------------------------------------------------{Colors.ENDC}\n")
            return ""
        else:
            print(f"{Colors.WARNING}LLM output did not match expected pattern for auto-proceed.{Colors.ENDC}")
    else:
        print(f"{Colors.DEBUG}No specific input pattern to check for task: {learn_career_path_interest_manager_instance.currentTask}{Colors.ENDC}")
    
    print(f"{Colors.CYAN}------------------- User Input Required -------------------{Colors.ENDC}")
    print(f"{Colors.BOLD}Your response: {Colors.ENDC}")
    if reactivechat:
        reactivechat_instance.learn_tab_interface.send(final_answer, user=career_path_interest_task_name_to_agent_name[learn_career_path_interest_manager_instance.currentTask], avatar=career_path_interest_avatars[career_path_interest_task_name_to_agent_name[learn_career_path_interest_manager_instance.currentTask]], respond=False)
        message = {
            "role": career_path_interest_task_name_to_agent_name[learn_career_path_interest_manager_instance.currentTask],
            "content": final_answer
        }
        learn_career_path_interest_manager_instance.messages.append(message)
        learn_career_path_interest_manager_instance.messagesCount += 1
        print("====================== learn_career_path_interest_manager_instance.messages ======================  when asking for human input", learn_career_path_interest_manager_instance.messages)
        print("====================== learn_career_path_interest_manager_instance.messagesCount ======================", learn_career_path_interest_manager_instance.messagesCount)
        print("Waiting for user input from reactive chat-----------------------------------------------------------")
        while globals.input_future is None:
            print(f"{Colors.INFO}Waiting for user input...{Colors.ENDC}")
            time.sleep(1)
        input_str = globals.input_future
        globals.input_future = None
    else:
        input_str = input()
    print(f"{Colors.CYAN}---------------------------------------------------------{Colors.ENDC}")
    print(f"{Colors.INFO}You have entered: {Colors.BOLD}{input_str}{Colors.ENDC}")
    print(f"{Colors.HEADER}---------------------------------------------------------{Colors.ENDC}\n")
    message = {
        "role": "student",
        "content": input_str
    }
    learn_career_path_interest_manager_instance.messages.append(message)
    learn_career_path_interest_manager_instance.messagesCount += 1
    print("====================== learn_career_path_interest_manager_instance.messages ======================  after receiving human input", learn_career_path_interest_manager_instance.messages)
    print("====================== learn_career_path_interest_manager_instance.messagesCount ======================", learn_career_path_interest_manager_instance.messagesCount)
    return input_str

CrewAgentExecutorMixin._ask_human_input = custom_career_path_interest_ask_human_input

# Define your LLM config for career path interest learning
llm_config = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.environ.get("OPENAI_API_KEY")
)

def configure_career_path_interest_agents_with_llm(agent_list, llm_config):
    for agent in agent_list:
        agent.llm = llm_config

def career_path_interest_callback_function(output):
    print(f"""
        {Colors.HEADER}===================== CAREER PATH INTEREST TASK CALLBACK TRIGGERED ====================={Colors.ENDC}
        {Colors.INFO}Task Description:{Colors.ENDC} {Colors.BOLD}{output.description}{Colors.ENDC}
        {Colors.INFO}Task Raw Output:{Colors.ENDC}
        {output.raw}
        {Colors.HEADER}======================================================================{Colors.ENDC}
    """)
    if reactivechat:
        reactivechat_instance.learn_tab_interface.send(output.raw, user=career_path_interest_task_name_to_agent_name[learn_career_path_interest_manager_instance.currentTask], avatar=career_path_interest_avatars[career_path_interest_task_name_to_agent_name[learn_career_path_interest_manager_instance.currentTask]], respond=False)
        message = {
            "role": career_path_interest_task_name_to_agent_name[learn_career_path_interest_manager_instance.currentTask],
            "content": output.raw
        }
        learn_career_path_interest_manager_instance.messages.append(message)
        learn_career_path_interest_manager_instance.messagesCount += 1
        print("====================== learn_career_path_interest_manager_instance.messages ======================", learn_career_path_interest_manager_instance.messages)
        print("====================== learn_career_path_interest_manager_instance.messagesCount ======================", learn_career_path_interest_manager_instance.messagesCount)
    return output

def career_path_interest_step_callback(step):
    thought_summary = (step.thought[:150] + '...') if step.thought and len(step.thought) > 150 else step.thought
    output_summary = (step.output[:150] + '...') if step.output and len(step.output) > 150 else step.output
    text_summary = (step.text[:150] + '...') if step.text and len(step.text) > 150 else step.text

    print(f"""
        {Colors.GREEN}---------------------- CAREER PATH INTEREST AGENT STEP COMPLETED ----------------------{Colors.ENDC}
        {Colors.CYAN}Thought:{Colors.ENDC} {thought_summary}
        {Colors.CYAN}Output:{Colors.ENDC} {output_summary}
        {Colors.CYAN}Text:{Colors.ENDC} {text_summary}
        {Colors.GREEN}----------------------------------------------------------------------{Colors.ENDC}
    """)

career_path_interest_task_callback_handler = {
    "Initiate Career Interest Survey": career_path_interest_callback_function,
    "Generate Career Interest Survey": career_path_interest_callback_function,
    "Conduct Adaptive Career Questioning": career_path_interest_callback_function,
    "Retrieve Career Market Data": career_path_interest_callback_function,
    "Analyze Career Trends and Performance": career_path_interest_callback_function,
    "Match Interests to Career Paths": career_path_interest_callback_function,
    "Extract Required Competencies": career_path_interest_callback_function,
    "Generate Career Development Plan": career_path_interest_callback_function,
    "Create Career Visualization": career_path_interest_callback_function,
    "Update Career Learning Profile": career_path_interest_callback_function,
    "Present Career Path Summary": career_path_interest_callback_function,
}

# Career path interest agent list
career_path_interest_agent_list = [
    career_path_interest_survey_agent,
    career_path_interest_questioning_agent,
    career_path_interest_matching_agent,
    career_path_interest_data_agent,
    career_path_interest_analysis_agent,
    career_path_interest_generation_agent,
    career_path_interest_visualization_agent,
    career_path_interest_competency_agent,
    career_path_interest_learner_agent
]

class learn_career_path_interest_manager():
    def __init__(self, *args, **kwargs):
        self.reactive_chat = kwargs.get('reactive_chat')
        if self.reactive_chat:
            self.attach_reactive_chat(self.reactive_chat)
        self.crew = kwargs.get('crew')
        self.task_list = kwargs.get('task_list')
        self.agent_list = kwargs.get('agent_list')
        self.process = kwargs.get('process')
        self.max_iterations = kwargs.get('max_iterations')
        self.verbose = kwargs.get('verbose')
        self.currentCareerPath = None
        self.currentTask = None
        self.messagesCount = 0
        self.messages = []
        self.reactive_chat_instance = None
        initialize_career_path_interest_task_events(self)
    
    def kickoff(self, *args, **kwargs):
        self.crew.kickoff(*args, **kwargs)
        
    def attach_reactive_chat(self, reactive_chat):
        global reactivechat
        reactivechat = True
        global reactivechat_instance
        reactivechat_instance = reactive_chat
        self.reactive_chat_instance = reactive_chat

    def _invoke_loop(self):
        super()._invoke_loop()

# Career path interest task list - following the FSM workflow
career_path_interest_task_list = [
    initiate_career_survey,
    generate_career_survey,
    conduct_adaptive_questioning,
    retrieve_career_data,
    analyze_career_trends,
    match_career_paths,
    extract_competencies,
    generate_career_plan,
    create_career_visualization,
    update_learner_profile,
    present_career_summary
]

# Set callbacks for career path interest tasks
for task in career_path_interest_task_list:
    task.callback = career_path_interest_task_callback_handler.get(task.name)
    if task.callback is None:
        print(f"{Colors.WARNING}[WARNING] No callback handler found for task: {Colors.BOLD}{task.name}{Colors.ENDC}")

processType = Process.sequential

reactivechat = None
reactivechat_instance = None

career_path_interest_learning_crew = Crew(
    name="career_path_interest_learning_crew",
    agents=career_path_interest_agent_list,
    tasks=career_path_interest_task_list,
    verbose=True,
    max_iterations=15,  # Increased for the longer career assessment workflow
    process=processType,
    step_callback=career_path_interest_step_callback
)

learn_career_path_interest_manager_instance = learn_career_path_interest_manager(
    crew=career_path_interest_learning_crew, 
    task_list=career_path_interest_task_list, 
    agent_list=career_path_interest_agent_list, 
    process=processType, 
    max_iterations=15,  # Increased for the longer career assessment workflow
    verbose=True
)

if __name__ == "__main__":
    learn_career_path_interest_manager_instance.kickoff() 
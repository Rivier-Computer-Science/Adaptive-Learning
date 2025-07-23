from crewai import Crew, Process
from src.crewAI.Tasks.learningTeluguTasks import *
from src.crewAI.Agents.learningTeluguAgents import *
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

# Telugu-specific avatars for the UI
telugu_avatars = {
    "student": "✏️",                 # Pencil
    "TeluguTeacherAgent": "🧑‍🎓",     # Female teacher
    "TeluguTutorAgent": "👩‍🏫",       # Person with graduation hat
    "TeluguProblemGeneratorAgent": "📚",  # Stack of books for problem generation
    "TeluguSolutionVerifierAgent": "🔍",  # Magnifying glass for solution verification
    "TeluguLearnerModelAgent": "🧠",      # Brain emoji for learner model
    "TeluguLevelAdapterAgent": "📈",      # Chart with upwards trend for level adaptation
    "TeluguMotivatorAgent": "🏆",         # Trophy for motivation
}

# Mapping task names to agent names for Telugu
telugu_task_name_to_agent_name = {
    "Select Telugu Topic": "TeluguTeacherAgent",
    "Teach Telugu Topic": "TeluguTeacherAgent",
    "Generate Telugu Problem": "TeluguProblemGeneratorAgent",
    "Verify Telugu Problem": "TeluguSolutionVerifierAgent",
    "Update Telugu Learner Model": "TeluguLearnerModelAgent",
    "Adjust Telugu Difficulty Level": "TeluguLevelAdapterAgent",
    "Motivate Telugu Student": "TeluguMotivatorAgent",
}

def initialize_telugu_task_events(learn_telugu_manager_instance):
    print(f"{Colors.HEADER}========================= Initializing Telugu Task Events ========================={Colors.ENDC}")
    
    @crewai_event_bus.on(TaskStartedEvent)
    def on_task_started(source, event: TaskStartedEvent):
        print(f"{Colors.CYAN}[EVENT] Task Started:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        learn_telugu_manager_instance.currentTask = event.task.name
        print(f"{Colors.INFO}        Current Task Set To: {Colors.BOLD}{learn_telugu_manager_instance.currentTask}{Colors.ENDC}")

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
        print(f"=========================Messages========================={Colors.ENDC}", json.dumps(learn_telugu_manager_instance.messages, indent=4, default=str))
        learn_telugu_manager_instance.reactive_chat_instance.update_progress()
        globals.kickoff_initiated = None

    @crewai_event_bus.on(LLMCallCompletedEvent)
    def on_llm_call_completed(source, event: LLMCallCompletedEvent):
        if(learn_telugu_manager_instance.reactive_chat_instance):
            learn_telugu_manager_instance.reactive_chat_instance.update_dashboard()

    @crewai_event_bus.on(TaskFailedEvent)
    def on_task_failed(source, event: TaskFailedEvent):
        print(f"{Colors.RED}[EVENT] Task Failed:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        print(f"{Colors.DEBUG}        Source: {source}, Full Event: {event}{Colors.ENDC}")

# Telugu-specific LLM response validation patterns
telugu_llm_response_validation_at_human_feedback = {
    "Select Telugu Topic": r"Topic: (\w+)",
    "Verify Telugu Problem": r"Final_Evaluation: (\w+)"
}

def custom_telugu_ask_human_input(self, final_answer: dict) -> str:
    print(f"\n{Colors.HEADER}---------- Waiting for Human Input ({learn_telugu_manager_instance.currentTask}) ----------{Colors.ENDC}")
    print(f"{Colors.INFO}LLM's Final Answer/Request for Input:{Colors.ENDC}\n{final_answer}")

    pattern = telugu_llm_response_validation_at_human_feedback.get(learn_telugu_manager_instance.currentTask)
    if pattern:
        match = re.search(pattern, str(final_answer))
        if match:
            self.ask_for_human_input = False
            print(f"{Colors.GREEN}Input pattern matched. Auto-proceeding.{Colors.ENDC}")
            print(f"{Colors.HEADER}---------------------------------------------------------{Colors.ENDC}\n")
            return ""
        else:
            print(f"{Colors.WARNING}LLM output did not match expected pattern for auto-proceed.{Colors.ENDC}")
    else:
        print(f"{Colors.DEBUG}No specific input pattern to check for task: {learn_telugu_manager_instance.currentTask}{Colors.ENDC}")
    
    print(f"{Colors.CYAN}------------------- User Input Required -------------------{Colors.ENDC}")
    print(f"{Colors.BOLD}Your response: {Colors.ENDC}")
    if reactivechat:
        reactivechat_instance.learn_tab_interface.send(final_answer, user=telugu_task_name_to_agent_name[learn_telugu_manager_instance.currentTask], avatar=telugu_avatars[telugu_task_name_to_agent_name[learn_telugu_manager_instance.currentTask]], respond=False)
        message = {
            "role": telugu_task_name_to_agent_name[learn_telugu_manager_instance.currentTask],
            "content": final_answer
        }
        learn_telugu_manager_instance.messages.append(message)
        learn_telugu_manager_instance.messagesCount += 1
        print("====================== learn_telugu_manager_instance.messages ======================  when asking for human input", learn_telugu_manager_instance.messages)
        print("====================== learn_telugu_manager_instance.messagesCount ======================", learn_telugu_manager_instance.messagesCount)
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
    learn_telugu_manager_instance.messages.append(message)
    learn_telugu_manager_instance.messagesCount += 1
    print("====================== learn_telugu_manager_instance.messages ======================  after receiving human input", learn_telugu_manager_instance.messages)
    print("====================== learn_telugu_manager_instance.messagesCount ======================", learn_telugu_manager_instance.messagesCount)
    return input_str

CrewAgentExecutorMixin._ask_human_input = custom_telugu_ask_human_input

# Define your LLM config for Telugu learning
llm_config = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.environ.get("OPENAI_API_KEY")
)

def configure_telugu_agents_with_llm(agent_list, llm_config):
    for agent in agent_list:
        agent.llm = llm_config

def telugu_callback_function(output):
    print(f"""
        {Colors.HEADER}===================== TELUGU TASK CALLBACK TRIGGERED ====================={Colors.ENDC}
        {Colors.INFO}Task Description:{Colors.ENDC} {Colors.BOLD}{output.description}{Colors.ENDC}
        {Colors.INFO}Task Raw Output:{Colors.ENDC}
        {output.raw}
        {Colors.HEADER}======================================================================{Colors.ENDC}
    """)
    if reactivechat:
        reactivechat_instance.learn_tab_interface.send(output.raw, user=telugu_task_name_to_agent_name[learn_telugu_manager_instance.currentTask], avatar=telugu_avatars[telugu_task_name_to_agent_name[learn_telugu_manager_instance.currentTask]], respond=False)
        message = {
            "role": telugu_task_name_to_agent_name[learn_telugu_manager_instance.currentTask],
            "content": output.raw
        }
        learn_telugu_manager_instance.messages.append(message)
        learn_telugu_manager_instance.messagesCount += 1
        print("====================== learn_telugu_manager_instance.messages ======================", learn_telugu_manager_instance.messages)
        print("====================== learn_telugu_manager_instance.messagesCount ======================", learn_telugu_manager_instance.messagesCount)
    return output

def telugu_step_callback(step):
    thought_summary = (step.thought[:150] + '...') if step.thought and len(step.thought) > 150 else step.thought
    output_summary = (step.output[:150] + '...') if step.output and len(step.output) > 150 else step.output
    text_summary = (step.text[:150] + '...') if step.text and len(step.text) > 150 else step.text

    print(f"""
        {Colors.GREEN}---------------------- TELUGU AGENT STEP COMPLETED ----------------------{Colors.ENDC}
        {Colors.CYAN}Thought:{Colors.ENDC} {thought_summary}
        {Colors.CYAN}Output:{Colors.ENDC} {output_summary}
        {Colors.CYAN}Text:{Colors.ENDC} {text_summary}
        {Colors.GREEN}----------------------------------------------------------------------{Colors.ENDC}
    """)

telugu_task_callback_handler = {
    "Select Telugu Topic": telugu_callback_function,
    "Teach Telugu Topic": telugu_callback_function,
    "Generate Telugu Problem": telugu_callback_function,
    "Verify Telugu Problem": telugu_callback_function,
    "Update Telugu Learner Model": telugu_callback_function,
    "Adjust Telugu Difficulty Level": telugu_callback_function,
    "Motivate Telugu Student": telugu_callback_function,
}

# Telugu agent list
telugu_agent_list = [
    telugu_teacher,
    telugu_problem_gen,
    telugu_verifier,
    telugu_learner,
    telugu_level_adapter,
    telugu_motivator
]



class learn_telugu_manager():
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
        self.currentTopic = None
        self.currentTask = None
        self.messagesCount = 0
        self.messages = []
        self.reactive_chat_instance = None
        initialize_telugu_task_events(self)
    
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

# Telugu task list
telugu_task_list = [
    select_telugu_topic, 
    teach_telugu_topic, 
    generate_telugu_problem, 
    verify_telugu_problem, 
    update_telugu_learner_model, 
    adjust_telugu_difficulty_level, 
    motivate_telugu_student
]

# Set callbacks for Telugu tasks
for task in telugu_task_list:
    task.callback = telugu_task_callback_handler.get(task.name)
    if task.callback is None:
        print(f"{Colors.WARNING}[WARNING] No callback handler found for task: {Colors.BOLD}{task.name}{Colors.ENDC}")

processType = Process.sequential

reactivechat = None
reactivechat_instance = None

telugu_learning_crew = Crew(
    name="learning_crew",
    agents=telugu_agent_list,
    tasks=telugu_task_list,
    verbose=True,
    max_iterations=10,
    # manager_agent=crew_manager,
    # process=Process.hierarchical
    process=processType,
    step_callback=telugu_step_callback
)

learn_telugu_manager_instance = learn_telugu_manager(
    crew=telugu_learning_crew, 
    task_list=telugu_task_list, 
    agent_list=telugu_agent_list, 
    process=processType, 
    max_iterations=10, 
    verbose=True
)

if __name__ == "__main__":
    learn_telugu_manager_instance.kickoff()
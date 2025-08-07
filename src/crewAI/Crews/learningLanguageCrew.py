from crewai import Crew, Process
from src.crewAI.Tasks.learningLanguageTasks import *
from src.crewAI.Agents.learningLanguageAgents import *
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

# Language-specific avatars for the UI
language_avatars = {
    "student": "✏️",                 # Pencil
    "LanguageTeachingAgent": "🧑‍🎓",   # Female teacher
    "LanguageTutorAgent": "👨‍🏫",      # Person with graduation hat
    "LanguageProblemGeneratorAgent": "📚",  # Stack of books for problem generation
    "LanguageSolutionVerifierAgent": "🔍",  # Magnifying glass for solution verification
    "LanguageLearnerModelAgent": "🧠",      # Brain emoji for learner model
    "LanguageLevelAdapterAgent": "📈",      # Chart with upwards trend for level adaptation
    "LanguageMotivatorAgent": "🏆",         # Trophy for motivation
}

# Mapping task names to agent names for Language learning
language_task_name_to_agent_name = {
    "Select Language Topic": "LanguageTeachingAgent",
    "Present Language Lesson": "LanguageTeachingAgent",
    "Generate Language Problem": "LanguageProblemGeneratorAgent",
    "Await Student Answer": "LanguageStudentAgent",
    "Verify Language Answer": "LanguageSolutionVerifierAgent",
    "Update Language Learner Model": "LanguageLearnerModelAgent",
    "Adapt Language Difficulty Level": "LanguageLevelAdapterAgent",
    "Motivate Language Student": "LanguageMotivatorAgent",
    "Provide Language Tutoring": "LanguageTutorAgent",
}

def initialize_language_task_events(learn_language_manager_instance):
    print(f"{Colors.HEADER}========================= Initializing Language Task Events ========================={Colors.ENDC}")
    
    @crewai_event_bus.on(TaskStartedEvent)
    def on_task_started(source, event: TaskStartedEvent):
        print(f"{Colors.CYAN}[EVENT] Task Started:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        learn_language_manager_instance.currentTask = event.task.name
        print(f"{Colors.INFO}        Current Task Set To: {Colors.BOLD}{learn_language_manager_instance.currentTask}{Colors.ENDC}")

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
        print(f"=========================Messages========================={Colors.ENDC}", json.dumps(learn_language_manager_instance.messages, indent=4, default=str))
        learn_language_manager_instance.reactive_chat_instance.update_progress()
        globals.kickoff_initiated = None

    @crewai_event_bus.on(LLMCallCompletedEvent)
    def on_llm_call_completed(source, event: LLMCallCompletedEvent):
        if(learn_language_manager_instance.reactive_chat_instance):
            learn_language_manager_instance.reactive_chat_instance.update_dashboard()

    @crewai_event_bus.on(TaskFailedEvent)
    def on_task_failed(source, event: TaskFailedEvent):
        print(f"{Colors.RED}[EVENT] Task Failed:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        print(f"{Colors.DEBUG}        Source: {source}, Full Event: {event}{Colors.ENDC}")

# Language-specific LLM response validation patterns
language_llm_response_validation_at_human_feedback = {
    "Select Language Topic": r"Topic: (\w+)",
    "Verify Language Answer": r"Final_Evaluation: (\w+)"
}

def custom_language_ask_human_input(self, final_answer: dict) -> str:
    print(f"\n{Colors.HEADER}---------- Waiting for Human Input ({learn_language_manager_instance.currentTask}) ----------{Colors.ENDC}")
    print(f"{Colors.INFO}LLM's Final Answer/Request for Input:{Colors.ENDC}\n{final_answer}")

    pattern = language_llm_response_validation_at_human_feedback.get(learn_language_manager_instance.currentTask)
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
        print(f"{Colors.DEBUG}No specific input pattern to check for task: {learn_language_manager_instance.currentTask}{Colors.ENDC}")
    
    print(f"{Colors.CYAN}------------------- User Input Required -------------------{Colors.ENDC}")
    print(f"{Colors.BOLD}Your response: {Colors.ENDC}")
    if reactivechat:
        reactivechat_instance.learn_tab_interface.send(final_answer, user=language_task_name_to_agent_name[learn_language_manager_instance.currentTask], avatar=language_avatars[language_task_name_to_agent_name[learn_language_manager_instance.currentTask]], respond=False)
        message = {
            "role": language_task_name_to_agent_name[learn_language_manager_instance.currentTask],
            "content": final_answer
        }
        learn_language_manager_instance.messages.append(message)
        learn_language_manager_instance.messagesCount += 1
        print("====================== learn_language_manager_instance.messages ======================  when asking for human input", learn_language_manager_instance.messages)
        print("====================== learn_language_manager_instance.messagesCount ======================", learn_language_manager_instance.messagesCount)
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
    learn_language_manager_instance.messages.append(message)
    learn_language_manager_instance.messagesCount += 1
    print("====================== learn_language_manager_instance.messages ======================  after receiving human input", learn_language_manager_instance.messages)
    print("====================== learn_language_manager_instance.messagesCount ======================", learn_language_manager_instance.messagesCount)
    return input_str

CrewAgentExecutorMixin._ask_human_input = custom_language_ask_human_input

# Define your LLM config for Language learning
llm_config = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.environ.get("OPENAI_API_KEY")
)

# def configure_language_agents_with_llm(agent_list, llm_config):
#     for agent in agent_list:
#         agent.llm = llm_config

def language_callback_function(output):
    print(f"""
        {Colors.HEADER}===================== LANGUAGE TASK CALLBACK TRIGGERED ====================={Colors.ENDC}
        {Colors.INFO}Task Description:{Colors.ENDC} {Colors.BOLD}{output.description}{Colors.ENDC}
        {Colors.INFO}Task Raw Output:{Colors.ENDC}
        {output.raw}
        {Colors.HEADER}======================================================================{Colors.ENDC}
    """)
    if reactivechat:
        reactivechat_instance.learn_tab_interface.send(output.raw, user=language_task_name_to_agent_name[learn_language_manager_instance.currentTask], avatar=language_avatars[language_task_name_to_agent_name[learn_language_manager_instance.currentTask]], respond=False)
        message = {
            "role": language_task_name_to_agent_name[learn_language_manager_instance.currentTask],
            "content": output.raw
        }
        learn_language_manager_instance.messages.append(message)
        learn_language_manager_instance.messagesCount += 1
        print("====================== learn_language_manager_instance.messages ======================", learn_language_manager_instance.messages)
        print("====================== learn_language_manager_instance.messagesCount ======================", learn_language_manager_instance.messagesCount)
    return output

def language_step_callback(step):
    thought_summary = (step.thought[:150] + '...') if step.thought and len(step.thought) > 150 else step.thought
    output_summary = (step.output[:150] + '...') if step.output and len(step.output) > 150 else step.output
    text_summary = (step.text[:150] + '...') if step.text and len(step.text) > 150 else step.text

    print(f"""
        {Colors.GREEN}---------------------- LANGUAGE AGENT STEP COMPLETED ----------------------{Colors.ENDC}
        {Colors.CYAN}Thought:{Colors.ENDC} {thought_summary}
        {Colors.CYAN}Output:{Colors.ENDC} {output_summary}
        {Colors.CYAN}Text:{Colors.ENDC} {text_summary}
        {Colors.GREEN}----------------------------------------------------------------------{Colors.ENDC}
    """)

language_task_callback_handler = {
    "Select Language Topic": language_callback_function,
    "Present Language Lesson": language_callback_function,
    "Generate Language Problem": language_callback_function,
    "Await Student Answer": language_callback_function,
    "Verify Language Answer": language_callback_function,
    "Update Language Learner Model": language_callback_function,
    "Adapt Language Difficulty Level": language_callback_function,
    "Motivate Language Student": language_callback_function,
    "Provide Language Tutoring": language_callback_function,
}

# Language agent list
language_agent_list = [
    language_teacher,
    language_problem_gen,
    language_verifier,
    language_learner,
    language_level_adapter,
    language_motivator,
    language_tutor,
    language_student
]

class learn_language_manager():
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
        self.language = 'Telugu'    
        initialize_language_task_events(self)
    
    def kickoff(self, *args, **kwargs):
        additional_inputs = {
            "language": self.language,
        }

        kwargs.setdefault("inputs", {})
        kwargs["inputs"] = {**additional_inputs, **kwargs["inputs"]}

        return self.crew.kickoff(*args, **kwargs)
        
    def attach_reactive_chat(self, reactive_chat):
        global reactivechat
        reactivechat = True
        global reactivechat_instance
        reactivechat_instance = reactive_chat
        self.reactive_chat_instance = reactive_chat

    def _invoke_loop(self):
        super()._invoke_loop()

# Language task list
language_task_list = [
    select_language_topic, 
    present_language_lesson, 
    generate_language_problem, 
    await_student_answer,
    verify_language_answer, 
    update_language_learner_model, 
    adapt_language_difficulty_level, 
    motivate_language_student,
    provide_language_tutoring
]

# Set callbacks for Language tasks
for task in language_task_list:
    task.callback = language_task_callback_handler.get(task.name)
    if task.callback is None:
        print(f"{Colors.WARNING}[WARNING] No callback handler found for task: {Colors.BOLD}{task.name}{Colors.ENDC}")

processType = Process.sequential

reactivechat = None
reactivechat_instance = None

language_learning_crew = Crew(
    name="language_learning_crew",
    agents=language_agent_list,
    tasks=language_task_list,
    verbose=True,
    max_iterations=10,
    # manager_agent=crew_manager,
    # process=Process.hierarchical
    process=processType,
    step_callback=language_step_callback
)

learn_language_manager_instance = learn_language_manager(
    crew=language_learning_crew, 
    task_list=language_task_list, 
    agent_list=language_agent_list, 
    process=processType, 
    max_iterations=10, 
    verbose=True
)

if __name__ == "__main__":
    learn_language_manager_instance.kickoff() 
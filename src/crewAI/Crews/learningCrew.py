from crewai import Agent, Task, Crew, Process
from src.crewAI.Tasks.learningTasks import *
from src.crewAI.crewAgents import *
from langchain_openai import ChatOpenAI
import os
from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin
import time
import traceback
import re
from crewai.utilities.events.task_events import TaskStartedEvent, TaskCompletedEvent
from crewai.utilities.events import crewai_event_bus
from src.crewAI.utils import Colors


def initialize_task_events(learn_math_manager_instance):
    print(f"{Colors.HEADER}========================= Initializing Task Events ========================={Colors.ENDC}")
    @crewai_event_bus.on(TaskStartedEvent)
    def on_task_started(source, event: TaskStartedEvent):
        print(f"{Colors.CYAN}[EVENT] Task Started:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        # print(f"{Colors.DEBUG}        Source: {source}, Event Details: {event}{Colors.ENDC}")
        learn_math_manager_instance.currentTask = event.task.name
        print(f"{Colors.INFO}        Current Task Set To: {Colors.BOLD}{learn_math_manager_instance.currentTask}{Colors.ENDC}")

    @crewai_event_bus.on(TaskCompletedEvent)
    def on_task_completed(source, event: TaskCompletedEvent):
        print(f"{Colors.GREEN}[EVENT] Task Completed:{Colors.ENDC} {Colors.BOLD}{event.task.name}{Colors.ENDC}")
        # Truncate long outputs for cleaner logging, or handle as needed
        output_summary = (event.output.raw[:100] + '...') if event.output and event.output.raw and len(event.output.raw) > 100 else (event.output.raw if event.output else "No output")
        print(f"{Colors.INFO}        Output: {output_summary}{Colors.ENDC}")
        print(f"{Colors.DEBUG}        Source: {source}, Full Event: {event}{Colors.ENDC}")

llm_response_validation_at_human_feedback = {
    "Select Math Topic" :  r"Topic: (\w+)",
    "Solve Math Problem" : r"Student_Answer: (\w+)",
    "Verify Math Problem" : r"Evaluation: (\w+)"
}

def custom_ask_human_input(self, final_answer: dict) -> str:
    global user_input
    # prompt = self._i18n.slice("getting_input").format(final_answer=final_answer)
    # chat_interface.send(prompt, user="assistant", respond=False)
    print(f"\n{Colors.HEADER}---------- Waiting for Human Input ({learn_math_manager_instance.currentTask}) ----------{Colors.ENDC}")
    print(f"{Colors.INFO}LLM's Final Answer/Request for Input:{Colors.ENDC}\n{final_answer}")

    pattern = llm_response_validation_at_human_feedback.get(learn_math_manager_instance.currentTask)
    if pattern:
        match = re.search(pattern, str(final_answer)) # Ensure final_answer is a string for regex
        if match:
            self.ask_for_human_input = False
            print(f"{Colors.GREEN}Input pattern matched. Auto-proceeding.{Colors.ENDC}")
            print(f"{Colors.HEADER}---------------------------------------------------------{Colors.ENDC}\n")
            return ""
        else:
            print(f"{Colors.WARNING}LLM output did not match expected pattern for auto-proceed.{Colors.ENDC}")
    else:
        print(f"{Colors.DEBUG}No specific input pattern to check for task: {learn_math_manager_instance.currentTask}{Colors.ENDC}")
    
    print(f"{Colors.CYAN}------------------- User Input Required -------------------{Colors.ENDC}")
    print(f"{Colors.BOLD}Your response: {Colors.ENDC}")
    user_input_str = input()
    print(f"{Colors.CYAN}---------------------------------------------------------{Colors.ENDC}")
    # while user_input is None:
    #     time.sleep(1)  

    # human_comments = user_input
    # user_input = None
    print(f"{Colors.INFO}You have entered: {Colors.BOLD}{user_input_str}{Colors.ENDC}")
    print(f"{Colors.HEADER}---------------------------------------------------------{Colors.ENDC}\n")
    return user_input_str

CrewAgentExecutorMixin._ask_human_input = custom_ask_human_input

# Define your LLM config (e.g., OpenAI GPT-4 with temperature 0.7)
llm_config = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key= os.environ.get("OPENAI_API_KEY")
)

def configure_agents_with_llm(agent_list, llm_config):
    for agent in agent_list:
        agent.llm = llm_config


def callback_function(output):
    # Do something after the task is completed
    # Example: Send an email to the manager
    print(f"""
        {Colors.HEADER}===================== TASK CALLBACK TRIGGERED ====================={Colors.ENDC}
        {Colors.INFO}Task Description:{Colors.ENDC} {Colors.BOLD}{output.description}{Colors.ENDC}
        {Colors.INFO}Task Raw Output:{Colors.ENDC}
        {output.raw}
        {Colors.HEADER}======================================================================{Colors.ENDC}
    """)
    # traceback.print_exc()
    # print("Stack trace: callback_function")
    # traceback.print_stack()
    return output

def step_callback(step):
    thought_summary = (step.thought[:150] + '...') if step.thought and len(step.thought) > 150 else step.thought
    output_summary = (step.output[:150] + '...') if step.output and len(step.output) > 150 else step.output
    text_summary = (step.text[:150] + '...') if step.text and len(step.text) > 150 else step.text

    print(f"""
        {Colors.GREEN}---------------------- AGENT STEP COMPLETED ----------------------{Colors.ENDC}
        {Colors.CYAN}Thought:{Colors.ENDC} {thought_summary}
        {Colors.CYAN}Output:{Colors.ENDC} {output_summary}
        {Colors.CYAN}Text:{Colors.ENDC} {text_summary}
        {Colors.GREEN}----------------------------------------------------------------------{Colors.ENDC}
    """)
    # match = re.search(pattern, step.output)
    # if match:
    #     print(f"Step output: {match.group(1)}")
    # else:
    #     print("Step output is None")
    # print("---------------------------------------------------------")


task_callback_handler = {
    "Select Math Topic": callback_function,
    "Teach Math Topic": callback_function,
    "Generate Math Problem": callback_function,
    "Solve Math Problem": callback_function,
    "Verify Math Problem": callback_function,
    "Update Learner Model": callback_function,
    "Adjust Difficulty Level": callback_function,
    "Generate Math Problem": callback_function,
    "Solve Math Problem": callback_function,
    "Verify Math Problem": callback_function,
    "Update Learner Model": callback_function,
    "Adjust Difficulty Level": callback_function,
}
# Example: Assuming you already defined your agents
agent_list = [
    greeter_agent,
    teacher,
    problem_gen,
    student,
    verifier,
    programmer,
    runner,
    verifier_code,
    learner,
    level_adapter,
    motivator
]

# Apply the LLM config to all agents
# configure_agents_with_llm(agent_list, llm_config)


class learn_math_manager():
    def __init__(self, *args, **kwargs):
        self.crew = kwargs.get('crew')
        self.task_list = kwargs.get('task_list')
        self.agent_list = kwargs.get('agent_list')
        self.process = kwargs.get('process')
        self.max_iterations = kwargs.get('max_iterations')
        self.verbose = kwargs.get('verbose')
        self.currentTopic = None
        self.currentTask = None
        initialize_task_events(self)
    
    def kickoff(self, *args, **kwargs):
        self.crew.kickoff(*args, **kwargs)
        
        
    def _invoke_loop(self):
        super()._invoke_loop()
        
task_list = [task1, task2, task3, task5, task9, task10, task11]
for task in task_list:
    task.callback = task_callback_handler.get(task.name)

    if task.callback is None:
        print(f"{Colors.WARNING}[WARNING] No callback handler found for task: {Colors.BOLD}{task.name}{Colors.ENDC}")

processType = Process.sequential

crew = Crew(
    agents=agent_list,
    tasks=task_list,
    verbose=True,
    max_iterations=10,
    # manager_agent=crew_manager,
    # process=Process.hierarchical
    process=processType,
    step_callback=step_callback
)

# === Run the Crew ===
# crew.kickoff()

learn_math_manager_instance = learn_math_manager(crew=crew, task_list=task_list, agent_list=agent_list, process=processType, max_iterations=10, verbose=True)
learn_math_manager_instance.kickoff({"topic": "Algebra"})
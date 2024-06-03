import autogen
import panel as pn
import openai
import os
import time
import asyncio
from typing import List, Dict
import logging
import src.globals as globals
from Agents.agents import StudentAgent, KnowledgeTracerAgent, TeacherAgent, TutorAgent,  ProblemGeneratorAgent, SolutionVerifierAgent, \
                   ProgrammerAgent, CodeRunnerAgent, LearnerModelAgent, LevelAdapterAgent, MotivatorAgent
from agent_transitions import FSM

logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {'model': "gpt-3.5-turbo"}  # You can adjust the model if needed
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}

globals.input_future = None

# Agents
student = StudentAgent()
knowledge_tracer = KnowledgeTracerAgent()
teacher = TeacherAgent()
tutor = TutorAgent()
problem_generator = ProblemGeneratorAgent()
solution_verifier = SolutionVerifierAgent()
programmer = ProgrammerAgent()
code_runner = CodeRunnerAgent()
learner_model = LearnerModelAgent()
level_adapter = LevelAdapterAgent()
motivator = MotivatorAgent()




# agents_list = [student, knowledge_tracer, teacher, tutor, problem_generator, solution_verifier,
#               programmer, code_runner, learner_model, level_adapter, motivator]
agents_dict = {
    "student": student,
    "knowledge_tracer": knowledge_tracer,
    "teacher": teacher,
    "tutor": tutor,
    "problem_generator": problem_generator,
    "solution_verifier": solution_verifier,
    "programmer": programmer,
    "code_runner": code_runner,
    "learner_model": learner_model,
    "level_adapter": level_adapter,
    "motivator": motivator
}
    
fsm = FSM(agents_dict)

# Create the GroupChat with agents and a manager
groupchat = autogen.GroupChat(agents=list(agents_dict.values()), 
                              messages=[],
                              max_round=20,
                              send_introductions=True,
                              speaker_selection_method=fsm.next_speaker_selector
                              )

class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  

    def run(self, *args, **kwargs):
        try:
            super().run(*args, **kwargs)  # Call the original run method
        except Exception as e:
            print(f"Exception occurred: {e}") 
            # Log the error, send a message to users, etc.

    async def delayed_initiate_chat(self, agent, recipient, message):
        globals.initiate_chat_task_created = True
        await asyncio.sleep(1) 
        await agent.a_initiate_chat(recipient, message=message)

manager = CustomGroupChatManager(groupchat=groupchat)

avatar = {
    student.name: "✏️",                 # Pencil
    knowledge_tracer.name: "🧠",       # Brain
    teacher.name: "👩‍🏫",                # Female teacher
    tutor.name: "🧑‍🎓",                  # Person with graduation hat
    problem_generator.name: "📚",  # Stack of books for problem generation
    solution_verifier.name: "🔍",  # Magnifying glass for solution verification
    programmer.name: "👨‍💻",       # Male programmer/coder emoji
    code_runner.name: "▶️",        # Play button for code execution
    learner_model.name: "🧠",      # Brain emoji for learner model
    level_adapter.name: "📈",      # Chart with upwards trend for level adaptation
    motivator.name: "🏆",          # Trophy emoji for motivation
}


def print_messages(recipient, messages, sender, config):
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

    content = messages[-1]['content']

    if all(key in messages[-1] for key in ['name']):
        chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
    else:
        chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
    
    return False, None  # required to ensure the agent communication flow continues



# Register the print_messages function for each agent
for agent in groupchat.agents:
    agent.register_reply([autogen.Agent, None], reply_func=print_messages, config={"callback": None})



# --- Panel Interface ---
pn.extension(design="material")




# async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
#     await tutor.a_initiate_chat(manager, message=contents) 

#     if globals.input_future and not globals.input_future.done():
#         globals.input_future.set_result(contents)




async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    if not globals.initiate_chat_task_created:
        asyncio.create_task(manager.delayed_initiate_chat(tutor, manager, contents))  
    else:
        if globals.input_future and not globals.input_future.done():
            globals.input_future.set_result(contents)
        else:
            print("No input being awaited.")


chat_interface = pn.chat.ChatInterface(callback=callback)

#Register chat interface with ConversableAgent
for agent in groupchat.agents:
    agent.chat_interface = chat_interface

chat_interface.send("Welcome to the Adaptive Math Tutor! How can I help you today?", user="System", respond=False)
chat_interface.servable()

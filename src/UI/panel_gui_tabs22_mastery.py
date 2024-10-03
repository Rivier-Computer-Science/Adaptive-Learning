import autogen
import panel as pn
import openai
import os
import asyncio

from typing import List, Dict
from src import globals
from src.Agents.agents import *
from src.Agents.mastery_agent import MasteryAgent
from src.Agents.chat_manager_fsms_mastery import FSM
from src.Agents.group_chat_manager_agent import CustomGroupChatManager, CustomGroupChat
from src.UI.reactive_chat import ReactiveChat
from src.UI.avatar import avatar

os.environ["AUTOGEN_USE_DOCKER"] = "False"

######
# Instantiate Agents
#################
# Agents
student = StudentAgent()
mastery = MasteryAgent()
teacher = TeacherAgent()
tutor = TutorAgent()
problem_generator = ProblemGeneratorAgent()
solution_verifier = SolutionVerifierAgent()
programmer = ProgrammerAgent()
code_runner = CodeRunnerAgent()
learner_model = LearnerModelAgent()
level_adapter = LevelAdapterAgent()
motivator = MotivatorAgent()
gamification = GamificationAgent(name="GamificationAgent")


# agents_list = [student, knowledge_tracer, teacher, tutor, problem_generator, solution_verifier,
#               programmer, code_runner, learner_model, level_adapter, motivator]
agents_dict = {
    "student": student,
    "mastery": mastery,
    "teacher": teacher,
    "tutor": tutor,
    "problem_generator": problem_generator,
    "solution_verifier": solution_verifier,
    "programmer": programmer,
    "code_runner": code_runner,
    "learner_model": learner_model,
    "level_adapter": level_adapter,
    "motivator": motivator,
    "gamification": gamification
}



 


##############################################
# Main Adaptive Learning Application
##############################################
globals.input_future = None
script_dir = os.path.dirname(os.path.abspath(__file__))
progress_file_path = os.path.join(script_dir, '../../progress.json')

fsm = FSM(agents_dict)

groupchat = CustomGroupChat(agents=list(agents_dict.values()), 
                              messages=[],
                              max_round=globals.MAX_ROUNDS,
                              send_introductions=True,
                              speaker_selection_method=fsm.next_speaker_selector
                              )

manager = CustomGroupChatManager(groupchat=groupchat,
                                filename=progress_file_path, 
                                is_termination_msg=lambda x: x.get("content", "").rstrip().find("TERMINATE") >= 0 )    

# Begin GUI components
reactive_chat = ReactiveChat(groupchat_manager=manager)

# Register groupchat_manager and reactive_chat GUI interface with ConversableAgents
for agent in groupchat.agents:
    agent.groupchat_manager = manager
    agent.reactive_chat = reactive_chat
    agent.register_reply([autogen.Agent, None], reply_func=agent.autogen_reply_func, config={"callback": None})

# Load chat history on startup
manager.get_chat_history_and_initialize_chat(filename=progress_file_path, chat_interface=reactive_chat.learn_tab_interface)
reactive_chat.update_dashboard()    # Call after history loaded


# Create app with speech recognition button
def create_app():    
     return pn.Column(
        reactive_chat.draw_view(),
       
    )

if __name__ == "__main__":    
    app = create_app()
    pn.serve(app, callback_exception='verbose')

import autogen
import os
from enum import Enum

#################################################
# Define Agents
#################################################
from src.Agents.student_agent import StudentAgent
from src.Agents.tutor_agent import TutorAgent
from src.Agents.solution_verifier_agent import SolutionVerifierAgent
from src.Agents.learner_model_agent import LearnerModelAgent
from src.Agents.level_adapter_agent import LevelAdapterAgent
from src.Agents.motivator_agent import MotivatorAgent

# Telugu specific
from src.Agents.telugu_teaching_agent import TeluguTeachingAgent
from src.Agents.telugu_problem_generator_agent import ProblemGeneratorAgent


#from src.Models.llm_config import gpt3_config

###############################################
# ChatGPT Model
###############################################

gpt4_config_list = [
    {
        'model': "gpt-4o",
    }
]
# These parameters attempt to produce precise reproducible results
temperature = 0
max_tokens = 1000
top_p = 0.5
frequency_penalty = 0.1
presence_penalty = 0.1
seed = 53


gpt4_config = {"config_list": gpt4_config_list, 
               "temperature": temperature,
               "max_tokens": max_tokens,
               "top_p": top_p,
               #"frequency_penalty": frequency_penalty,
              # "presence_penalty": presence_penalty,
               "seed": seed
}

llm = gpt4_config


class AgentKeys(Enum):
    TEACHER = 'teacher'
    TUTOR = 'tutor'
    STUDENT = 'student'
    PROBLEM_GENERATOR = 'problem_generator'
    SOLUTION_VERIFIER = 'solution_verifier'
    LEARNER_MODEL = 'learner_model'
    LEVEL_ADAPTER = 'level_adapter'
    MOTIVATOR = 'motivator'
 
# Agents
student = StudentAgent(llm_config=llm)
teacher = TeluguTeachingAgent(llm_config=llm)
tutor = TutorAgent(llm_config=llm)
problem_generator = ProblemGeneratorAgent(llm_config=llm)
solution_verifier = SolutionVerifierAgent(llm_config=llm)
learner_model = LearnerModelAgent(llm_config=llm)
level_adapter = LevelAdapterAgent(llm_config=llm)
motivator = MotivatorAgent(llm_config=llm)

agents_dict = {
    AgentKeys.STUDENT.value: student,
    AgentKeys.TEACHER.value: teacher,
    AgentKeys.TUTOR.value: tutor,
    AgentKeys.PROBLEM_GENERATOR.value: problem_generator,
    AgentKeys.SOLUTION_VERIFIER.value: solution_verifier,
    AgentKeys.LEARNER_MODEL.value: learner_model,
    AgentKeys.LEVEL_ADAPTER.value: level_adapter,
    AgentKeys.MOTIVATOR.value: motivator,
}
 

avatars = {
    student.name: "✏️",                 # Pencil
    teacher.name: "🧑‍🎓" ,                # Female teacher
    tutor.name: "👩‍🏫",                  # Person with graduation hat
    problem_generator.name: "📚",  # Stack of books for problem generation
    solution_verifier.name: "🔍",  # Magnifying glass for solution verification
    learner_model.name: "🧠",      # Brain emoji for learner model
    level_adapter.name: "📈",      # Chart with upwards trend for level adaptation
    motivator.name: "🏆",  
 }
      




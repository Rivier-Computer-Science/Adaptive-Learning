from typing import Dict
from src.KnowledgeGraphs.math_graph import KnowledgeGraph
import src.KnowledgeGraphs.math_taxonomy as mt
class FSM:
    def __init__(self, agents: Dict):
        self.agents = agents
        self.current_state = "AwaitingTopic"
        
    
    def next_speaker_selector(self, last_speaker, groupchat):
        print(f"Current state: {self.current_state}") 
        if self.current_state == "AwaitingTopic":
            self.current_state = "PresentingLesson"
            return self.agents["teacher"]
        
        elif self.current_state == "PresentingLesson":
            self.current_state = "AwaitingProblem"
            return self.agents["tutor"]
        
        elif self.current_state == "AwaitingProblem":
            self.current_state = "AwaitingAnswer"
            return self.agents["problem_generator"]
        
        elif self.current_state == "AwaitingAnswer":
            self.current_state = "VerifyingAnswer"
            return self.agents["student"]
        
        elif self.current_state == "VerifyingAnswer":
            self.current_state = "VisualizingAnswer"
            return self.agents["solution_verifier"]
        
        elif self.current_state == "VisualizingAnswer":
            self.current_state = "RunningCode"
            return self.agents["programmer"]
        
        elif self.current_state == "RunningCode":
            self.current_state = "UpdatingModel"
            return self.agents["code_runner"]
        
        elif self.current_state == "UpdatingModel":
            self.current_state = "AdaptingLevel"
            return self.agents["learner_model"]
        
        elif self.current_state == "AdaptingLevel":
            self.current_state = "Motivating"
            return self.agents["level_adapter"]
        
        elif self.current_state == "Motivating":
            self.current_state = "PresentingLesson" #TODO: Need more complicated state machine
            return self.agents["motivator"]
                
        else:  # Default to tutor for managing other cases
            print("state not found. Defaulting to Tutor")
            return self.agents["tutor"]
        
class FSMGraphTracerConsole:
    def __init__(self, agents: Dict):
        self.agents = agents
        self.current_state = "Initial"
        
        # Enumerate the agents to reduce typing
        self.student = self.agents["student"]
        self.knowledge_tracer = self.agents["knowledge_tracer"]
        self.problem_generator = self.agents["problem_generator"]
        self.solution_verifier = self.agents["solution_verifier"]
        # Build knowledge graph
        self.skill_level = 0
        self.kg = {}
        i = 0  # Start with a counter at 0
        for key, value_list in mt.subsubsub_topics.items():
            for value in value_list:
                self.kg[i] = value  
                i += 1 
        
        # pick a graph edge - start with Algebra
        for key, value in self.kg.items():
            if value.startswith("Algebra"):
                self.skill_level = key
                break
            else:
                self.skill_level = 0 
    # Modify the next_speaker_selector to accept the required arguments
    def next_speaker_selector(self, last_speaker=None, groupchat=None):
        print(f"Current state: {self.current_state}") 
        if self.current_state == "Initial":
            self.knowledge_tracer.send(f"I will begin to test you on {self.kg[self.skill_level]}", recipient=self.student, request_reply=False, silent=False)
            self.current_state = "GenerateQuestion"
            return self.knowledge_tracer
        
        if self.current_state == "GenerateQuestion":
            self.knowledge_tracer.send(f"Please generate a very easy question for the student on {self.kg[self.skill_level]}", recipient=self.problem_generator, request_reply=True)
            self.pg_response = self.problem_generator.last_message()["content"]
            self.current_state = "AwaitStudentAnswer"
            return self.problem_generator
        
        if self.current_state == "AwaitStudentAnswer":
            self.student_response = input("Enter your answer: ")  # Simulate the student's response
            self.current_state = "VerifySolution"
            return self.solution_verifier
        
        if self.current_state == "VerifySolution":
            self.knowledge_tracer.send(f"{self.student_response} is the student's response to {self.pg_response}. Is the student's answer correct? Answer yes or no", recipient=self.solution_verifier, request_reply=True)
            self.verifier_answer = self.solution_verifier.last_message()["content"]
            self.was_correct = "Yes" in self.verifier_answer
            self.current_state = "AdaptLevel"
            return self.knowledge_tracer
        
        if self.current_state == "AdaptLevel":
            if self.was_correct:
                self.skill_level += 1
                print("The next topic is", self.kg[self.skill_level])
            else:
                print("Better to practice a little more")
            self.current_state = "GenerateQuestion"
            return self.knowledge_tracer
        
        return None
class FSMGraphTracerGUI:
    def __init__(self, agents: Dict):
        self.agents = agents
        self.groupchat_manager = None
        self.reactive_chat = None
        self.current_state = "InitialDelayed"
        
        # Enumerate the agents just to make less typing
        self.student = self.agents["student"]
        self.knowledge_tracer = self.agents["knowledge_tracer"]
        self.problem_generator = self.agents["problem_generator"]
        self.solution_verifier = self.agents["solution_verifier"]
        # Build knowledge graph
        # self.node_name = None
        # self.kg =   KnowledgeGraph()
        # self.kg.build_dag_from_dict(mt.subsubsub_topics)
        # Replace the subsubsub_topics "key" with an integer denoting level of difficulty
        # Each dictionary value is a list. Flatten it and increment the key
        # TODO: Update this code in graph_builder.py
        self.skill_level = 0
        self.kg = {}
        i = 0  # Start with a counter at 0
        for key, value_list in mt.subsubsub_topics.items():
            for value in value_list:
                self.kg[i] = value  
                i += 1 
        # pick a graph edge - start with Algebra
        for key, value in self.kg.items():
            if value.startswith("Algebra"):
                self.skill_level = key
                break
            else:
                self.skill_level = 0 
    
    def next_speaker_selector(self, lastspeaker, groupchat):
        print(f"GRAPH Speaker Selector Current state: {self.current_state}") 
        if self.current_state == "InitialDelayed":
            self.current_state = "Initial"
            return self.knowledge_tracer        
        
        elif self.current_state == "Initial":
            message = {
                'content': f"The student has been working on {self.kg[self.skill_level]}",
                'role': 'user',  # or another role as required
                'name': self.knowledge_tracer.name
            }
            self.problem_generator.send(message, recipient=self.problem_generator, request_reply=False, silent=True)
            self.problem_generator.send(message, self.groupchat_manager)
            #self.reactive_chat.update_graph_tab(recipient=self.groupchat_manager, messages=message,
            #                                    sender=self.problem_generator, config=None)
            groupchat.append(message, self.knowledge_tracer)
            self.current_state = "SelectTopic"
            return self.knowledge_tracer
        
        elif self.current_state == "SelectTopic":
           message = {
                'content': f"ProblemGeneratorAgent, please generate a very easy question on {self.kg[self.skill_level]}. It will be for a high school student.",
                'role': 'user',  # or another role as required
                'name': self.knowledge_tracer.name
            }
           #self.knowledge_tracer.send(message, recipient=self.problem_generator, request_reply=True)
           #groupchat.append(message, self.knowledge_tracer)
           #self.pg_response = self.problem_generator.last_message(agent=self.knowledge_tracer)["content"]
           #groupchat.append(self.pg_response, self.problem_generator)
           #print("pg_response=  ", self.pg_response)          
           self.current_state = "GenerateQuestion"
           return self.problem_generator
        
        elif self.current_state == "GenerateQuestion":
           #self.pg_response = self.problem_generator.last_message(agent=self.problem_generator)["content"]
           #groupchat.append(self.pg_response, self.problem_generator)
           #print("pg_response=  ", self.pg_response)          
           self.current_state = "AwaitStudentAnswer"
           return self.student
           
        elif self.current_state == "AwaitStudentAnswer":
            #self.student_response = input()
            self.current_state = "VerifySolution"
            return self.solution_verifier
        
        elif self.current_state == "VerifySolution":
            #self.knowledge_tracer.send(f"{self.student_response} is the Students response to {self.pg_response}. Is the Student's answer correct? Answer yes or no", recipient=self.solution_verifier, request_reply=True)
            #self.verifier_answer = self.solution_verifier.last_message()["content"]
            #self.was_correct = True if "Yes" in self.verifier_answer else False            
            self.current_state = "AdaptLevel"
            return self.knowledge_tracer
        
        elif self.current_state == "AdaptLevel":
            if self.was_correct:
                self.skill_level += 1
                print("The next topic is", self.kg[self.skill_level])
            else:
                print("Better to practice a little more")
            self.current_state = "GenerateQuestion"
            return self.knowledge_tracer
        
        else:
            return None
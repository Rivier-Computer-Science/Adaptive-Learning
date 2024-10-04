from typing import Dict
import pprint
import src.KnowledgeGraphs.math_taxonomy as mt
class FSMGraphTracerConsole:
    def __init__(self, agents: Dict):
        self.agents = agents
        self.groupchat_manager = None
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
    def register_groupchat_manager(self, groupchat_manager):
        self.groupchat_manager = groupchat_manager
    def next_speaker_selector(self, last_speaker=None, groupchat=None):
        print(f"Current state: {self.current_state}") 
        
        if self.current_state == "Initial":
            # Ask the student which concept they want to learn
            concepts = list(self.kg.values())
            print("Available concepts:")
            for idx, concept in enumerate(concepts):
                print(f"{idx + 1}. {concept}")
            
            concept_choice = int(input("Enter the number of the concept you want to learn: ")) - 1
            self.skill_level = concept_choice
            print(f"You chose: {self.kg[self.skill_level]}")
            self.current_state = "GenerateFirstQuestion"
            return self.knowledge_tracer
        
        if self.current_state == "GenerateFirstQuestion":
            # Generate the first question for the student based on their chosen concept
            self.knowledge_tracer.send(f"Please generate a very easy question for the student on {self.kg[self.skill_level]}", recipient=self.problem_generator, request_reply=True)
            self.pg_response = self.problem_generator.last_message(agent=self.knowledge_tracer)["content"]
            self.current_state = "AwaitStudentAnswer"
            return self.problem_generator
        
        if self.current_state == "AwaitStudentAnswer":
            # Await the student's answer to the question
            print(f"Question: {self.pg_response}")
            self.student_response = input("Enter your answer: ")  # Simulate the student's response
            self.current_state = "VerifySolution"
            return self.solution_verifier
        
        if self.current_state == "VerifySolution":
            # Verify the student's answer
            self.knowledge_tracer.send(f"{self.student_response} is the student's response to {self.pg_response}. Is the student's answer correct? Answer yes or no", recipient=self.solution_verifier, request_reply=True)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(self.groupchat_manager.groupchat.get_messages())     
            self.verifier_answer = self.groupchat_manager.groupchat.get_messages()[-1]['content']
            self.was_correct = "Yes" in self.verifier_answer
            
            # Only allow the student to proceed if they gave the correct answer
            if self.was_correct:
                print("Correct answer. Moving to the next question.")
                self.current_state = "AdaptLevel"
            else:
                print("Incorrect answer. Try again.")
                self.current_state = "GenerateQuestion"  # Ask another question if the answer is wrong
            return self.knowledge_tracer
        
        if self.current_state == "AdaptLevel":
            # Adapt the difficulty level and move to the next question if the student was correct
            if self.was_correct:
                self.skill_level += 1
                if self.skill_level >= len(self.kg):
                    print("Congratulations! You have completed all concepts.")
                    return None
                print(f"The next topic is {self.kg[self.skill_level]}")
            else:
                print("Let's try again with another question on the same topic.")
            self.current_state = "GenerateQuestion"
            return self.knowledge_tracer
        
        if self.current_state == "GenerateQuestion":
            # Generate a question for the student
            self.knowledge_tracer.send(f"Please generate another question for the student on {self.kg[self.skill_level]}", recipient=self.problem_generator, request_reply=True)
            self.pg_response = self.problem_generator.last_message(agent=self.knowledge_tracer)["content"]
            self.current_state = "AwaitStudentAnswer"
            return self.problem_generator
        
        return None
# State Machine Definition

#     States:
#         Welcome: System greets the user.
#         AwaitingTopic: Waiting for the user to choose a math topic.
#         PresentingLesson: Teacher presents the lesson.
#         AwaitingProblem: Tutor requests a problem from the ProblemGenerator.
#         AwaitingAnswer: Waiting for the student's answer.
#         VerifyingAnswer: Tutor requests verification from the SolutionVerifier.
#         VisualizingAnswer: Tutor requests visualization from the Programmer.
#         RunningCode: Tutor requests code execution from the CodeRunner.
#         UpdatingModel: Tutor updates the LearnerModel.
#         AdaptingLevel: Tutor adjusts difficulty with the LevelAdapter.
#         Motivating: Tutor requests motivation from the Motivator.
#         AskingForMore: Tutor asks the student if they want more questions.
#         NextLesson: Teacher starts the next lesson.

#     Transitions:
#         Welcome -> AwaitingTopic: On system greeting.
#         AwaitingTopic -> PresentingLesson: When user chooses a topic.
#         PresentingLesson -> AwaitingProblem: After lesson presentation.
#         AwaitingProblem -> AwaitingAnswer: When a problem is generated.
#         AwaitingAnswer -> VerifyingAnswer: When the student provides an answer.
#         VerifyingAnswer -> VisualizingAnswer: After answer verification.
#         VisualizingAnswer -> RunningCode: After code generation.
#         RunningCode -> UpdatingModel: After code execution.
#         UpdatingModel -> AdaptingLevel: After model update.
#         AdaptingLevel -> Motivating: After difficulty adjustment.
#         Motivating -> AskingForMore: After providing motivation.
#         AskingForMore -> AwaitingProblem: If the user wants more questions.
#         AskingForMore -> NextLesson: If the user wants to move on.
#         NextLesson -> AwaitingProblem: When the next lesson starts.

    # System: "Welcome to the math tutor! Let's get started. What areas of math are you interested in?"
    # Human: "I want to learn about algebra."
    # Teacher: Here is your first lesson
    # Tutor: Ask the Problem Generator for a question to test the Student based on the Teacher's lesson
    # Student: Answer the question.
    # Tutor: Ask the Solution Verifier to check the Answer
    # Tutor: Ask the Programmer to write a program to visualize the answer
    # Tutor: Ask the Code Runner to run the program
    # Tutor: Ask the Learner Model to update itself based on the Student's answer
    # Tutor: Ask the Level Adapter if the difficulty should be increased, decreased, or remain the same
    # Tutor: Ask the Motivator to provide motivation to the student
    # Tutor: Ask the student if they want more test questions
    # Teacher: Start the next lesson at the Student's request

from typing import Dict

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
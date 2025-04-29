

# Introduction Adaptive Learning Career Path Recommendation System

This project creates an adaptable learning platform that recommends career paths based on student responses and developing interests.
It includes an FSM (Finite State Machine) to control discussion flow, a multi-agent system for dynamic analysis, and a Panel-based UI for student involvement.

My Contributions:

Developed the full CareerFSM in fsm_career_path_interest.py.

Designed and implemented the Panel UI with agent interactions in panel_gui_tabs_vt.py.

Developed the Reactive Chat Interface in reactive_chat_vt.py for real-time agent communication.

Integrated agents, state transitions, group chat management, and frontend UI buttons.

Tested state transitions, message routing, and dynamic career recommendation updates.



# Sprint Objective Summary

Sprint | Objective
Sprint 1 | Build minimum viable agent setup (basic student interaction)
Sprint 2 | FSM spike: Career progression state transitions
Sprint 3 | Create working MVP: Panel tabs, UI buttons wired to agents
Sprint 4 | Improve agent interactions, handle dynamic interest updates



# User Story

User Story CP1: Career Path Agent Enhancement - *As a student, I want the Career Path Agent to provide personalized career guidance based on my interests and skills, so I can plan my career path and address skill gaps effectively.


Task | Status | Owner
CP 1.1: Career Path Interest Exploration (Autogen Agents, 24 ph) #360 | ✅ Completed
**Career Pathway and Certification Planning (Autogen Agents, 22 ph)** #373 | ✅ Completed
**Identifying and Addressing Skill Gaps (Autogen Agents, 20 ph)** #391 | ✅ Completed
**Dynamic Recommendation Updates (Autogen Agents, 14 ph)** #392 | ✅ Completed
**State Machine Integration (Autogen Agents, 18 ph)** #393 | ✅ Completed
**Testing and Validation (Autogen Agents, 20 ph)** #394 | ✅ Completed



## Speech Recognition Module
```sh
conda install SpeechRecognition 
conda install pyaudio
```


# Agents

There are 11 agents used in the adaptive learning system:

**Agent Name** | **Role / Responsibility**
CareerGrowthAgent | Generates step-by-step career progression plans tailored to the student profile.
CertificationRecommendationAgent | Suggests industry-relevant certification pathways based on the chosen career.
JobFinderAgent | Retrieves real-time job recommendations based on learner capabilities.
CompetencyExtractionAgent | Extracts required competencies for selected job roles or career paths.
GapAnalysisAgent | Compares learner skills with job requirements and identifies skill gaps.
PersonalizedLearningPlanAgent | Builds a custom study plan (courses, books, exercises) to fill skill gaps.
ResourceRankingAgent | Prioritizes learning resources based on relevance and student preferences.
LearnerModelAgent | Tracks and updates the student's skill profile, capabilities, and progression.
UserPreferenceUpdateAgent | Dynamically updates student preferences and learning goals based on inputs.
RealTimeCareerAdjustmentAgent | Adjusts recommendations on-the-fly as student interests evolve.
RecommendationTestingAgent | Tests the accuracy and adaptability of the system’s career recommendations.
StateDefinitionAgent | Defines the states and transitions of the career progression FSM.
StateTransitionAgent | Triggers transitions between FSM states based on learner updates.
DataSynchronizationAgent | Synchronizes updates between FSM state and learner model/dashboard.
StateMachineTestingAgent | Validates FSM transitions for correctness and consistency.
AIEvaluationAgent | Evaluates how well the recommendations match student inputs and industry trends.
ScenarioSimulationAgent | Simulates diverse learner profiles to stress-test the system.
DynamicRecommendationTestingAgent | Tests the system’s responsiveness to evolving preferences and skills.

# System Architecture

The system is a modular, agent-based career recommendation platform that guides students through personalized learning and career exploration using a finite state machine (FSM) and AI agents. The front-end uses Panel (Python GUI), and the backend orchestrates a set of intelligent agents built using the autogen framework


# Panel UI

![panel_ui](~/../pics/panel_ui.png)

The Model tab interacts with the LearnerModel agent and provides an assessment of the student's capabilities.

![learner_model](~/../pics/learner_model.png)


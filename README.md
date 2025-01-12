

# Introduction Multi-Agent Adaptive Learning

This code is from Rivier University's Professional Seminar class (COMP-699) from the Summer of 2024.

It uses [Microsoft's autogen](https://microsoft.github.io/autogen/docs/Getting-Started/) to specialize an agent for each function of an adaptive learning system. The model used is OpenAI's ChatGPT-4o.

It uses [panel](https://panel.holoviz.org/) for the chat interface. It opens in a web browser.

There is [a paper published by the Rivier Academic Journal](https://www2.rivier.edu/journal/ROAJ-Summer-2024/J1324_Glossner%20et%20al_2024.pdf) describing the system. 

Dokku, S., Gumpula, A., Gudati, S., Nagisetty, M., Thimmarayappa, R., Yeruva, J. P., & Glossner, J. (2024). Multi-agent adaptive learning for mathematics. _Rivier Academic Journal_, 19(1), Summer 2024. Rivier University.


# Running the Code

Run as a module. It will open up a browser tab in your default browser. 

Note that as of 1/12/2025, it does not work with Firefox. Use Chrome.

```sh
(adaptive) user@machine:~/Adaptive-Learning$ python -m src.UI.panel_gui_tabs_jg
```

# Installing Dependencies

Install Anaconda
- Download and install it from the [official Anaconda website](https://www.anaconda.com/products/individual).

Install Dependencies from conda environment file

```sh
conda env create -f conda_env.yml -n adaptive
conda activate adaptive
```



## To Install Each Package Manually (not recommended)

It is preferable to install with the conda_env.yml file but these packages can also be install manually.

```sh
conda update --all
conda create -n adaptive python=3.12
conda activate adaptive
```

Install panel

`conda install -c conda-forge panel`

Install transitions state machine

`conda install -c conda-forge transitions`

Install pyautogen 0.2.33+

```sh
conda install openai
conda install -c conda-forge pyautogen
```

Note that there is also a package called autogen. Do NOT install it. You want pyautogen.

Install Firebase tools 

```sh
conda install aiohttp
conda config --set pip_interop_enabled True
pip install firebase-admin
```


## OpenAI Environment Configuration


- LINUX: export  OPENAI_API_KEY=sk-
- WINDOWS: set  OPENAI_API_KEY=sk-

If you don't have Docker installed, you need to set AUTOGEN_USE_DOCKER=False. Be advised that if you set this to False it allows code to run on your system at whatever privileges you have (e.g., Windows Admin).

You can also use a .env file if you don't want to export/set every time.



## Speech Recognition Module
```sh
conda install SpeechRecognition 
conda install pyaudio
```


# Agents

There are 11 agents used in the adaptive learning system:

| **Agents**         | **Role**                                                                 |
|--------------------|--------------------------------------------------------------------------|
| Student            | A user proxy for a student who wants to learn mathematics.               |
| Knowledge Tracer   | Determine the Student's mathematical capabilities.                       |
| Teacher            | Present new material in multiple formats.                                |
| Tutor              | Explain answers to a Student. Help a Student to learn new material or review previous materials. |
| Problem Generator  | Generate math problems at the appropriate level for the Student.         |
| Solution Verifier  | Check the Student's solutions to math problems.                          |
| Programmer         | Write python code to solve math problem.                                 |
| Code Runner        | Execute python code and display the result.                              |
| Level Adapter      | Determine when to increase or decrease the level of difficulty for a Student. |
| Learner Model      | A model of the Student's learning level.                                 |
| Motivator          | Provides positive and encouraging feedback to the Student.               |

# Agent Communications

We had hoped to use an unconstrained `autogen.GroupChatManager` to manage agent communications. Try as we may, we could not get agents to stay within their assigned roles. We eventually resorted to a state machine for agent selection using the panel gui. The limitation of this approach means there is a very specific learning path. See the paper for details.

The console knowledge tracer program uses direct agent communication.

## State Machine in panel UI

![uml_state_machine_v3](~/../pics/uml_state_machine_v3.png)

# Panel UI

The UI contains multiple tabs in various states of completion. The Learn tab is the main interface. 

![panel_ui](~/../pics/panel_ui.png)

The Model tab interacts with the LearnerModel agent and provides an assessment of the student's capabilities.

![learner_model](~/../pics/learner_model.png)


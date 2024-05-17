import autogen
import os
import asyncio
from globals import input_future


os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {
        'model': "gpt-3.5-turbo",
    }
]
gpt4_config = {"config_list": config_list, "temperature": 0, "seed": 53}


class MyConversableAgent(autogen.ConversableAgent):
    def __init__(self, chat_interface, **kwargs):
        super().__init__(**kwargs)
        self.chat_interface = chat_interface

    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        print('AGET!!!!!!')  # or however you wish to display the prompt
        self.chat_interface.send(prompt, user="System", respond=False)
        if input_future is None or input_future.done():
            input_future = asyncio.Future()
        await input_future
        input_value = input_future.result()
        input_future = None
        return input_value

class AdminAgent(MyConversableAgent):
    def __init__(self, chat_interface):
        super().__init__(
            chat_interface=chat_interface,
            name="Admin",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message="""A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.""",
            code_execution_config=False,
            human_input_mode="ALWAYS",
            llm_config=gpt4_config,
        )

class EngineerAgent(autogen.AssistantAgent):
    def __init__(self):
        super().__init__(
            name="Engineer",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
        )

class ScientistAgent(autogen.AssistantAgent):
    def __init__(self):
        super().__init__(
            name="Scientist",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code.""",
        )

class PlannerAgent(autogen.AssistantAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            human_input_mode="NEVER",
            system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
            llm_config=gpt4_config,
        )

class ExecutorAgent(autogen.UserProxyAgent):
    def __init__(self):
        super().__init__(
            name="Executor",
            system_message="Executor. Execute the code written by the engineer and report the result.",
            human_input_mode="NEVER",
            code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
        )

class CriticAgent(autogen.AssistantAgent):
    def __init__(self):
        super().__init__(
            name="Critic",
            system_message="""Critic. Double check plan, claims, code from other agents and provide feedback. 
Check whether the plan includes adding verifiable info such as source URL.""",
            llm_config=gpt4_config,
            human_input_mode="NEVER",
        )




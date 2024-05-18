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


####################################################################
#
# Conversable Agents
#
##################################################################### 

class MyConversableAgent(autogen.ConversableAgent):
    def __init__(self, input_queue, chat_interface, **kwargs):  
        super().__init__(**kwargs)
        self.chat_interface = chat_interface
        self.input_queue = input_queue  

    async def a_get_human_input(self, prompt: str) -> str:
        self.chat_interface.send(prompt, user="System", respond=False)
        return await self.input_queue.get()  


class AdminAgent(MyConversableAgent):
    def __init__(self, input_queue, chat_interface):  
        super().__init__(
            input_queue=input_queue, 
            chat_interface=chat_interface,
            name="Admin",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
            system_message="""A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.""",
            code_execution_config=False,
            human_input_mode="ALWAYS",
            llm_config=gpt4_config,

        )

####################################################################
#
# Assisstant Agents
#
#####################################################################        

class MyAssisstantAgent(autogen.AssistantAgent):
    def __init__(self, input_queue, **kwargs):
        super().__init__(**kwargs)
        self.input_queue = input_queue

    def generate_reply(self, messages, sender, config):  # Override generate_reply
        asyncio.create_task(self.input_queue.put(self.reply_message))        
        return self.reply_message 


class EngineerAgent(MyAssisstantAgent):
    def __init__(self, input_queue):
        super().__init__(
            input_queue = input_queue,
            name="Engineer",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
        )
 
 
class ScientistAgent(MyAssisstantAgent):
    def __init__(self, input_queue):
        super().__init__(
            input_queue = input_queue,
            name="Scientist",
            human_input_mode="NEVER",
            llm_config=gpt4_config,
            system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code.""",
        )


class PlannerAgent(MyAssisstantAgent):
    def __init__(self, input_queue):
        super().__init__(
            input_queue = input_queue,
            name="Planner",
            human_input_mode="NEVER",
            system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
            llm_config=gpt4_config,
        )


class CriticAgent(MyAssisstantAgent):
    def __init__(self, input_queue):
        super().__init__(
            input_queue = input_queue,
            name="Critic",
            system_message="""Critic. Double check plan, claims, code from other agents and provide feedback. 
Check whether the plan includes adding verifiable info such as source URL.""",
            llm_config=gpt4_config,
            human_input_mode="NEVER",
        )



####################################################################
#
# UserProxy Agents
#
#####################################################################        

class ExecutorAgent(autogen.UserProxyAgent):
    def __init__(self):
        super().__init__(
            name="Executor",
            system_message="Executor. Execute the code written by the engineer and report the result.",
            human_input_mode="NEVER",
            code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
        )



avatar = {
    "Admin": "👨‍💼",
    "Engineer": "👩‍💻",
    "Scientist": "👩‍🔬",
    "Planner": "🗓",
    "Executor": "🛠",
    "Critic": "📝",
}

def print_messages(recipient, messages, sender, config):
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    content = messages[-1]['content']
    if hasattr(recipient, 'chat_interface'):
        if all(key in messages[-1] for key in ['name']):
            recipient.chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            recipient.chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
    return False, None

import asyncio
from unittest.mock import MagicMock
import panel as pn

# Mocking the agents and autogen
learner = MagicMock(name='LearnerAgent')
tutor = MagicMock(name='TutorAgent')
problem_generator = MagicMock(name='ProblemGeneratorAgent')
solution_verifier = MagicMock(name='SolutionVerifierAgent')
motivator = MagicMock(name='MotifatorAgent')
visualizer = MagicMock(name='VisualizerAgent')
executor = MagicMock(name='CodeExecutorAgent')

autogen = MagicMock()
globals = MagicMock()
globals.input_future = None

autogen.GroupChat.return_value = MagicMock()
autogen.GroupChatManager.return_value = MagicMock()
autogen.Agent = MagicMock()

avatar = {
    learner.name: "🎓", tutor.name: "🧑‍🏫", problem_generator.name: "❓",
    solution_verifier.name: "✅", motivator.name: "🙌", visualizer.name: "📊", executor.name: "🖥️"
}

def print_messages(recipient, messages, sender, config):
    content = messages[-1]['content']

    # Check if the message is from the Problem Generator and intended for the Tutor
    if sender == problem_generator and recipient == tutor:
        return False, None  # Don't print or send to chat interface

    # Set the appropriate user for the chat interface
    if sender == learner:  # Check if the sender is the Learner
        user_name = "Learner"  # Use "Learner" as the user for their messages
    else:
        user_name = sender.name  # Otherwise, use the agent's name

    # Ensure all messages have a 'name' key for proper display
    if 'name' not in messages[-1]:
        messages[-1]['name'] = user_name  # Set the correct user name

    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    chat_interface.send(content, user=user_name, avatar=avatar.get(user_name, "🤖"), respond=False)
    pn.io.push_notebook()  # Force UI update after sending the message
    return False, None

async def delayed_initiate_chat(agent, recipient, message):
    await asyncio.sleep(2)
    await agent.a_initiate_chat(recipient, message=message)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    if globals.input_future and not globals.input_future.done():
        globals.input_future.set_result(contents)
    else:
        print("No input being awaited.")

chat_interface = pn.chat.ChatInterface(callback=callback)

# Manually test print_messages function
def test_print_messages():
    messages = [{'content': 'Test message', 'name': 'Learner'}]
    recipient = tutor
    sender = problem_generator
    config = {}

    should_print, _ = print_messages(recipient, messages, sender, config)
    print(f"Test 1 - should_print: {should_print}, message name: {messages[-1].get('name')}")

    messages = [{'content': 'Test message'}]
    sender = learner

    should_print, _ = print_messages(recipient, messages, sender, config)
    print(f"Test 2 - should_print: {should_print}, message name: {messages[-1].get('name')}")

# Manually test callback function
async def test_callback():
    contents = "Test message"
    user = "Test User"
    instance = MagicMock()

    await callback(contents, user, instance)

    globals.input_future = MagicMock()
    globals.input_future.done.return_value = False

    await callback(contents, user, instance)
    print(f"globals.input_future.set_result called with: {contents}")

# Run the tests
if __name__ == '__main__':
    test_print_messages()
    asyncio.run(test_callback())
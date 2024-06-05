# message_handler.py

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
    pn.io.push_notebook()   # Force UI update after sending the message
    return False, None

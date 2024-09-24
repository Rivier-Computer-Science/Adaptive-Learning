import panel as pn
import param


class BookmarkPage(param.Parameterized):
    def __init__(self, **params):
        super().__init__(**params)
        
        # Placeholder for storing bookmarked messages
        self.bookmarked_messages = []
        self.chat_interface = pn.chat.ChatInterface(callback=self.noop_callback, name="BookmarkInterface")
        
    async def noop_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        """No operation callback for the bookmark interface."""
        pass

    def add_bookmark(self, message_data):
        """Add a new message to bookmarks and update the chat interface."""
        self.bookmarked_messages.append(message_data)
        self.update_bookmark_view()

    def remove_bookmark(self, message_data):
        """Remove a message from bookmarks and update the chat interface."""
        self.bookmarked_messages.remove(message_data)
        self.update_bookmark_view()

    def update_bookmark_view(self):
        """Update the chat interface to display bookmarked messages with remove buttons."""
        self.chat_interface.clear()  # Clear previous messages

        for message_data in self.bookmarked_messages:
            user = message_data['user']
            message = message_data['message']

            # Create a button to remove the bookmark
            remove_button = pn.widgets.ButtonIcon(icon="heart",active_icon="heart-filled",value=True, size="2em", description="favorite")
            remove_button.on_click(lambda event, msg=message_data: self.remove_bookmark(msg))

            # Send the bookmarked message to the chat interface and append the remove button
            self.chat_interface.send(message, user=user, avatar=None, respond=False)
            self.chat_interface.append(pn.Row(remove_button))

    def get_view(self):
        """Return the view of the chat interface with bookmarked messages."""
        return pn.Column(self.chat_interface)

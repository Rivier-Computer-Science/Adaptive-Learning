import unittest
from unittest.mock import AsyncMock, patch
import asyncio

class TestPanelGuiTutor(unittest.IsolatedAsyncioTestCase):

    @patch('panel_gui_tutor.asyncio.sleep', new_callable=AsyncMock)
    async def test_delayed_initiate_chat(self, mock_sleep):
        from panel_gui_tutor import delayed_initiate_chat, learner, tutor

        # Ensure a_initiate_chat is an AsyncMock
        learner.a_initiate_chat = AsyncMock()

        agent = learner
        recipient = tutor
        message = "Test message"

        # Call the function to test
        await delayed_initiate_chat(agent, recipient, message)

        # Ensure that the appropriate agent's a_initiate_chat method is called
        agent.a_initiate_chat.assert_awaited_once_with(recipient, message=message)
        # Ensure there is a 2-second delay
        mock_sleep.assert_awaited_once_with(2)

if __name__ == '__main__':
    unittest.main()

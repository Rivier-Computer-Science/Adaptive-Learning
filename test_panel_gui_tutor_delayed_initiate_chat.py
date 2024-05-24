import unittest
from unittest.mock import MagicMock, AsyncMock
import asyncio

class TestPanelGuiTutor(unittest.IsolatedAsyncioTestCase):
    
    async def test_delayed_initiate_chat(self):
        from panel_gui_tutor import delayed_initiate_chat, learner, tutor

        agent = learner
        recipient = tutor
        message = "Test message"

        await delayed_initiate_chat(agent, recipient, message)

        # Ensure that the appropriate agent's a_initiate_chat method is called
        agent.a_initiate_chat.assert_awaited_once_with(recipient, message=message)
        # Ensure there is a 2-second delay
        self.assertEqual(asyncio.sleep.call_args[0][0], 2)

if __name__ == '__main__':
    unittest.main()
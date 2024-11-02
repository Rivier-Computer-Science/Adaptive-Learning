import unittest
from unittest.mock import patch, MagicMock
import speech_recognition as sr

# Replace 'src.UI.panel_gui_tabs_with_speech_buttons' with the actual module path if different
from src.UI.panel_gui_tabs_with_speech_buttons import (
    recognize_speech_from_mic,
    start_listening,
    reset_recognizer,
    status_text
)

class TestSpeechToText(unittest.TestCase):

    @patch('speech_recognition.Recognizer.recognize_google')
    @patch('speech_recognition.Recognizer.listen')
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_successful_transcription(self, mock_adjust_for_ambient_noise, mock_listen, mock_recognize_google):
        """Test that the speech is correctly transcribed when recognize_google returns a valid transcript"""
        
        # Mock audio input and Google recognition output
        mock_audio = MagicMock(name="AudioData")
        mock_listen.return_value = mock_audio
        mock_recognize_google.return_value = "This is a test"

        # Call the function
        transcript = recognize_speech_from_mic()

        # Assertions
        mock_listen.assert_called_once()
        mock_recognize_google.assert_called_once_with(mock_audio)
        self.assertEqual(transcript, "This is a test")

    @patch('speech_recognition.Recognizer.recognize_google', side_effect=sr.UnknownValueError)
    @patch('speech_recognition.Recognizer.listen')
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_transcription_unknown_value_error(self, mock_adjust_for_ambient_noise, mock_listen, mock_recognize_google):
        """Test that the function handles cases where the audio cannot be understood"""
        
        # Mock audio input
        mock_audio = MagicMock(name="AudioData")
        mock_listen.return_value = mock_audio

        # Call the function
        transcript = recognize_speech_from_mic()

        # Assertions
        mock_listen.assert_called_once()
        mock_recognize_google.assert_called_once_with(mock_audio)
        self.assertIsNone(transcript)

    @patch('speech_recognition.Recognizer.listen', side_effect=sr.WaitTimeoutError)
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_transcription_timeout_error(self, mock_adjust_for_ambient_noise, mock_listen):
        """Test that the function handles timeout errors during listening"""

        # Call the function
        transcript = recognize_speech_from_mic()

        # Assertions
        mock_listen.assert_called_once()
        self.assertIsNone(transcript)

    @patch('speech_recognition.Recognizer.recognize_google', side_effect=sr.RequestError("API error"))
    @patch('speech_recognition.Recognizer.listen')
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_network_error_during_transcription(self, mock_adjust_for_ambient_noise, mock_listen, mock_recognize_google):
        """Test that the function handles network errors properly"""
        
        # Mock audio input
        mock_audio = MagicMock(name="AudioData")
        mock_listen.return_value = mock_audio

        # Call the function
        transcript = recognize_speech_from_mic()

        # Assertions
        mock_listen.assert_called_once()
        mock_recognize_google.assert_called_once_with(mock_audio)
        self.assertIsNone(transcript)

    @patch('speech_recognition.Recognizer.listen')
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_recognizer_reset(self, mock_adjust_for_ambient_noise, mock_listen):
        """Test that the recognizer resets properly after each session"""
        
        # Mock audio input
        mock_audio = MagicMock(name="AudioData")
        mock_listen.return_value = mock_audio

        # Simulate a successful transcription
        start_listening()
        reset_recognizer()

        # Ensure that listen was not called after reset
        self.assertEqual(mock_listen.call_count, 0)

    @patch('speech_recognition.Recognizer.listen')
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    @patch('src.UI.panel_gui_tabs_with_speech_buttons.status_text')
    def test_status_text_updated_correctly(self, mock_status_text, mock_adjust_for_ambient_noise, mock_listen):
        """Test that the status indicator is updated correctly during the listening and processing states"""
        
        # Mock audio input
        mock_audio = MagicMock(name="AudioData")
        mock_listen.return_value = mock_audio

        # Simulate the function call
        start_listening()

        # Ensure the status text is updated correctly
        self.assertEqual(mock_status_text.value, "Listening for 5 seconds...")

    @patch('speech_recognition.Recognizer.listen', side_effect=sr.WaitTimeoutError)
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    @patch('src.UI.panel_gui_tabs_with_speech_buttons.status_text')
    def test_status_text_on_timeout(self, mock_status_text, mock_adjust_for_ambient_noise, mock_listen):
        """Test that the status indicator shows the correct state on timeout"""
        
        # Call the function to trigger timeout
        recognize_speech_from_mic()

        # Ensure the status text is updated correctly
        self.assertEqual(mock_status_text.value, "Timeout: No speech detected")

    @patch('speech_recognition.Recognizer.recognize_google')
    @patch('speech_recognition.Recognizer.listen')
    @patch('speech_recognition.Recognizer.adjust_for_ambient_noise')
    def test_consecutive_sessions(self, mock_adjust_for_ambient_noise, mock_listen, mock_recognize_google):
        """Test that the recognizer handles consecutive sessions without issues"""
        
        # Mock audio input and Google recognition output
        mock_audio = MagicMock(name="AudioData")
        mock_listen.return_value = mock_audio
        mock_recognize_google.return_value = "Test transcription"

        # First session
        start_listening()
        reset_recognizer()

        # Second session
        start_listening()
        reset_recognizer()

        # Assertions
        self.assertEqual(mock_listen.call_count, 2)
        self.assertEqual(mock_recognize_google.call_count, 2)


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import requests # Make sure requests is imported if send_pushbullet_notification uses it directly

# Assuming auto_rip_and_eject.py is in the same directory or accessible in PYTHONPATH
from auto_rip_and_eject import send_pushbullet_notification # PUSHBULLET_API_KEY import removed

USER_PROVIDED_API_KEY = "o.UqWB9szmZcPUIJVmHq5cmkRg7UmLBmil" # Added user-provided API key

class TestPushbulletNotification(unittest.TestCase):

    @patch('requests.post')
    def test_send_pushbullet_notification_success(self, mock_post):
        """Test successful Pushbullet notification."""
        # Configure the mock to simulate a successful API call
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock() # Mock raise_for_status to do nothing
        mock_post.return_value = mock_response

        test_title = "Test Success"
        test_message = "This is a successful test notification."
        
        # Call the function
        send_pushbullet_notification(test_title, test_message, USER_PROVIDED_API_KEY) # Use locally defined API key

        # Assert that requests.post was called correctly
        mock_post.assert_called_once_with(
            "https://api.pushbullet.com/v2/pushes",
            json={"type": "note", "title": test_title, "body": test_message},
            headers={"Access-Token": USER_PROVIDED_API_KEY, "Content-Type": "application/json"}, # Use locally defined API key
            timeout=10
        )
        mock_response.raise_for_status.assert_called_once()

    @patch('requests.post')
    def test_send_pushbullet_notification_api_error(self, mock_post):
        """Test Pushbullet notification when API returns an error."""
        # Configure the mock to simulate an API error
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(side_effect=requests.exceptions.HTTPError("API Error"))
        mock_post.return_value = mock_response

        test_title = "Test API Error"
        test_message = "This notification should simulate an API error."

        # Call the function
        send_pushbullet_notification(test_title, test_message, USER_PROVIDED_API_KEY) # Use locally defined API key

        # Assert that requests.post was called
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch('requests.post')
    def test_send_pushbullet_notification_request_exception(self, mock_post):
        """Test Pushbullet notification with a general request exception."""
        # Configure the mock to raise a RequestException
        mock_post.side_effect = requests.exceptions.RequestException("Network Error")

        test_title = "Test Network Error"
        test_message = "This notification should simulate a network error."

        send_pushbullet_notification(test_title, test_message, USER_PROVIDED_API_KEY) # Use locally defined API key
        
        mock_post.assert_called_once()

    def test_send_pushbullet_notification_no_api_key(self):
        """Test Pushbullet notification when API key is missing."""
        # No need to mock requests.post if the function returns early
        test_title = "Test No Key"
        test_message = "This should not be sent."
        
        # Call the function with a None or empty API key
        send_pushbullet_notification(test_title, test_message, None)
        # Add assertions here if your function prints to stdout or logs
        # For example, you might capture stdout and check its content.
        # This example assumes the function just prints and returns.

if __name__ == '__main__':
    unittest.main()

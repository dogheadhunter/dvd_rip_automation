import requests
import argparse

PUSHBULLET_API_KEY = "o.UqWB9szmZcPUIJVmHq5cmkRg7UmLBmil"  # Your Pushbullet API Key

def send_cli_pushbullet_notification(title: str, message: str, api_key: str):
    """
    Sends a notification via Pushbullet.
    """
    if not api_key:
        print("Error: Pushbullet API key is not set in the script.")
        return False
    if not title or not message:
        print("Error: Both title and message are required.")
        return False

    try:
        data = {"type": "note", "title": title, "body": message}
        headers = {"Access-Token": api_key, "Content-Type": "application/json"}
        response = requests.post("https://api.pushbullet.com/v2/pushes", json=data, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        print(f"Pushbullet notification '{title}' sent successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending Pushbullet notification: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a Pushbullet notification from the command line.")
    parser.add_argument("-t", "--title", required=True, help="The title of the notification.")
    parser.add_argument("-m", "--message", required=True, help="The body of the notification message.")

    args = parser.parse_args()

    send_cli_pushbullet_notification(args.title, args.message, PUSHBULLET_API_KEY)

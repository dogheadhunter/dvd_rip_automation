\
import smtplib
import ssl
from email.message import EmailMessage

# --- USER CONFIGURATION ---
# SMS Details
phone_number = "5079517868"
# Spectrum Mobile typically uses vtext.com (like Verizon).
# If this doesn't work, try: f"{phone_number}@mypixmessages.com"
sms_gateway_address = f"{phone_number}@vtext.com"

# Gmail SMTP Configuration
smtp_server = "smtp.gmail.com"
smtp_port = 465  # For SSL
sender_email = "notifymail225@gmail.com"
# IMPORTANT: This is your Gmail App Password
email_app_password = "dbkv iqyq tciq ouwo"

# --- END USER CONFIGURATION ---

def send_sms(message_body: str):
    """
    Sends an SMS to the configured phone number via Gmail SMTP.
    """
    if not message_body:
        print("Error: Message body cannot be empty.")
        return

    msg = EmailMessage()
    # SMS gateways usually only care about the body, subject is often ignored or prepended.
    # For simplicity, we'll just set the body.
    msg.set_content(message_body)
    msg['To'] = sms_gateway_address
    msg['From'] = sender_email # Some gateways might require the 'From' to be the same as login

    print(f"Attempting to send SMS to {sms_gateway_address} from {sender_email}...")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, email_app_password)
            server.send_message(msg)
        print("SMS notification sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Failed to login. Check sender_email and email_app_password.")
        print("Ensure you are using a valid Gmail App Password if 2-Step Verification is enabled.")
    except smtplib.SMTPServerDisconnected:
        print("SMTP Server Disconnected: Could not connect to the server. Check server address and port.")
    except smtplib.SMTPException as e:
        print(f"SMTP Error: An error occurred while sending the email: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Get message from user input
    custom_message = input("Enter the message you want to send as an SMS: ")
    if custom_message:
        send_sms(custom_message)
    else:
        print("No message entered. Exiting.")

import os
import smtplib
from email.message import EmailMessage

EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)


def send_email(subject: str, body: str, to_email: str):
    """
    Sends an email using SMTP.
    If EMAIL_ENABLED is false or credentials are missing, prints the email instead.
    """
    if not EMAIL_ENABLED or not all([SMTP_USER, SMTP_PASS, EMAIL_FROM]):
        print(f"[DEV MODE] Email to {to_email} - Subject: {subject}, Body: {body}")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"[PROD MODE] Email sent to {to_email}.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


def send_otp_email(otp: str, to_email: str):
    """
    Sends an OTP email.
    """
    subject = "Your OTP Code"
    body = f"Your OTP is {otp}."
    return send_email(subject, body, to_email)


def send_order_decline_email(reason: str, to_email: str):
    """
    Sends an order decline notification via email.
    """
    subject = "Order Declined"
    body = (
        f"Your order has been declined due to: '{reason}'.\n"
        "If you have any questions, feel free to contact 8008692727."
    )
    return send_email(subject, body, to_email)



# import os
# from twilio.rest import Client

# TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() == "true"
# TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

# def send_otp_sms(otp: str, phone_number: str):
#     """
#     Sends OTP via SMS using Twilio or logs it in development mode.
#     """
#     if not TWILIO_ENABLED or not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE]):
#         print(f"[DEV MODE] OTP for {phone_number} is {otp}")
#         return

#     try:
#         client = Client(TWILIO_SID, TWILIO_TOKEN)
#         message = client.messages.create(
#             body=f"Your OTP is {otp}",
#             from_=TWILIO_PHONE,
#             to=phone_number
#         )
#         print(f"[PROD MODE] OTP sent to {phone_number}. SID: {message.sid}")
#         return message.sid
#     except Exception as e:
#         print(f"[ERROR] Failed to send OTP: {e}")


# def send_order_decline_sms(reason: str, phone_number: str):
#     message_body = (
#         f"Your order has been declined due to: '{reason}'. "
#         "If you have any questions, feel free to contact 8008692727."
#     )

#     if not TWILIO_ENABLED or not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE]):
#         print(f"[DEV MODE] SMS to {phone_number}: {message_body}")
#         return

#     try:
#         client = Client(TWILIO_SID, TWILIO_TOKEN)
#         message = client.messages.create(
#             body=message_body,
#             from_=TWILIO_PHONE,
#             to=phone_number
#         )
#         print(f"[PROD MODE] SMS sent to {phone_number}. SID: {message.sid}")
#         return message.sid
#     except Exception as e:
#         print(f"[ERROR] Failed to send SMS: {e}")

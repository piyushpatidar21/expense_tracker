import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(receiver_email: str, subject: str, body: str):
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = receiver_email

    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)

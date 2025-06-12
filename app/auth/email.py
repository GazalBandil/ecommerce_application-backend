import os
import smtplib
from email.message import EmailMessage

def send_email(to_email: str, subject: str, body: str):
    sender = os.getenv("SMTP_USER")
    app_password = os.getenv("SMTP_PASS")  # 16-character Gmail App Password

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)

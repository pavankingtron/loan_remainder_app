import os
import smtplib
from email.message import EmailMessage


class EmailService:

    def __init__(self):
        self.email = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")

    def send_email(self, to_email, subject, message):

        try:
            msg = EmailMessage()

            msg["From"] = self.email
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.set_content(message)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            print("Email Error:", e)
            return False

from flask import Flask, request
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
from urlmatch import urlmatch

load_dotenv()
app = Flask(__name__)


class MailClient:
    def __init__(self):
        self.server = smtplib.SMTP(
            os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))
        )
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))

    def send_mail(self, mail, subject, reply_to, message):
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = os.getenv("MAIL_USERNAME")
        msg["To"] = mail
        msg["Reply-To"] = reply_to
        self.server.send_message(msg)

    def quit(self):
        self.server.quit()

    def __del__(self):
        try:
            self.quit()
        except Exception:
            pass


client = MailClient()


ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS").split(",")]


@app.post("/<mail>")
def send_mail(*args, **kwargs):
    if not any([urlmatch(host, request.host) for host in ALLOWED_HOSTS]):
        return "Unauthorized", 401

    mail = kwargs.get("mail")
    subject = request.json.get("_subject")
    reply_to = request.json.get("_replyto")
    message = request.json.get("message")
    if mail is None or subject is None or reply_to is None or message is None:
        return "Missing arguments", 400
    client.send_mail(mail, subject, reply_to, message)
    return "OK", 200


@app.get("/")
def index():
    return "<h1>FormSubmitter is running</h1>", 200


if __name__ == "__main__":
    app.run(host=os.getenv("HOST"), port=int(os.getenv("PORT")))
    client.quit()

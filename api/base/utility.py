from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import threading
import re
import phonenumbers


import phonenumbers ### this library is for country code and number of phone number 

### below libraries are for twilio
from twilio.rest import Client
from decouple import config



regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
regex_phone = re.compile(r"^(\+\d{3})?\s?\(?\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
regex_username = re.compile(r'^[a-zA-Z_]\w{2,19}$')

############################################################ Email sending message with thread
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self=self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["subject"], body=data["body"], to=[data["to_email"]]
        )
        if data.get("content_type") == "html":
            email.content_subtype = "html"

        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string("email/send_email_code.html", {"code": code})
    Email.send_email(
        {
            "subject": "Instagram ro'yhatdan o'tish",
            "body": html_content,
            "to_email": email,
            "content_type": "html",
        }
    )
############################################################


def check_username(username):
    if re.fullmatch(regex_username, username):
        return True
    else:
        return False

def check_user_type(user_input):
    if (re.fullmatch(regex, user_input)):
        return 'email'
    
    elif (re.fullmatch(regex_username, user_input)):
        return "username"

    phone_number = phonenumbers.parse(user_input)
    if phonenumbers.is_valid_number(phone_number):
        return 'phone'
    

    else:
        return False


def send_phone_code(phone, code):
    account_sid = config("account_sid")
    auth_token = config("auth_token")
    client = Client(account_sid=account_sid, auth_token=auth_token)

    client.messages.create(
        body=f"Salom! Sizning codeingiz: {code}\n",
        from_="+998908533642",
        to=f"{phone}"
    )
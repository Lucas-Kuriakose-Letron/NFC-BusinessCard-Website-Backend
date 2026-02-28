import smtplib
from email.mime.text import MIMEText


class Emailer:
    sender_email   = "kuriakose.biji@gmail.com"
    sender_password = "kadn velr fhkh skqn"

def setup_email(gmail_address, app_password):
    Emailer.sender_email = gmail_address
    Emailer.sender_password = app_password

def send_email(to_address, subject, body):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = Emailer.sender_email
    message["To"]= to_address
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(Emailer.sender_email, Emailer.sender_password)
            server.sendmail(Emailer.sender_email, to_address, message.as_string())
    except Exception as error:
        print("[Email error]", error)
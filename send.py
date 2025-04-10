# Send all the extracted files to the specified email
import smtplib, ssl, os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DIRECTORY = os.path.abspath(os.path.dirname(__file__))
ERROR_LOG = os.path.join(DIRECTORY, "logs/error_log.txt")

class Send:
    
    sender_email = None
    password = None
    receiver_email = None
    subject_prefix = "Job Postings from "
    host = "smtp.gmail.com"
    port = 465
    
    def send_all_extracts():
        send_ajo_extract()
        send_chronicle_extract()
        send_naaee_extract()
    
        return 0


def send_ajo_extract():

    filename = os.path.join(DIRECTORY, "extracts/ajo_postings.txt")   
     
    message = MIMEMultipart()
    subject_suffix = "Academic Jobs Online"
    
    body = ""
    with open(filename, "r", encoding="utf-8") as file:
        body = file.read()

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    send_extract(message, subject_suffix)

    return 0

def send_chronicle_extract():
    
    filename = os.path.join(DIRECTORY, "extracts/chronicle_postings.txt")   
     
    message = MIMEMultipart()
    subject_suffix = "Chronicle of Higher Education Jobs"
    
    body = ""
    with open(filename, "r", encoding="utf-8") as file:
        body = file.read()

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    send_extract(message, subject_suffix)
    
    return 0

def send_naaee_extract():
    
    filename = os.path.join(DIRECTORY, "extracts/naaee_postings.txt")   
     
    message = MIMEMultipart()
    subject_suffix =  "NAAEE Jobs"
    
    body = ""
    with open(filename, "r", encoding="utf-8") as file:
        body = file.read()

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    send_extract(message, subject_suffix)
    
    return 0

def send_extract(message, subject_suffix):
    
    message["From"] = Send.sender_email
    message["To"] = Send.receiver_email
    message["Subject"] = Send.subject_prefix + subject_suffix
    
    filename = os.path.join(DIRECTORY, "signature.txt")

    signature = ""
    with open(filename, "r") as file:
        signature = file.read()
    
    message.attach(MIMEText(signature, "html"))

    text = message.as_string()
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(Send.host, Send.port, context=context) as server:
        server.login(Send.sender_email, Send.password)
        server.sendmail(Send.sender_email, Send.receiver_email, text)
    
    return 0


if __name__ == "main":
    Send.send_all_extracts()
# Send all the extracted files to the specified email
import smtplib, ssl, datetime, os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_ajo_extract(sender_email, password, receiver_email, subject_prefix, host, port):

    directory = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(directory, "extracts/ajo_postings.txt")   
     
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject_prefix + "Academic Jobs Online"
    
    text = ""
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

    # Add body to email
    message.attach(MIMEText(text, "plain"))

    send_extract(message, sender_email, password, receiver_email, host, port)

    return 0

def send_chronicle_extract(sender_email, password, receiver_email, subject_prefix, host, port):
    
    directory = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(directory, "extracts/chronicle_postings.txt")   
     
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject_prefix + "Chronicle of Higher Education Jobs"
    
    text = ""
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

    # Add body to email
    message.attach(MIMEText(text, "plain"))

    send_extract(message, sender_email, password, receiver_email, host, port)
    
    return 0

def send_naaee_extract(sender_email, password, receiver_email, subject_prefix, host, port):
    
    directory = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(directory, "extracts/naaee_postings.txt")   
     
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject_prefix + "NAAEE Jobs"
    
    text = ""
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()

    # Add body to email
    message.attach(MIMEText(text, "plain"))

    send_extract(message, sender_email, password, receiver_email, host, port)
    
    return 0

def send_extract(message, sender_email, password, receiver_email, host, port):
    
    salutation = "<html><body><b><i>--Courtesy of your friendly neighborhood Spider-Dev</i></b></body></html>"
    
    message.attach(MIMEText(salutation, "html"))

    text = message.as_string()
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    
    return 0

def send_all_extracts(sender_email, password, receiver_email, subject_prefix, host, port):
    send_ajo_extract(sender_email, password, receiver_email, subject_prefix, host, port)
    send_chronicle_extract(sender_email, password, receiver_email, subject_prefix, host, port)
    send_naaee_extract(sender_email, password, receiver_email, subject_prefix, host, port)
    
    return 0

if __name__ == "main":
    send_all_extracts()
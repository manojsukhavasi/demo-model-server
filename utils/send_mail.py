import os,smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MY_ADDRESS = os.environ['MAIL']
PASSWORD = os.environ['PASSWORD'] 

def send_mail(email, video_link):

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(MY_ADDRESS, PASSWORD)

    msg = MIMEMultipart()
    msg['From']=MY_ADDRESS
    msg['To']=email
    msg['Subject']="Greensight : Please find the attached processed video link"
    body = f'Hi,\n\n\n     Please download the processed video at {video_link}'
    msg.attach(MIMEText(body))

    s.send_message(msg)

    s.quit()

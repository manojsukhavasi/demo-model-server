import os,smtplib,argparse

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

    me = MY_ADDRESS
    to = email
    bcc = "manoj.sukhavasi1@gmail.com, anvesh@greensight.ai"
    rcpt = bcc.split(',') + [to]

    msg = MIMEMultipart()
    msg['To']=email
    msg['Subject']="Greensight: Please find the attached processed video link"
    body = f'Hi,\n\n\n    Please download the processed video and top 10 highlight clips at {video_link}\n\n    Please feel free to give feedback/suggestions by replying to this email.'
    msg.attach(MIMEText(body))

    #s.send_message(msg)
    s.sendmail(me, rcpt, msg.as_string())

    s.quit()

if __name__=="__main__":
    parser  = argparse.ArgumentParser()

    parser.add_argument('-m', '--mail', help='Youtube url')

    args = parser.parse_args()
    send_mail(args.mail, 'Sample')

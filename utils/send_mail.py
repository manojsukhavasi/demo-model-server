import os,smtplib,argparse

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MY_ADDRESS = os.environ['MAIL']
PASSWORD = os.environ['PASSWORD'] 

def send_mail(email, video_link, zip_link):

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(MY_ADDRESS, PASSWORD)

    me = MY_ADDRESS
    to = email
    bcc = "manoj@greensight.ai, anvesh@greensight.ai"
    rcpt = bcc.split(',') + [to]

    msg = MIMEMultipart()
    msg['To']=email
    msg['Subject']="Greensight: Please find the attached processed video link"
    body = f'Hi,\n\n\nPlease download the processed video at {video_link} and top 10 highlight clips at {zip_link}\n\nPlease feel free to give feedback/suggestions by replying to this email.\n\n\nCheers,\nGreensight'
    msg.attach(MIMEText(body))

    #s.send_message(msg)
    s.sendmail(me, rcpt, msg.as_string())

    s.quit()

def send_confirmation_mail(email, video_url):

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(MY_ADDRESS, PASSWORD)

    me = MY_ADDRESS
    to = email
    bcc = "manoj@greensight.ai, anvesh@greensight.ai"
    rcpt = bcc.split(',') + [to]

    msg = MIMEMultipart()
    msg['To']=email
    msg['Subject']="Greensight: Confirmation of your demo request"
    body = f'Hi,\n\nThis is confirmation that we have received your request to generate highlights for the video {video_url}\n\nProcessing time varies but typically takes about 1hr for 1hr of footage (It will be worth the wait. Promise! ).\n\n\nCheers,\nGreensight'
    msg.attach(MIMEText(body))

    #s.send_message(msg)
    s.sendmail(me, rcpt, msg.as_string())

    s.quit()


if __name__=="__main__":
    parser  = argparse.ArgumentParser()

    parser.add_argument('-m', '--mail', help='Youtube url')

    args = parser.parse_args()
    send_confirmation_mail(args.mail, 'https://youtube.com')

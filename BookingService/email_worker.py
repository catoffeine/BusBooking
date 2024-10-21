import smtplib as smtp
from getpass import getpass

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from myauth.models import GET_VAR

ATTACHMENT_NAME = 'отчет.xlsx'
email = GET_VAR('email-login')
password = GET_VAR('email-password')


def send_email(user=None, subject=None, message=None, attachfile=None):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = user.email
    msg.attach(MIMEText(message))

    if attachfile is not None:
        with open(attachfile, 'rb') as f:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('content-disposition', 'attachment', filename=('utf-8', '', ATTACHMENT_NAME))
            msg.attach(part)
    s = smtplib.SMTP_SSL('smtp.yandex.com')
    s.login(email, password)
    s.sendmail(email, user.email, msg.as_string())
    s.quit()

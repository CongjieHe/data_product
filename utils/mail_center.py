# -*- coding: utf-8 -*-
# @Time       : 2021/11/6 0:25
# @Author     : CongjieHe
# @Email      : congjiehe95@gmail.com
# @LastChange : 2021/11/6

import warnings
import smtplib
from httplib2 import socks
import socket
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import unittest
import os
import sys

sys.path.append(os.getcwd())

from config import *
from config.email_config import MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASS, MAIL_RECEIVER

# socket.socket = socks.socksocket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 10808)


class EmailCenter:
    def __init__(self, subject=None, header=None):
        self.mail_host = MAIL_HOST
        self.mail_port = MAIL_PORT
        self.mail_user = MAIL_USER
        self.mail_pass = MAIL_PASS
        self.mail_rec = MAIL_RECEIVER
        self.subject = subject
        self.header = header

    def send_img(self, title, imgs):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(self.subject, 'utf-8')
        msg['From'] = Header(self.header, 'utf-8')
        ss = ""
        for img in imgs:
            msgImage = MIMEImage(img.read())
            img.close()
            msgImage.add_header('Content-ID', title)
            ss = ss + """<br><img src="cid:%s"></br>\n""" % title
            msg.attach(msgImage)
        html = """
         <html>
             <head></head>
             <body>
                 <p>This email was sent by env: %s ：<br>
                     %s              
                 </p>
             </body>
         </html>
         """ % (RUN_ENV, ss)
        message = MIMEText(html, "html", "utf-8")
        msg.attach(message)
        try:
            smtpObj = smtplib.SMTP_SSL(MAIL_HOST)
            smtpObj.connect('pop.exmail.qq.com', 465)
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.mail_user, self.mail_rec, msg.as_string())
        except smtplib.SMTPException as e:
            logger_error.error("UNKNOW error happened ,send email failed")
            logger_error.error(str(e))
        else:
            logger_info.info("send email success")


class TestMailSend(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        print("Begin testing email sender")

    @classmethod
    def tearDownClass(cls) -> None:
        print("End to test email sender")

    def test_send_email(self):
        subject = 'Python SMTP 邮件测试'
        email = EmailCenter()
        message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
        message['From'] = Header("数据服务器", 'utf-8')
        message['To'] = Header("测试", 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')

        try:
            # pass
            smtpObj = smtplib.SMTP_SSL(email.mail_host)
            smtpObj.connect(email.mail_host, email.mail_port)
            smtpObj.login(email.mail_user, email.mail_pass)
            smtpObj.sendmail(email.mail_user, email.mail_rec, message.as_string())
            smtpObj.quit()
            smtpObj.close()
        except smtplib.SMTPException as e:
            print(e)
            print("Unknown error happened, send email failed")
        else:
            print("send email success")


if __name__ == '__main__':
    unittest.main()

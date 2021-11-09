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

from config import *

from config.email_config import MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASS, MAIL_RECEIVER

socket.socket = socks.socksocket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 10808)


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

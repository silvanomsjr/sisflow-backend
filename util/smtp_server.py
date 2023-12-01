"""
SMTP Server

Allows sending mail messages
"""
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import logging
import smtplib
import os
import threading
import time

logging = logging.getLogger(__name__)

# Creates a smtp server thread to asynchronous send mails from a mail list
class SmtpServer:

    def __init__(self):
        self.smtp_server = None
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_login = None
        self.smtp_password = None
        self.finish_thread = False
        self.server_ready = False
        self.mail_list = []
    
    # Starts thread to run smtp server for sending mails, self is shared
    def start(self, smtp_host, smtp_port, smtp_login, smtp_password):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_login = smtp_login
        self.smtp_password = smtp_password
        threading.Thread(target = self.__run).start()

    # Private method used by thread to run smtp server asynchronous
    def __run(self):
        self.__connect_SMTP()
        self.__awaits_for_mail_list()

    # Creates a SMTP connection to host and port with login credentials
    def __connect_SMTP(self):
        self.smtp_server = smtplib.SMTP(
            self.smtp_host,
            self.smtp_port
        )

        self.smtp_server.ehlo()
        self.smtp_server.starttls()

        self.smtp_server.login(
            self.smtp_login,
            self.smtp_password
        )

        self.server_ready = True
        logging.info(f'Smtp thread {threading.get_ident()}: Connection to SMTP successfull')
  
    # Awaits for appends to mail list
    def __awaits_for_mail_list(self):
        while self.finish_thread == False:
            if len(self.mail_list) > 0:
                self.__send_mail(self.mail_list[0])
                del self.mail_list[0]
            else:
                time.sleep(1)

    # Sends mail from mail object
    #   if an exception occur, restart conection and try again(avoid disconnection by timeout)
    def __send_mail(self, mailobj):

        logging.info(f'Smtp thread {threading.get_ident()}: Sending mail to {mailobj["email_to"]}')

        exception_ocurred = False
        try:
            self.smtp_server.sendmail(self.smtp_login, mailobj['email_to'], mailobj['mm_mail_body'])
        except Exception as e:
            exception_ocurred = True
            self.__connect_SMTP()

        if exception_ocurred:
            self.smtp_server.sendmail(self.smtp_login, mailobj['email_to'], mailobj['mm_mail_body'])
        logging.info(f'Smtp thread {threading.get_ident()}: Done')
    
    # Append a mail object to the mail_list, python append() is thread safe
    def add_email(self, raw_to, raw_subject, raw_body):
        
        email_to, subject, body = self.mail_args_format(raw_to, raw_subject, raw_body)
        mm_mail_body = self.mail_mime_multipart_format(email_to, subject, body)
        self.mail_list.append({'email_to': email_to, 'mm_mail_body': mm_mail_body})

    # Stops thread
    def stop(self):
        self.finish_thread = True

    @staticmethod
    def mail_args_format(raw_to, raw_subject, raw_body):

        to = raw_to
        subject = raw_subject

        with open('./templates/smtpMailTemplate.html', 'r', encoding="utf8") as f:
            template_Html = f.read()

            soup = BeautifulSoup(template_Html, 'html.parser')
            div_top_content = soup.find('div', id='top-content')
            div_bottom_content = soup.find('div', id='bottom-content')
            btn_content = soup.find('tr', id="button-content")

            div_top_content.append(BeautifulSoup(raw_body, 'html.parser'))
            btn_content.append(BeautifulSoup(
                f'''<td> <a href="{os.getenv("FRONT_URL")}" target="_blank">Acessar o SisFlow</a> </td>''', 
                'html.parser')
            )
        
            if os.getenv("SYS_DEBUG") == "True":
                to = os.getenv("SMTP_LOGIN")
                div_bottom_content.append(BeautifulSoup(
                    f"""
                    <p> Modo de testes ativo </p>
                    <p> Deveria ser enviado a este email: {raw_to} </p>
                    """
                    , 'html.parser')
                )
    
        return to, subject, soup.prettify()

    @staticmethod
    def mail_mime_multipart_format(to, subject, body):

        mm_mail = MIMEMultipart()
        mm_mail["From"] = os.getenv("SMTP_LOGIN")
        mm_mail["To"] = to
        mm_mail["Subject"] = subject
        mm_mail.attach(MIMEText(body, "html"))

        return mm_mail.as_string()
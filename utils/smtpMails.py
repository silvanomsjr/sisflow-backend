from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import threading
import time

systemSmtpServer = None

def startSmtpServer():

  global systemSmtpServer

  if systemSmtpServer == None:
    systemSmtpServer = SmtpServer()

def addToSmtpMailServer(rawTo, rawSubject, rawBody):

  global systemSmtpServer

  if systemSmtpServer == None:
    systemSmtpServer = SmtpServer()

  to, subject, body = mailArgsFormat(rawTo, rawSubject, rawBody)
  mmMail = mailMIMEMultipartFormat(to, subject, body)

  systemSmtpServer.appendToMailList(to, mmMail)

def stopSmtpServer():

  global systemSmtpServer

  if systemSmtpServer != None:
    systemSmtpServer.stop()

def mailArgsFormat(rawTo, rawSubject, rawBody):

  to = rawTo
  subject = rawSubject

  with open('./utils/smtpMailTemplate.html', 'r', encoding="utf8") as f:
    templateHtml = f.read()

    soup = BeautifulSoup(templateHtml, 'html.parser')
    divTopContent = soup.find('div', id='top-content')
    divBottomContent = soup.find('div', id='bottom-content')
    btnContent = soup.find('tr', id="button-content")

    divTopContent.append(BeautifulSoup(rawBody, 'html.parser'))
    btnContent.append(BeautifulSoup(
      f'''<td> <a href="{os.getenv("FRONT_BASE_URL")}" target="_blank">Acessar o Sisges</a> </td>''', 
      'html.parser'))
    
    if os.getenv("SYS_DEBUG") == "True":
      to = os.getenv("SMTP_LOGIN")
      divBottomContent.append(BeautifulSoup(
        f"""
          <p> Modo de testes ativo </p>
          <p> Deveria ser enviado a este email: {rawTo} </p>
        """
        , 'html.parser'))
  
  return to, subject, soup.prettify()

def mailMIMEMultipartFormat(to, subject, body):

  mmMail = MIMEMultipart()
  mmMail["From"] = os.getenv("SMTP_LOGIN")
  mmMail["To"] = to
  mmMail["Subject"] = subject
  mmMail.attach(MIMEText(body, "html"))

  return mmMail.as_string()

# Creates a smtp server thread to asynchronous send mails from a mail list
class SmtpServer:

  # Starts thread to run smtp server for sending mails, self is shared
  def __init__(self):
    self.finishThread = False
    self.mailList = []
    threading.Thread(target = self.__run).start()

  # Private method used by thread to run smtp server asynchronous
  def __run(self):
    self.__connectSMTP()
    self.__awaitsForMailList()

  # Creates a SMTP connection to host and port with login credentials
  def __connectSMTP(self):
    self.smtpServer = smtplib.SMTP(
      os.getenv("SMTP_HOST"),
      os.getenv("SMTP_PORT"))

    self.smtpServer.ehlo()
    self.smtpServer.starttls()

    self.smtpServer.login(
      os.getenv("SMTP_LOGIN"),
      os.getenv("SMTP_PASSWORD"))
    
    print(f'# Smtp thread {threading.get_ident()}: Connection to SMTP successfull')
  
  # Awaits for appends to mail list
  def __awaitsForMailList(self):

    while self.finishThread == False:
      if len(self.mailList) > 0:
        self.__sendMail(self.mailList[0])
        del self.mailList[0]
      else:
        print(f'# Smtp thread {threading.get_ident()}: # Awaiting for mails')
        time.sleep(10)

  # Sends mail from mail object
  #   if an exception occur, restart conection and try again(avoid disconnection by timeout)
  def __sendMail(self, mailObj):

    print(f'# Smtp thread {threading.get_ident()}: Sending mail to {mailObj["emailTo"]}')
    exceptionOcurred = False
    try:
      self.smtpServer.sendmail(os.getenv("SMTP_LOGIN"), mailObj['emailTo'], mailObj['mmMailBody'])
    except Exception as e:
      exceptionOcurred = True
      self.__connectSMTP()

    if exceptionOcurred:
      self.smtpServer.sendmail(os.getenv("SMTP_LOGIN"), mailObj['emailTo'], mailObj['mmMailBody'])
    print(f'# Smtp thread {threading.get_ident()}: Done!')
  
  # append a mail object to the mailList, python append() is thread safe
  def appendToMailList(self, emailTo, mmMailBody):
    self.mailList.append({'emailTo': emailTo, 'mmMailBody': mmMailBody})

  # Stops thread
  def stop(self):
    self.finishThread = True
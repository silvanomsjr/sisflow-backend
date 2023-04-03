import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread

import os

smtpServer = None

def smtpStart():

  global smtpServer

  smtpServer = smtplib.SMTP(
    os.getenv("SMTP_HOST"),
    os.getenv("SMTP_PORT"))

  smtpServer.ehlo()
  smtpServer.starttls()

  smtpServer.login(
    os.getenv("SMTP_LOGIN"),
    os.getenv("SMTP_PASSWORD"))

  print("# Connection to SMTP successfull")

def smtp_working():

  global smtpServer
  
  try:
    status = smtpServer.noop()[0]
  except:  # smtplib.SMTPServerDisconnected
    status = -1

  if status == 250:
    return True
  return False

def smtpSend(mailTo, mailSubject, mailInnerHtml):
  Thread(target=smtpSendTask, args=(mailTo, mailSubject, mailInnerHtml)).start()

def smtpSendTask(mailTo, mailSubject, mailInnerHtml):

  global smtpServer
  
  print(mailTo, mailSubject, mailInnerHtml)

  if not smtpServer:
    print("# Smtp not started")
    return

  if not smtp_working():
    smtpStart()
    if not smtp_working():
      print("# Could not reconnect to smtp")
      return

  mailToTmp = None
  mailHtml = None
  if os.getenv("SYS_DEBUG") == "True":
    mailToTmp = os.getenv("SMTP_LOGIN")
    mailHtml = f'''
    <!DOCTYPE html><html><body><h1 style="color:blue;">Sisges</h1>
    {mailInnerHtml}
    <br><p> Modo de testes ativo </p><p> Deveria ser enviado a este email: {mailTo} </p>
    </body></html>
    '''
  else:
    mailToTmp = mailTo
    mailHtml = f'''
    <!DOCTYPE html><html><body><h1 style="color:blue;">Sisges</h1>
    {mailInnerHtml}
    </body></html>
    '''

  mail = MIMEMultipart()
  mail["From"] = os.getenv("SMTP_LOGIN")
  mail["To"] = mailToTmp
  mail["Subject"] = mailSubject
  mail.attach(MIMEText(mailHtml, "html"))

  smtpServer.sendmail(
    os.getenv("SMTP_LOGIN"),
    mailToTmp,
    mail.as_string())

  return
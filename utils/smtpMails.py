from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os

from threading import Thread

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

def isSmtpWorking():

  global smtpServer

  if not smtpServer:
    smtpStart()
    if not smtpServer:
      print("# Could not reconnect to smtp local server")
      return False
  
  try:
    status = smtpServer.noop()[0]
  except:  # smtplib.SMTPServerDisconnected
    status = -1

  if status == 250:
    return True
  return False

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

def smtpSend(rawTo, rawSubject, rawBody):

  global smtpServer

  if not isSmtpWorking:
    return

  to, subject, body = mailArgsFormat(rawTo, rawSubject, rawBody)
  mmMail = mailMIMEMultipartFormat(to, subject, body)

  smtpServer.sendmail(os.getenv("SMTP_LOGIN"), to, mmMail)
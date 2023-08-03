import traceback

from utils.dbUtils import *
from utils.sistemConfig import getCoordinatorEmail
from utils.smtpMails import addToSmtpMailServer
from utils.utils import sistemStrParser

def sendSolicitationMails(solicitationId, studentData):
  
  try:
    solicitationMails = dbGetAll(
      " SELECT dm.mail_subject, dm.mail_body_html, dm.is_sent_to_student, dm.is_sent_to_advisor, dm.is_sent_to_coordinator "
      "   FROM solicitation AS s "
      "     JOIN solicitation_start_mail AS ssm ON s.id = ssm.solicitation_id "
      "     JOIN dynamic_mail AS dm ON ssm.dynamic_mail_id = dm.id "
      "     WHERE s.id = %s; ",
    [(solicitationId)])
  except Exception as e:
    print("# Database reading error:")
    print(e)
    traceback.print_exc()
    return False
  
  return sendMails(solicitationMails, studentData)

def sendTransitionMails(transitionId, studentData=None, advisorData=None):
  try:
    transitionMails = dbGetAll(
      " SELECT dm.mail_subject, dm.mail_body_html, dm.is_sent_to_student, dm.is_sent_to_advisor, dm.is_sent_to_coordinator "
      "   FROM solicitation_state_transition AS sst "
      "     JOIN solicitation_state_transition_mail AS sstm ON sst.id = sstm.solicitation_state_transition_id "
      "     JOIN dynamic_mail AS dm ON sstm.dynamic_mail_id = dm.id "
      "     WHERE sst.id = %s; ",
      [(transitionId)])
  except Exception as e:
    print("# Database reading error:")
    print(e)
    traceback.print_exc()
    return False
  
  return sendMails(transitionMails, studentData, advisorData)

def sendMails(mailList, studentData=None, advisorData=None):
  
  try:
    for mail in mailList:
      
      # treat mail subject and body
      parsedSubject = sistemStrParser(mail["mail_subject"], studentData, advisorData)
      parsedBody = sistemStrParser(mail["mail_body_html"], studentData, advisorData)

      if mail["is_sent_to_student"]:
        addToSmtpMailServer(studentData['institutional_email'], parsedSubject, parsedBody)

      if mail["is_sent_to_advisor"]:
        addToSmtpMailServer(advisorData['institutional_email'], parsedSubject, parsedBody)

      if mail["is_sent_to_coordinator"]:
        addToSmtpMailServer(getCoordinatorEmail(), parsedSubject, parsedBody)

  except Exception as e:
    print("# Smtp sending error:")
    print(e)
    traceback.print_exc()
    return False

  return True
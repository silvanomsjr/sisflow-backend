from datetime import datetime, timedelta
import json
import threading
import traceback

import service.scheduleService
import service.sendMailService
import service.transitionService

from utils.dbUtils import *
from utils.utils import getFormatedMySQLJSON

### Validation methods ###
def getDPageComponentsInvalidMsg(components):

  for component in components:

    # Checks if all required inputs are valid
    if component["component_type"] == "input" and component["input_required"]:
      found = False
      
      for userInput in solicitationUserData['inputs']:
        if userInput["input_name"] == component["input_name"]:
          found = True
        
      if not found:
        return "Input da solicitação está faltando!"

    # Checks if all required uploads are valid
    if component["component_type"] == "upload" and component["upload_required"]:
      found = False

      for userUpload in solicitationUserData["uploads"]:

        if userUpload["upload_name"] == component["upload_name"]:
          try:
            if dbGetSingle(
                " SELECT att.hash_name "
                "   FROM attachment AS att JOIN user_has_attachment AS uhatt ON att.id = uhatt.attachment_id "
                "   WHERE uhatt.user_id = %s AND att.hash_name = %s; ",
                [userData["user_id"], userUpload["upload_hash_name"]]):
              found = True
              break
          except Exception as e:
            print("# Database reading error:")
            print(e)
            traceback.print_exc()
            return "Erro na base de dados"
              
      if not found:
        return "Anexo da solicitação está faltando!"
            
    # Checks if all required select uploads are valid - incomplete
    if component["component_type"] == "select_upload" and component["select_upload_required"]:
      pass

    return None

def getUserSolStateChangeInvalidMsg(userData, studentData, advisorData, solStateData):

  # if not adm check if is student or advisor
  if not "ADM" in userData["profile_acronyms"] and not "COO" in userData["profile_acronyms"]:
    if userData["user_id"] != studentData["user_id"] and userData["user_id"] != advisorData["user_id"]:
      return "Edição a solicitação não permitida!"
  
  # checks if profile is allowed to change solicitation
  profileCanEdit = False
  for profileEditor in solStateData["profile_acronyms"].split(','):
    if profileEditor in userData["profile_acronyms"]:
      profileCanEdit = True
  if not profileCanEdit:
    return "Perfil editor a solicitação inválido!"
  
  # Valid
  return None

def getSolStateChangeInvalidMsg(solStateData):

  # check if the actual changeable state is the requested state
  if solStateData["actual_solicitation_state_id"] != solStateData["solicitation_state_id"]:
    return "Edição do estado da solicitação não permitido!"

  # data validation
  if solStateData["start_datetime"] and datetime.now() < solStateData["start_datetime"]:
    return "Esta etapa da solicitação não foi iniciada!"
  if solStateData["end_datetime"] and datetime.now() > solStateData["end_datetime"]:
    return "Esta etapa da solicitação foi expirada!"
  
  # status validation
  if solStateData["decision"] != "Em analise":
    return "Esta solicitação já foi realizada!"
  
  # Valid
  return None

### Database reading methods ###
def getSolStateDataByUserStateId(userHasStateId):

  try:
    solStateData = dbGetSingle(
      " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, uc_stu.institutional_email AS student_institutional_email, "
      " uc_stu.secondary_email AS student_secondary_email, uc_stu.gender AS student_gender, "
      " uc_stu.phone AS student_phone, uc_stu.creation_datetime AS student_creation_datetime, "
      " uhpsd.matricula AS student_matricula, uhpsd.course AS student_course, "

      " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, uc_adv.institutional_email AS advisor_institutional_email, "
      " uc_adv.secondary_email AS advisor_secondary_email, uc_adv.gender AS advisor_gender, uc_adv.phone AS advisor_phone, "
      " uc_adv.creation_datetime AS advisor_creation_datetime, uhpad.siape AS advisor_siape, 3 AS advisor_students, "

      " uhs.id AS user_has_solicitation_id, uhs.solicitation_id, uhs.actual_solicitation_state_id, uhs.solicitation_user_data, "
      " uhss.id AS user_has_solicitation_state_id, uhss.solicitation_state_id, uhss.decision, uhss.start_datetime, uhss.end_datetime, "
      " sspe.profile_acronyms, "
      " dp.id AS page_id "
      "   FROM user_account AS uc_stu "
      "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
      "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
      "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
      "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
      "     JOIN solicitation_state AS ss ON uhss.solicitation_state_id = ss.id "
      "     LEFT JOIN dynamic_page AS dp ON ss.state_dynamic_page_id = dp.id "
      "     LEFT JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
      "     LEFT JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
      "     LEFT JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
      "     LEFT JOIN ( "
      "       SELECT sspe.solicitation_state_id, "
      "         GROUP_CONCAT(sspe.state_profile_editor) AS state_profile_editors, "
      "         GROUP_CONCAT(p.profile_acronym) AS profile_acronyms "
      "           FROM solicitation_state_profile_editors sspe "
      "           JOIN profile p ON sspe.state_profile_editor = p.id "
      "           GROUP BY sspe.solicitation_state_id) sspe ON ss.id = sspe.solicitation_state_id "
      "   WHERE uhss.id = %s; ",
      [(userHasStateId)])
    
    return solStateData, False
    
  except Exception as e:
    print("# Database reading error:")
    print(e)
    traceback.print_exc()
    return "Erro na base de dados", True

def getTransitionSolStateData(transitionId):

  try:
    solStateData = dbGetSingle(
      " SELECT ss.id AS state_id, ss.state_max_duration_days, sspe.profile_acronyms "
      "   FROM solicitation_state_transition AS sst "
      "     LEFT JOIN solicitation_state AS ss ON sst.solicitation_state_id_to = ss.id "
      "     LEFT JOIN ( "
      "       SELECT sspe.solicitation_state_id, "
      "         GROUP_CONCAT(sspe.state_profile_editor) AS state_profile_editors, "
      "         GROUP_CONCAT(p.profile_acronym) AS profile_acronyms "
      "           FROM solicitation_state_profile_editors sspe "
      "           JOIN profile p ON sspe.state_profile_editor = p.id "
      "           GROUP BY sspe.solicitation_state_id) sspe ON ss.id = sspe.solicitation_state_id "
      "     WHERE sst.id = %s; ",
      (transitionId,))
    
    return solStateData, False

  except Exception as e:
    print("# Database reading error:")
    print(e)
    traceback.print_exc()
    return "Erro na base de dados", True

### Data parsing methods ###
def createProfileDataBySolStateData(solStateData):

  # Student profile token
  studentData={
    "user_id": solStateData["student_id"],
    "institutional_email": solStateData["student_institutional_email"],
    "user_name": solStateData["student_name"],
    "gender": solStateData["student_gender"],
    "profiles": [{
      "profile_acronym":"STU",
      "matricula": solStateData["student_matricula"],
      "course": solStateData["student_course"]
    }]
  }
  # Advisor profile token
  advisorData={
    "user_id": solStateData["advisor_id"],
    "institutional_email": solStateData["advisor_institutional_email"],
    "user_name": solStateData["advisor_name"],
    "gender": solStateData["advisor_gender"],
    "profiles": [{
      "profile_acronym":"ADV",
      "siape": solStateData["advisor_siape"]
    }]
  }

  return studentData, advisorData

def getParsedSolicitationUserData(solStateData, solicitationUserData):

  # parses solicitation data
  oldSolicitationUserData = getFormatedMySQLJSON(solStateData["solicitation_user_data"])
  parsedSolicitationUserData = None
  if oldSolicitationUserData:
    parsedSolicitationUserData = oldSolicitationUserData
  else:
    parsedSolicitationUserData = {
      "inputs": {},
      "uploads": {},
      "select_uploads": {}
    }

  if solicitationUserData:
    for input in solicitationUserData["inputs"]:
      parsedSolicitationUserData["inputs"][input["input_name"]] = input
    for upload in solicitationUserData["uploads"]:
      parsedSolicitationUserData["uploads"][upload["upload_name"]] = upload
    for selectUpload in solicitationUserData["select_uploads"]:
      parsedSolicitationUserData["select_uploads"][selectUpload["select_upload_name"]] = selectUpload
  
  parsedSolicitationUserData = json.dumps(parsedSolicitationUserData)

  return parsedSolicitationUserData

### Resolves solicitation change ###
def resolveSolStateChange(solStateData, solStateTransition, nextSolStateData, parsedSolicitationUserData, studentData, advisorData, dbObjectIns=None):

  # start transaction only if the transaction is internal
  internalTransaction = (dbObjectIns == None)
  if internalTransaction:
    dbObjectIns = dbStartTransactionObj()

  try:
    # updates actual user state
    dbExecute(
      " UPDATE user_has_solicitation_state "
      "   SET decision = %s, reason = %s "
      "   WHERE id = %s; ",
      [
        solStateTransition["transition_decision"],
        solStateTransition["transition_reason"],
        solStateData["user_has_solicitation_state_id"]
      ], True, dbObjectIns)
    
    # remove old events from scheduler
    #service.scheduleService.removeScheduledSolicitation(solStateData["user_has_solicitation_state_id"], True, dbObjectIns)

    # if next state exists
    if solStateTransition["solicitation_state_id_to"]:
      nextStateCreatedDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      nextStateFinishDate = None if not nextSolStateData["state_max_duration_days"] else (datetime.now() + timedelta(days=nextSolStateData["state_max_duration_days"])).strftime("%Y-%m-%d %H:%M:%S")

      nextStateReason = ''
      sendProfileNames = None
      if nextSolStateData["profile_acronyms"]:
        if "STU" in nextSolStateData["profile_acronyms"]:
          sendProfileNames = "aluno"
        if "ADV" in nextSolStateData["profile_acronyms"]:
          sendProfileNames = "orientador" if not sendProfileNames else sendProfileNames + ", orientador"
        if "COO" in nextSolStateData["profile_acronyms"]:
          sendProfileNames = "coordenação de estágios" if not sendProfileNames else sendProfileNames + ", coordenação de estágios"
        if "," in sendProfileNames:
          lastIndex = sendProfileNames.rfind(",")
          sendProfileNames = sendProfileNames[:lastIndex] + " e" + sendProfileNames[lastIndex+1:]

        if sendProfileNames == "coordenação de estágios":
          nextStateReason = "Aguardando a coordenação de estágios"
        else:
          nextStateReason = ("Aguardando o " + sendProfileNames) if sendProfileNames else None
      else:
        nextStateReason = "Finalizado"
        
      # inserts new user state
      dbExecute(
        " INSERT INTO user_has_solicitation_state "
        " (user_has_solicitation_id, solicitation_state_id, decision, reason, start_datetime, end_datetime) VALUES "
        "   (%s, %s, DEFAULT, %s, %s, %s); ",
        [
          solStateData["user_has_solicitation_id"],
          solStateTransition["solicitation_state_id_to"],
          nextStateReason,
          nextStateCreatedDate,
          nextStateFinishDate],
        True, dbObjectIns)

      userHasNextStateId = dbGetSingle("SELECT LAST_INSERT_ID() AS id;", (), True, dbObjectIns)['id']
      nextStateTransitions = service.transitionService.getTransitions(solStateTransition["solicitation_state_id_to"])

      # updates user solicitation data and changes its actual state
      dbExecute(
        " UPDATE user_has_solicitation "
        "   SET actual_solicitation_state_id = %s, solicitation_user_data = %s "
        "   WHERE id = %s; ",
        [
          solStateTransition["solicitation_state_id_to"],
          parsedSolicitationUserData,
          solStateData["user_has_solicitation_id"]
        ], True, dbObjectIns)

      # sets schedule
      service.scheduleService.scheduleTransitions(userHasNextStateId, nextStateTransitions, True, dbObjectIns)

    # if next state not exists
    else:
      # updates only user solicitation data
      dbExecute(
        " UPDATE user_has_solicitation "
        "   SET solicitation_user_data = %s "
        "   WHERE id = %s; ",
        [parsedSolicitationUserData, solStateData["user_has_solicitation_id"]], True, dbObjectIns)
      
  except Exception as e:
    if internalTransaction:
      dbRollback(dbObjectIns)
    print("# Database reading error:")
    print(e)
    traceback.print_exc()
    return "Erro na base de dados", 409

  if internalTransaction:
    dbCommit(dbObjectIns)
  print("# Solicitation done!\n# Sending mails")

  service.sendMailService.sendTransitionMails(solStateTransition["id"], studentData, advisorData)
  print("# Operation done!")

  return {}, 200
from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json
import datetime

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.smtpMails import smtpSend
from utils.sistemConfig import getCoordinatorEmail
from utils.utils import getFormatedMySQLJSON, sistemStrParser

# Data from single solicitation
class Solicitation(Resource):

  # get single solicitation and associated dynamic page data
  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs.add_argument("user_has_step_id", location="args", type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    userHasStepId = solicitationsArgs["user_has_step_id"]

    print("\n# Starting get single solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT uhs.user_id, uc_pro.id AS professor_id "
        "   FROM user_has_solicitation_step AS uhss "
        "     JOIN user_has_solicitation AS uhs ON uhss.user_has_solicitation_id = uhs.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "   WHERE uhss.id = %s; ",
        [(userHasStepId)])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if not queryRes:
      abort(401, "Usuario não possui a etapa de solicitação!")

    studentId = queryRes[0]
    professorId = queryRes[1]

    if not "ADM" in tokenData["profile_acronyms"] and not "COO" in tokenData["profile_acronyms"]:
      if tokenData["user_id"] != studentId and tokenData["user_id"] != professorId:
        abort(401, "Acesso a solicitação não permitido!")

    try:
      queryRes = dbGetSingle(
        " SELECT uc_stu.user_name, uc_stu.institutional_email, uc_stu.secondary_email, uc_stu.gender, "
        " uc_stu.phone, uc_stu.creation_datetime, uhpsd.matricula, uhpsd.course, "

        " uc_pro.user_name, uc_pro.institutional_email, uc_pro.secondary_email, uc_pro.gender, "
        " uc_pro.phone, uc_pro.creation_datetime, uhppd.siape, "

        " s.solicitation_name, "
        " ssprof.profile_acronym, ss.step_order_in_solicitation, ss.step_description, ss.step_max_duration_days, "
        " uhs.actual_solicitation_step_order, uhs.solicitation_user_data, "
        " uhss.id, uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "

        " ssp.use_dynamic_page, ssp.static_page_name, "
        " dp.title, dp.top_inner_html, dp.mid_inner_html, dp.bot_inner_html, dp.inputs, dp.downloads, "
        " dp.uploads, dp.select_uploads, dp.is_solicitation_button_active "
        
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_step AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_step AS ss ON ss.id = uhss.solicitation_step_id "
        "     JOIN solicitation_step_page AS ssp ON ss.id = ssp.solicitation_step_id "
        "     LEFT JOIN profile AS ssprof ON ss.step_profile_editor = ssprof.id "
        "     LEFT JOIN dynamic_page AS dp ON ssp.dynamic_page_id = dp.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "   WHERE uc_stu.id = %s AND uhss.id = %s; ",
        [studentId, userHasStepId])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    if not queryRes:
      abort(401, "Usuario não possui a etapa de solicitação!")

    print("# Operation Done!")

    # Refactor this in future
    studentParserToken={
      "user_name": queryRes[0],
      "gender": queryRes[3],
      "profiles": [{
        "profile_acronym":"STU",
        "matricula": queryRes[6],
        "course": queryRes[7]
      }]
    }

    return {
      "student": {
        "user_name": queryRes[0],
        "institutional_email": queryRes[1],
        "secondary_email": queryRes[2],
        "gender": queryRes[3],
        "phone": queryRes[4],
        "creation_datetime": str(queryRes[5]),
        "matricula": queryRes[6],
        "course": queryRes[7]
      },
      "professor": {
        "user_name": queryRes[8],
        "institutional_email": queryRes[9],
        "secondary_email": queryRes[10],
        "gender": queryRes[11],
        "phone": queryRes[12],
        "creation_datetime": str(queryRes[13]),
        "siape": queryRes[14]
      },
      "solicitation":{
        "solicitation_name": queryRes[15],
        "step_profile_editor_acronym": queryRes[16],
        "step_order_in_solicitation": queryRes[17],
        "step_description": queryRes[18],
        "step_max_duration_days": queryRes[19],
        "actual_solicitation_step_order": queryRes[20],
        "solicitation_user_data": getFormatedMySQLJSON(queryRes[21]),
        "user_has_step_id": queryRes[22],
        "decision": queryRes[23],
        "reason": queryRes[24],
        "start_datetime": str(queryRes[25]),
        "end_datetime": str(queryRes[26]),
        "page": {
          "use_dynamic_page": queryRes[27],
          "static_page_name": queryRes[28],
          "title": sistemStrParser(queryRes[29], studentParserToken),
          "top_inner_html": sistemStrParser(queryRes[30], studentParserToken),
          "mid_inner_html": sistemStrParser(queryRes[31], studentParserToken),
          "bot_inner_html": sistemStrParser(queryRes[32], studentParserToken),
          "inputs": getFormatedMySQLJSON(queryRes[33]),
          "downloads": getFormatedMySQLJSON(queryRes[34]),
          "uploads": getFormatedMySQLJSON(queryRes[35]),
          "select_uploads": getFormatedMySQLJSON(queryRes[36]),
          "is_solicitation_button_active": queryRes[37]
        }
      },
    }, 200
  
  # put to create solicitations - works only for students
  def put(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs.add_argument("solicitation_id", location="json", type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ["STU"])
    if not isTokenValid:
      abort(401, errorMsg)

    solicitationId = solicitationsArgs["solicitation_id"]
    userId = tokenData["user_id"]

    print("\n# Starting put Single Solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")
    
    stepId = None
    stepMaxDurationDays = None
    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT ss.id, ss.step_max_duration_days "
        "   FROM solicitation AS s JOIN solicitation_step AS ss ON s.id = ss.solicitation_id "
        "   WHERE s.id = %s AND step_order_in_solicitation = 1; ",
        [(solicitationId)])

      if not queryRes:
        raise Exception("No step with code 1 return for solicitation with id " + str(solicitationId))
      
      stepId = queryRes[0]
      stepMaxDurationDays = queryRes[1]

      queryRes = dbGetSingle(
        " SELECT s.id	FROM user_account AS us "
	      "   JOIN user_has_solicitation AS uhs ON us.id = uhs.user_id "
	      "   JOIN solicitation AS s ON uhs.solicitation_id = s.id "
	      "   WHERE s.id = %s AND us.id = %s; ",
        [solicitationId, userId])

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if queryRes:
      abort(401, "Você já possui essa solicitação!")
    
    # set created date and finish date based on max day interval from solicitation step
    createdDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    finishDate = None if not stepMaxDurationDays else (datetime.datetime.now() + datetime.timedelta(days=stepMaxDurationDays)).strftime("%Y-%m-%d %H:%M:%S")

    userHasSolId = None
    userHasSolStepId = None
    try:
      # insert user solicitation
      dbExecute(
        " INSERT INTO user_has_solicitation "
        " (user_id, professor_siape, solicitation_id, actual_solicitation_step_order, solicitation_user_data) VALUES "
        "   (%s, \"SIAPERENATO\", %s, 1, NULL); ",
        [userId, solicitationId], False)

      # select added user solicitation id
      queryRes = dbGetSingle(
        " SELECT uhs.id "
        "   FROM user_has_solicitation AS uhs "
        "   WHERE uhs.user_id = %s AND solicitation_id = %s; ",
        [userId, solicitationId], False)
      
      if not queryRes:
        raise Exception("No return for user_has_solicitation insertion ")

      userHasSolId = queryRes[0]

      # insert user solicitation step
      dbExecute(
        " INSERT INTO user_has_solicitation_step "
        " (user_has_solicitation_id, solicitation_step_id, decision, reason, start_datetime, end_datetime) VALUES "
        "   (%s, %s, \"Em analise\", \"Aguardando o envio de dados pelo aluno\", %s, %s); ",
        [userHasSolId, stepId, createdDate, finishDate], False)

      # select added user solicitation step id
      queryRes = dbGetSingle(
        " SELECT uhss.id "
        "   FROM user_has_solicitation_step AS uhss "
        "   WHERE uhss.user_has_solicitation_id = %s AND uhss.solicitation_step_id = %s; ",
        [userHasSolId, stepId], False)

      if not queryRes:
        raise Exception("No return for user_has_solicitation_step insertion ")
      
      userHasSolStepId = queryRes[0]
      
    except Exception as e:
      dbRollback()
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    dbCommit()
    print("# Operation done!")
    return { "user_has_solicitation_id": userHasSolId, "user_has_step_id": userHasSolStepId }, 200
      
  # post to resolve solicitations
  def post(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs.add_argument("user_has_step_id", location="json", type=int, required=True)
    solicitationsArgs.add_argument("decision", location="json", type=str, required=True)
    solicitationsArgs.add_argument("reason", location="json", type=str, required=True)
    solicitationsArgs.add_argument("solicitation_user_data", location="json", required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    userHasStepId = solicitationsArgs["user_has_step_id"]
    decision = solicitationsArgs["decision"]
    reason = solicitationsArgs["reason"]
    solicitationUserData = solicitationsArgs["solicitation_user_data"]

    if solicitationUserData:
      solicitationUserData = json.loads(
        solicitationUserData.replace("\'", "\"") if isinstance(solicitationUserData, str) else solicitationUserData.decode("utf-8"))
    
    print("\n# Starting post to resolve solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT uc_stu.id AS student_id, uc_stu.institutional_email AS student_ins_email, uc_stu.secondary_email AS student_sec_email, "
        " uc_pro.id AS professor_id, uc_pro.institutional_email AS professor_ins_email, uc_pro.secondary_email AS professor_sec_email, "
        " uhs.id, uhs.solicitation_id, uhs.actual_solicitation_step_order, uhs.solicitation_user_data, "
        " uhss.solicitation_step_id, uhss.decision, uhss.start_datetime, uhss.end_datetime, "
        " ss.step_order_in_solicitation, ssprof.profile_acronym, "
        " dp.inputs, dp.uploads, dp.select_uploads "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_step AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation_step AS ss ON uhss.solicitation_step_id = ss.id "
        "     JOIN solicitation_step_page AS ssp ON ss.id = ssp.solicitation_step_id "
        "     LEFT JOIN profile AS ssprof ON ss.step_profile_editor = ssprof.id "
        "     LEFT JOIN dynamic_page AS dp ON ssp.dynamic_page_id = dp.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "   WHERE uhss.id = %s; ",
        [(userHasStepId)])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if not queryRes:
      abort(401, "Usuario não possui a etapa de solicitação!")

    studentId = queryRes[0]
    studentInsEmail = queryRes[1]
    studentSecEmail = queryRes[2]
    professorId = queryRes[3]
    professorInsEmail = queryRes[4]
    professorSecEmail = queryRes[5]
    userHasSolId = queryRes[6]
    solicitationId = queryRes[7]
    actualStepOrder = queryRes[8]
    oldSolicitationUserData = getFormatedMySQLJSON(queryRes[9])
    stepId = queryRes[10]
    stepDecision = queryRes[11]
    stepStartDatetime = queryRes[12]
    stepEndDatetime = queryRes[13]
    stepOrder = queryRes[14]
    stepProfileAcronymEditor = queryRes[15]
    pageInputs = getFormatedMySQLJSON(queryRes[16])
    pageUploads = getFormatedMySQLJSON(queryRes[17])
    pageSelectUploads = getFormatedMySQLJSON(queryRes[18])

    # Verify solicitation args correcteness
    print("# Validating data")

    # user acess
    if not "ADM" in tokenData["profile_acronyms"] and not "COO" in tokenData["profile_acronyms"]:
      if tokenData["user_id"] != studentId and tokenData["user_id"] != professorId:
        abort(401, "Edição a solicitação não permitida!")

    if not stepProfileAcronymEditor in tokenData["profile_acronyms"]:
      abort(401, "Perfil editor a solicitação inválido!")
      
    if actualStepOrder!=stepOrder:
      abort(401, "Solicitação está fora de ordem!")

    # data validation
    if stepStartDatetime and datetime.datetime.now() < stepStartDatetime:
      abort(401, "Esta etapa da solicitação não foi iniciada!")

    if stepEndDatetime and datetime.datetime.now() > stepEndDatetime:
      abort(401, "Esta etapa da solicitação foi expirada!")
    
    if stepDecision != "Em analise":
      abort(401, "Esta solicitação já foi realizada!")
    
    # Checks if all required inputs are valid
    if pageInputs and pageInputs[0]:
      
      for pInp in pageInputs:
        if pInp["required"]:
          found = False

          for solInp in solicitationUserData["inputs"]:
            if solInp["label_txt"] == pInp["label_txt"]:
              found = True
          
          if not found:
            abort(401, "Input da solicitação está faltando!")

    # Checks if all required uploads are valid
    if pageUploads and pageUploads[0]:

      for pageUpload in pageUploads:
        if pageUpload["required"]:
          found = False

          for solUpload in solicitationUserData["uploads"]:
            if solUpload["file_content_id"] == pageUpload["file_content_id"]:

              try:
                if dbGetSingle(
                    " SELECT att.hash_name "
                    "   FROM attachment AS att JOIN user_has_attachment AS uhatt ON att.id = uhatt.attachment_id "
                    "   WHERE uhatt.user_id = %s AND att.hash_name = %s; ",
                    [tokenData["user_id"], solUpload["hash_name"]]):
                  found = True
                  break
              except Exception as e:
                print("# Database reading error:")
                print(str(e))
                return "Erro na base de dados", 409
              
          if not found:
            abort(401, "Anexo da solicitação está faltando!")
          else:
            # add to solicitation data without updating old ones upload names
            pass
            
    # Checks if all required select uploads are valid - incomplete
    if pageSelectUploads and pageSelectUploads[0]:
      pass

    # get next step if exists
    try:
      queryRes = dbGetSingle(
        " SELECT ss.id, ss.step_max_duration_days, ssprof.profile_acronym "
        "   FROM solicitation AS s "
        "     JOIN solicitation_step AS ss ON s.id = ss.solicitation_id "
        "     LEFT JOIN profile AS ssprof ON ss.step_profile_editor = ssprof.id "
        "     WHERE s.id = %s AND ss.step_order_in_solicitation = %s; ",
        [solicitationId, actualStepOrder+1])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
  
    nextStepId = None if not queryRes else queryRes[0]
    nextStepMaxDays = None if not queryRes else queryRes[1]
    nextStepProfileEditorAcronym = None if not queryRes else queryRes[2]

    print("# Updating and Inserting data in db")
    try:
      # updates actual user step
      dbExecute(
        " UPDATE user_has_solicitation_step "
        "   SET decision = %s, reason = %s "
        "   WHERE id = %s; ",
        [decision, reason, userHasStepId], False)
      
      # if next step exists
      if nextStepId:
        nextStepCreatedDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nextStepFinishDate = None if not nextStepMaxDays else (datetime.datetime.now() + datetime.timedelta(days=nextStepMaxDays)).strftime("%Y-%m-%d %H:%M:%S")

        # inserts new user step
        dbExecute(
          " INSERT INTO user_has_solicitation_step "
          " (user_has_solicitation_id, solicitation_step_id, decision, reason, start_datetime, end_datetime) VALUES "
          "   (%s, %s, \"Em analise\", %s, %s, %s); ",
          [
            solicitationId,
            nextStepId,
            "Aguardando o envio de dados pelo " + ("aluno" if nextStepProfileEditorAcronym == "STU" else ("orientador" if nextStepProfileEditorAcronym == "POO" else "coordenador")),
            nextStepCreatedDate,
            nextStepFinishDate],
          False)

        # updates user solicitation data and increase its step order
        dbExecute(
          " UPDATE user_has_solicitation "
          "   SET actual_solicitation_step_order = %s "
          "   WHERE id = %s; ",
          [actualStepOrder+1, userHasSolId], False)
        
      # if next step not exists
      else:
        # updates only user solicitation data
        pass
        
    except Exception as e:
      dbRollback()
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    dbCommit()
    print("# Solicitation done!\n# Sending mails")

    # mail message sending
    try:
      queryRes = dbGetAll(
        " SELECT dm.mail_subject, dm.mail_body_html, dm.is_sent_to_student, dm.is_sent_to_professor, dm.is_sent_to_coordinator "
        "   FROM solicitation AS s "
        "     JOIN solicitation_step AS ss ON s.id = ss.solicitation_id "
        "     JOIN solicitation_step_dynamic_mail AS ssdm ON ss.id = ssdm.solicitation_step_id "
        "     JOIN dynamic_mail AS dm ON ssdm.dynamic_mail_id = dm.id "
        "     WHERE ss.id = %s; ",
        [(stepId)])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    if queryRes:

      mailList = []
      for r in queryRes:
        mailList.append({
          "mailSubject": r[0],
          "mailBodyHtml": sistemStrParser(r[1], tokenData),
          "isSentToStudent": r[2],
          "isSentToProfessor": r[3],
          "isSentToCoordinator": r[4]
        })

      for mail in mailList:

        if mail["isSentToStudent"]:
          smtpSend(studentInsEmail, mail["mailSubject"], mail["mailBodyHtml"])
          smtpSend(studentSecEmail, mail["mailSubject"], mail["mailBodyHtml"])
          
        if mail["isSentToProfessor"]:
          smtpSend(professorInsEmail, mail["mailSubject"], mail["mailBodyHtml"])
          smtpSend(professorSecEmail, mail["mailSubject"], mail["mailBodyHtml"])

        if mail["isSentToCoordinator"]:
          smtpSend(getCoordinatorEmail(), mail["mailSubject"], mail["mailBodyHtml"])
      
      print("# Operation done!")

    return {}, 200
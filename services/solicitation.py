import datetime
import json
import traceback

from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.sistemConfig import getCoordinatorEmail
from utils.smtpMails import smtpSend
from utils.utils import getFormatedMySQLJSON, sistemStrParser

def loadPageComponents(pageId, studentParserToken=None):

  useParser = studentParserToken!=None

  pageComponentsQuery = dbGetAll(
    " SELECT dphc.dynamic_component_order AS component_order, "
    " dc.id AS component_id, dc.type AS component_type, "
    " dc_inner_html.inner_html, "
    " dc_input.input_name, dc_input.input_type, dc_input.input_required, dc_input.input_missing_message, "
    " dc_upload.upload_label, dc_upload.upload_name, dc_upload.upload_required, dc_upload.upload_missing_message, "
    " dc_select.select_name, dc_select.select_label, dc_select.select_initial_text, dc_select.is_select_required, dc_select.select_missing_message, "
    
    " dcsupload_select.dynamic_component_id AS select_upload_select_id, dcsupload_select.select_name AS select_upload_select_name, "
    " dcsupload_select.select_label AS select_upload_select_label, dcsupload_select.select_initial_text AS select_upload_select_initial_text, "
    " dcsupload_select.is_select_required AS select_upload_is_select_required, dcsupload_select.select_missing_message AS select_upload_select_missing_message, "
    
    " dc_download.download_label, dc_download.download_from, dc_download.internal_upload_name, dc_download.internal_select_upload_name, dc_download.external_download_link, "
    " dc_button.button_label, dc_button.button_color "
    "   FROM dynamic_page AS dp "
    "     JOIN dynamic_page_has_component AS dphc ON dp.id = dphc.dynamic_page_id "
    "     JOIN dynamic_component AS dc ON dphc.dynamic_component_id = dc.id "

    "     LEFT JOIN dynamic_component_inner_html AS dc_inner_html ON dc.id = dc_inner_html.dynamic_component_id "

    "     LEFT JOIN dynamic_component_input AS dc_input ON dc.id = dc_input.dynamic_component_id "

    "     LEFT JOIN dynamic_component_upload AS dc_upload ON dc.id = dc_upload.dynamic_component_id "

    "     LEFT JOIN dynamic_component_select AS dc_select ON dc.id = dc_select.dynamic_component_id "

    "     LEFT JOIN dynamic_component_select_upload AS dc_select_upload ON dc.id = dc_select_upload.dynamic_component_id "
    "     LEFT JOIN dynamic_component_select AS dcsupload_select ON dc_select_upload.dynamic_component_select_name = dcsupload_select.select_name "
    
    "     LEFT JOIN dynamic_component_download AS dc_download ON dc.id = dc_download.dynamic_component_id "

    "     LEFT JOIN dynamic_component_button AS dc_button ON dc.id = dc_button.dynamic_component_id "
    
    "   WHERE dp.id = %s "
    "   ORDER BY dphc.dynamic_component_order; ",
    [(pageId)])
  
  if not pageComponentsQuery:
    raise Exception("No return for dynamic_page in get single solicitation ")
  
  # copy from query result to avoid empty fields
  pageComponents = []
  for componentQ in pageComponentsQuery:

    component = {}
    component["component_order"] = componentQ["component_order"]
    component["component_id"] = componentQ["component_id"]
    component["component_type"] = componentQ["component_type"]

    if component["component_type"] == "inner_html":
      component["inner_html"] = sistemStrParser(componentQ["inner_html"], studentParserToken) if useParser else componentQ["inner_html"]

    if component["component_type"] == "input":
      component["input_name"] = componentQ["input_name"]
      component["input_type"] = componentQ["input_type"]
      component["input_required"] = componentQ["input_required"]
      component["input_missing_message"] = componentQ["input_missing_message"]

      if component["input_type"] == "date":

        rawInputDateRules = dbGetAll(
          " SELECT rule_type, rule_message_type, rule_start_days, rule_end_days, rule_missing_message "
          "   FROM dynamic_component_input AS dc_input "
          "     JOIN dynamic_component_input_date_rule AS dc_input_date_rules ON dc_input.dynamic_component_id = dc_input_date_rules.dynamic_component_input_id "
          "   WHERE dc_input.dynamic_component_id = %s; ",
          [(component["component_id"])])

        if rawInputDateRules:
          component["input_date_rules"] = rawInputDateRules

    if component["component_type"] == "upload":
      component["upload_label"] = componentQ["upload_label"]
      component["upload_name"] = componentQ["upload_name"]
      component["upload_required"] = componentQ["upload_required"]
      component["upload_missing_message"] = componentQ["upload_missing_message"]
    
    if component["component_type"] == "select":
      component["select_name"] = componentQ["select_name"]
      component["select_label"] = componentQ["select_label"]
      component["select_initial_text"] = componentQ["select_initial_text"]
      component["is_select_required"] = componentQ["is_select_required"]
      component["select_missing_message"] = componentQ["select_missing_message"]

      rawSelectOpts = dbGetAll(
        " SELECT select_option_label AS option_label, select_option_value AS option_value "
        "   FROM dynamic_component_select AS dc_select "
        "     JOIN dynamic_component_select_option AS dc_select_option ON dc_select.dynamic_component_id = dc_select_option.dynamic_component_select_id "
        "   WHERE dc_select.dynamic_component_id = %s; ",
        [(component["component_id"])])

      component["select_options"] = rawSelectOpts

    if component["component_type"] == "select_upload":
      component["select_id"] = componentQ["select_upload_select_id"]
      component["select_upload_name"] = componentQ["select_upload_select_name"]
      component["select_upload_label"] = componentQ["select_upload_select_label"]
      component["select_upload_initial_text"] = componentQ["select_upload_select_initial_text"]
      component["select_upload_required"] = componentQ["select_upload_is_select_required"]
      component["select_upload_missing_message"] = componentQ["select_upload_select_missing_message"]

      rawSelectUploadOptions = dbGetAll(
        " SELECT select_option_label AS label, select_option_value AS value "
        "   FROM dynamic_component_select AS dc_select "
        "     JOIN dynamic_component_select_option AS dc_select_option ON dc_select.dynamic_component_id = dc_select_option.dynamic_component_select_id "
        "   WHERE dc_select.dynamic_component_id = %s; ",
        [(component["select_id"])])

      component['select_upload_options'] = rawSelectUploadOptions

    if component["component_type"] == "download":
      component["download_label"] = componentQ["download_label"]
      component["download_from"] = componentQ["download_from"]
      component["internal_upload_name"] = componentQ["internal_upload_name"]
      component["internal_select_upload_name"] = componentQ["internal_select_upload_name"]
      component["external_download_link"] = componentQ["external_download_link"]
      
    if component["component_type"] == "button":
      component["button_label"] = componentQ["button_label"]
      component["button_color"] = componentQ["button_color"]

      rawButtonTransiction = dbGetSingle(
        " SELECT sst.id, solicitation_state_id_from, solicitation_state_id_to "
        "   FROM dynamic_page AS dp "
        "     JOIN dynamic_page_has_component AS dphc ON dp.id = dphc.dynamic_page_id "
      
        "     JOIN solicitation_state_transition AS sst ON dphc.id = sst.dynamic_page_has_component_id "
        "       AND dphc.dynamic_component_id = sst.dynamic_page_has_component_button_id "
        
        "     WHERE dp.id = %s AND sst.dynamic_page_has_component_button_id = %s; ",
        [pageId, component["component_id"]])
        
      component["transition_id"] = rawButtonTransiction["id"]
    
    # index by component order
    pageComponents.append(component)
  
  return pageComponents

# Data from single solicitation
class Solicitation(Resource):

  # get single solicitation and associated dynamic page data
  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs.add_argument("user_has_state_id", location="args", type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    userHasStateId = solicitationsArgs["user_has_state_id"]

    print("\n# Starting get single solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT uhs.user_id, uc_adv.id AS advisor_id "
        "   FROM user_has_solicitation_state AS uhss "
        "     JOIN user_has_solicitation AS uhs ON uhss.user_has_solicitation_id = uhs.id "
        "     LEFT JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
        "     LEFT JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
        "     LEFT JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
        "   WHERE uhss.id = %s; ",
        [(userHasStateId)])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if not queryRes:
      abort(401, "Usuario não possui o estado da solicitação!")

    studentId = queryRes["user_id"]
    advisorId = queryRes["advisor_id"]

    if not "ADM" in tokenData["profile_acronyms"] and not "COO" in tokenData["profile_acronyms"]:
      if tokenData["user_id"] != studentId and tokenData["user_id"] != advisorId:
        abort(401, "Acesso a solicitação não permitido!")

    solicitationQuery = None
    try:
      solicitationQuery = dbGetSingle(
        " SELECT uc_stu.user_name AS student_name, uc_stu.institutional_email AS student_institutional_email, "
        " uc_stu.secondary_email AS student_secondary_email, uc_stu.gender AS student_gender, "
        " uc_stu.phone AS student_phone, uc_stu.creation_datetime AS student_creation_datetime, "
        " uhpsd.matricula AS student_matricula, uhpsd.course AS student_course, "

        " uc_adv.user_name AS advisor_name, uc_adv.institutional_email AS advisor_institutional_email, "
        " uc_adv.secondary_email AS advisor_secondary_email, uc_adv.gender AS advisor_gender, "
        " uc_adv.phone AS advisor_phone, uc_adv.creation_datetime AS advisor_creation_datetime, uhpad.siape AS advisor_siape, "

        " s.solicitation_name, "
        " ssprof.profile_acronym AS state_profile_editor_acronym, ss.id, ss.state_description, ss.state_max_duration_days, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, "
        " uhss.id AS user_has_state_id, uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " dp.id AS page_id, dp.title AS page_title "
        
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "

        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_state AS ss ON uhss.solicitation_state_id = ss.id "
        "     JOIN dynamic_page AS dp ON ss.state_dynamic_page_id = dp.id "

        "     LEFT JOIN profile AS ssprof ON ss.state_profile_editor = ssprof.id "
        "     LEFT JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
        "     LEFT JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
        "     LEFT JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
        "   WHERE uc_stu.id = %s AND uhss.id = %s; ",
        [studentId, userHasStateId])
      
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if not solicitationQuery:
      abort(401, "Usuario não possui o estado da solicitação!")

    # Refactor this in future
    studentParserToken={
      "user_name": solicitationQuery["student_name"],
      "gender": solicitationQuery["student_gender"],
      "profiles": [{
        "profile_acronym":"STU",
        "matricula": solicitationQuery["student_matricula"],
        "course": solicitationQuery["student_course"]
      }]
    }
    
    pageId = solicitationQuery["page_id"]
    pageComponents = loadPageComponents(pageId, studentParserToken)

    print("# Operation Done!")
    
    return {
      "student": {
        "user_name": solicitationQuery["student_name"],
        "institutional_email": solicitationQuery["student_institutional_email"],
        "secondary_email": solicitationQuery["student_secondary_email"],
        "gender": solicitationQuery["student_gender"],
        "phone": solicitationQuery["student_phone"],
        "creation_datetime": str(solicitationQuery["student_creation_datetime"]),
        "matricula": solicitationQuery["student_matricula"],
        "course": solicitationQuery["student_course"]
      },
      "advisor": {
        "user_name": solicitationQuery["advisor_name"],
        "institutional_email": solicitationQuery["advisor_institutional_email"],
        "secondary_email": solicitationQuery["advisor_secondary_email"],
        "gender": solicitationQuery["advisor_gender"],
        "phone": solicitationQuery["advisor_phone"],
        "creation_datetime": str(solicitationQuery["advisor_creation_datetime"]),
        "siape": solicitationQuery["advisor_siape"]
      },
      "solicitation":{
        "solicitation_name": solicitationQuery["solicitation_name"],
        "state_profile_editor_acronym": solicitationQuery["state_profile_editor_acronym"],
        "state_description": solicitationQuery["state_description"],
        "state_max_duration_days": solicitationQuery["state_max_duration_days"],
        "actual_solicitation_state_id": solicitationQuery["actual_solicitation_state_id"],
        "solicitation_user_data": getFormatedMySQLJSON(solicitationQuery["solicitation_user_data"]),
        "user_has_state_id": solicitationQuery["user_has_state_id"],
        "decision": solicitationQuery["decision"],
        "reason": solicitationQuery["reason"],
        "start_datetime": str(solicitationQuery["start_datetime"]),
        "end_datetime": str(solicitationQuery["end_datetime"]),
        "page": {
          "title": sistemStrParser(solicitationQuery["page_title"], studentParserToken),
          "components" : pageComponents
        }
      },
    }, 200
  
  # put to create solicitations - only for students
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
    
    stateId = None
    stateMaxDurationDays = None
    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT ss.id AS state_id, ss.state_max_duration_days "
        "   FROM solicitation AS s JOIN solicitation_state AS ss ON s.id = ss.solicitation_id "
        "   WHERE s.id = %s AND ss.is_initial_state = TRUE; ",
        [(solicitationId)])

      if not queryRes:
        raise Exception("No initial state return for solicitation with id " + str(solicitationId))
      
      stateId = queryRes["state_id"]
      stateMaxDurationDays = queryRes["state_max_duration_days"]

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
    
    # set created date and finish date based on max day interval from solicitation state
    createdDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    finishDate = None if not stateMaxDurationDays else (datetime.datetime.now() + datetime.timedelta(days=stateMaxDurationDays)).strftime("%Y-%m-%d %H:%M:%S")
    
    userHasSolId = None
    userHasSolStateId = None

    # start transaction
    dbObjectIns = dbStartTransactionObj()
    try:
      # insert user solicitation
      dbExecute(
        " INSERT INTO user_has_solicitation "
        " (user_id, advisor_siape, solicitation_id, actual_solicitation_state_id, solicitation_user_data) VALUES "
        "   (%s, \"SIAPERENATO\", %s, %s, NULL); ",
        [userId, solicitationId, stateId], True, dbObjectIns)

      # select added user solicitation id
      queryRes = dbGetSingle(
        " SELECT uhs.id "
        "   FROM user_has_solicitation AS uhs "
        "   WHERE uhs.user_id = %s AND solicitation_id = %s; ",
        [userId, solicitationId], True, dbObjectIns)
      
      if not queryRes:
        raise Exception("No return for user_has_solicitation insertion ")

      userHasSolId = queryRes["id"]

      # insert user solicitation state
      dbExecute(
        " INSERT INTO user_has_solicitation_state "
        " (user_has_solicitation_id, solicitation_state_id, decision, reason, start_datetime, end_datetime) VALUES "
        "   (%s, %s, \"Em analise\", \"Aguardando o envio de dados pelo aluno\", %s, %s); ",
        [userHasSolId, stateId, createdDate, finishDate], True, dbObjectIns)

      # select added user solicitation state id
      queryRes = dbGetSingle(
        " SELECT uhss.id "
        "   FROM user_has_solicitation_state AS uhss "
        "   WHERE uhss.user_has_solicitation_id = %s AND uhss.solicitation_state_id = %s; ",
        [userHasSolId, stateId], True, dbObjectIns)

      if not queryRes:
        raise Exception("No return for user_has_solicitation_state insertion ")
      
      userHasSolStateId = queryRes["id"]
      
    except Exception as e:
      dbRollback(dbObjectIns)
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    # ends transaction
    dbCommit(dbObjectIns)
    print("# Operation done!")
    return { "user_has_solicitation_id": userHasSolId, "user_has_state_id": userHasSolStateId }, 200
      
  # post to resolve solicitations
  def post(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs.add_argument("user_has_state_id", location="json", type=int, required=True)
    solicitationsArgs.add_argument("transition_id", location="json", type=str, required=True)
    solicitationsArgs.add_argument("solicitation_user_data", location="json", required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    userHasStateId = solicitationsArgs["user_has_state_id"]
    transitionId = solicitationsArgs["transition_id"]
    solicitationUserData = solicitationsArgs["solicitation_user_data"]

    if solicitationUserData:
      solicitationUserData = json.loads(
        solicitationUserData.replace("\'", "\"") if isinstance(solicitationUserData, str) else solicitationUserData.decode("utf-8"))
    
    print("\n# Starting post to resolve solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT uc_stu.id AS student_id, uc_stu.institutional_email AS student_ins_email, uc_stu.secondary_email AS student_sec_email, "
        " uc_adv.id AS advisor_id, uc_adv.institutional_email AS advisor_ins_email, uc_adv.secondary_email AS advisor_sec_email, "
        " uhs.id AS user_has_solicitation_id, uhs.solicitation_id, uhs.actual_solicitation_state_id, uhs.solicitation_user_data, "
        " uhss.solicitation_state_id, uhss.decision, uhss.start_datetime, uhss.end_datetime, "
        " ssprof.profile_acronym, "
        " dp.id AS page_id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation_state AS ss ON uhss.solicitation_state_id = ss.id "
        "     JOIN dynamic_page AS dp ON ss.state_dynamic_page_id = dp.id "
        "     LEFT JOIN profile AS ssprof ON ss.state_profile_editor = ssprof.id "
        "     LEFT JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
        "     LEFT JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
        "     LEFT JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
        "   WHERE uhss.id = %s; ",
        [(userHasStateId)])
      
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if not queryRes:
      abort(401, "Usuario não possui o estado da solicitação!")

    studentId = queryRes["student_id"]
    studentInsEmail = queryRes["student_ins_email"]
    studentSecEmail = queryRes["student_sec_email"]
    advisorId = queryRes["advisor_id"]
    advisorInsEmail = queryRes["advisor_ins_email"]
    advisorSecEmail = queryRes["advisor_sec_email"]
    userHasSolId = queryRes["user_has_solicitation_id"]
    solicitationId = queryRes["solicitation_id"]
    actualSolStateId = queryRes["actual_solicitation_state_id"]
    oldSolicitationUserData = getFormatedMySQLJSON(queryRes["solicitation_user_data"])
    stateId = queryRes["solicitation_state_id"]
    stateDecision = queryRes["decision"]
    stateStartDatetime = queryRes["start_datetime"]
    stateEndDatetime = queryRes["end_datetime"]
    stateProfileAcronymEditor = queryRes["profile_acronym"]
    pageId = queryRes["page_id"]

    pageComponents = None
    try:
      pageComponents = loadPageComponents(pageId, None)
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    # Verify solicitation args correcteness
    print("# Validating data")

    # user acess
    if not "ADM" in tokenData["profile_acronyms"] and not "COO" in tokenData["profile_acronyms"]:
      if tokenData["user_id"] != studentId and tokenData["user_id"] != advisorId:
        abort(401, "Edição a solicitação não permitida!")

    if not stateProfileAcronymEditor in tokenData["profile_acronyms"]:
      abort(401, "Perfil editor a solicitação inválido!")
      
    if actualSolStateId!=stateId:
      abort(401, "Edição do estado da solicitação não permitido!")

    # data validation
    if stateStartDatetime and datetime.datetime.now() < stateStartDatetime:
      abort(401, "Esta etapa da solicitação não foi iniciada!")

    if stateEndDatetime and datetime.datetime.now() > stateEndDatetime:
      abort(401, "Esta etapa da solicitação foi expirada!")
    
    if stateDecision != "Em analise":
      abort(401, "Esta solicitação já foi realizada!")
  
    for component in pageComponents:

      # Checks if all required inputs are valid
      if component["component_type"] == "input" and component["input_required"]:
        found = False
        
        for userInput in solicitationUserData['inputs']:
          if userInput["input_name"] == component["input_name"]:
            found = True
          
        if not found:
          abort(401, "Input da solicitação está faltando!")

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
                  [tokenData["user_id"], userUpload["upload_hash_name"]]):
                found = True
                break
            except Exception as e:
              print("# Database reading error:")
              print(str(e))
              return "Erro na base de dados", 409
                
        if not found:
          abort(401, "Anexo da solicitação está faltando!")
              
      # Checks if all required select uploads are valid - incomplete
      if component["component_type"] == "select_upload" and component["select_upload_required"]:
        pass

    # get transiction data
    try:
      queryRes = dbGetSingle(
        " SELECT sst.transition_decision, sst.transition_reason, "
        "   ss.id AS state_id, ss.state_max_duration_days, ssprof.profile_acronym "
        "   FROM solicitation_state_transition AS sst "
        "     LEFT JOIN solicitation_state AS ss ON sst.solicitation_state_id_to = ss.id "
        "     LEFT JOIN profile AS ssprof ON ss.state_profile_editor = ssprof.id "
        "     WHERE sst.id = %s; ",
        [transitionId])
      
      if not queryRes:
        raise Exception("No return for solicitation_state_transition ")

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    transitionDecision = queryRes["transition_decision"]
    transitionReason = queryRes["transition_reason"]
    nextStateId = queryRes["state_id"]
    nextStateMaxDays = queryRes["state_max_duration_days"]
    nextStateProfileEditorAcronym = queryRes["profile_acronym"]

    # parse solicitation data
    newSolicitationUserData = None
    if oldSolicitationUserData:
      newSolicitationUserData = oldSolicitationUserData
    else:
      newSolicitationUserData = {
        "inputs": {},
        "uploads": {},
        "select_uploads": {}
      }

    if solicitationUserData:
      for input in solicitationUserData["inputs"]:
        newSolicitationUserData["inputs"][input["input_name"]] = input
      for upload in solicitationUserData["uploads"]:
        newSolicitationUserData["uploads"][upload["upload_name"]] = upload
      for selectUpload in solicitationUserData["select_uploads"]:
        newSolicitationUserData["select_uploads"][selectUpload["select_upload_name"]] = selectUpload
    
    newSolicitationUserData = json.dumps(newSolicitationUserData)
    
    # start transaction
    dbObjectIns = dbStartTransactionObj()
    print("# Updating and Inserting data in db")
    try:
      # updates actual user state
      dbExecute(
        " UPDATE user_has_solicitation_state "
        "   SET decision = %s, reason = %s "
        "   WHERE id = %s; ",
        [transitionDecision, transitionReason, userHasStateId], True, dbObjectIns)
      
      # if next state exists
      if nextStateId:
        nextStateCreatedDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nextStateFinishDate = None if not nextStateMaxDays else (datetime.datetime.now() + datetime.timedelta(days=nextStateMaxDays)).strftime("%Y-%m-%d %H:%M:%S")

        sendProfileName = None
        if nextStateProfileEditorAcronym == "STU":
          sendProfileName = "aluno"
        elif nextStateProfileEditorAcronym == "ADV":
          sendProfileName = "orientador"
        elif nextStateProfileEditorAcronym == "COO":
          sendProfileName = "coordenador"

        # inserts new user state
        dbExecute(
          " INSERT INTO user_has_solicitation_state "
          " (user_has_solicitation_id, solicitation_state_id, decision, reason, start_datetime, end_datetime) VALUES "
          "   (%s, %s, DEFAULT, %s, %s, %s); ",
          [
            userHasSolId,
            nextStateId,
            "Aguardando o envio de dados pelo " + sendProfileName if sendProfileName else None,
            nextStateCreatedDate,
            nextStateFinishDate],
          True, dbObjectIns)
        
        # updates user solicitation data and changes its actual state
        dbExecute(
          " UPDATE user_has_solicitation "
          "   SET actual_solicitation_state_id = %s, solicitation_user_data = %s "
          "   WHERE id = %s; ",
          [nextStateId, newSolicitationUserData, userHasSolId], True, dbObjectIns)

      # if next state not exists
      else:
        # updates only user solicitation data
        dbExecute(
          " UPDATE user_has_solicitation "
          "   SET solicitation_user_data = %s "
          "   WHERE id = %s; ",
          [newSolicitationUserData, userHasSolId], True, dbObjectIns)
        
    except Exception as e:
      dbRollback(dbObjectIns)
      print("# Database reading error:")
      traceback.print_exc()
      print(str(e))
      return "Erro na base de dados", 409

    dbCommit(dbObjectIns)
    print("# Solicitation done!\n# Sending mails")

    # mail message sending
    try:
      queryRes = dbGetAll(
        " SELECT dm.mail_subject, dm.mail_body_html, dm.is_sent_to_student, dm.is_sent_to_advisor, dm.is_sent_to_coordinator "
        "   FROM solicitation AS s "
        "     JOIN solicitation_state AS ss ON s.id = ss.solicitation_id "
        "     JOIN solicitation_state_dynamic_mail AS ssdm ON ss.id = ssdm.solicitation_state_id "
        "     JOIN dynamic_mail AS dm ON ssdm.dynamic_mail_id = dm.id "
        "     WHERE ss.id = %s; ",
        [(stateId)])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    if queryRes:

      mailList = []
      for r in queryRes:
        mailList.append({
          "mailSubject": r["mail_subject"],
          "mailBodyHtml": sistemStrParser(r["mail_body_html"], tokenData),
          "isSentToStudent": r["is_sent_to_student"],
          "isSentToAdvisor": r["is_sent_to_advisor"],
          "isSentToCoordinator": r["is_sent_to_coordinator"]
        })

      for mail in mailList:

        if mail["isSentToStudent"]:
          smtpSend(studentInsEmail, mail["mailSubject"], mail["mailBodyHtml"])
          smtpSend(studentSecEmail, mail["mailSubject"], mail["mailBodyHtml"])
          
        if mail["isSentToAdvisor"]:
          smtpSend(advisorInsEmail, mail["mailSubject"], mail["mailBodyHtml"])
          smtpSend(advisorSecEmail, mail["mailSubject"], mail["mailBodyHtml"])

        if mail["isSentToCoordinator"]:
          smtpSend(getCoordinatorEmail(), mail["mailSubject"], mail["mailBodyHtml"])
      
      print("# Operation done!")

    return {}, 200
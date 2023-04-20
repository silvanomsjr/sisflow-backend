from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json
import datetime
import traceback

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.smtpMails import smtpSend
from utils.sistemConfig import getCoordinatorEmail
from utils.utils import getFormatedMySQLJSON, sistemStrParser

def loadPageComponents(pageId, studentParserToken=None):

  useParser = studentParserToken!=None

  pageComponentsQuery = dbGetAll(
    " SELECT dphc.dynamic_component_order, "
    " dc.id, dc.type, "
    " dc_inner_html.inner_html, "
    " dc_input.input_name, dc_input.input_type, dc_input.input_required, dc_input.input_missing_message, "
    " dc_upload.upload_label, dc_upload.upload_name, dc_upload.upload_required, dc_upload.upload_missing_message, "
    " dc_select.select_name, dc_select.select_label, dc_select.select_initial_text, dc_select.is_select_required, dc_select.select_missing_message, "
    
    " dcsupload_select.dynamic_component_id, dcsupload_select.select_name, dcsupload_select.select_label, dcsupload_select.select_initial_text, "
    " dcsupload_select.is_select_required, dcsupload_select.select_missing_message, "
    
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
  
  pageComponents = []
  for componentQ in pageComponentsQuery:

    component = {}
    component['component_order'] = componentQ[0]
    component['component_id'] = componentQ[1]
    component['component_type'] = componentQ[2]

    if component['component_type'] == 'inner_html':
      component['inner_html'] = sistemStrParser(componentQ[3], studentParserToken) if useParser else componentQ[3]

    if component['component_type'] == 'input':
      component['input_name'] = componentQ[4]
      component['input_type'] = componentQ[5]
      component['input_required'] = componentQ[6]
      component['input_missing_message'] = componentQ[7]

      if component['input_type'] == 'date':

        rawInputDateRules = dbGetAll(
          " SELECT rule_type, rule_message_type, rule_start_days, rule_end_days, rule_missing_message "
          "   FROM dynamic_component_input AS dc_input "
          "     JOIN dynamic_component_input_date_rule AS dc_input_date_rules ON dc_input.dynamic_component_id = dc_input_date_rules.dynamic_component_input_id "
          "   WHERE dc_input.dynamic_component_id = %s; ",
          [(component['component_id'])])

        if rawInputDateRules:
          component['input_date_rules'] = []

          for inputRule in rawInputDateRules:
            component['input_date_rules'].append({
              "rule_type": inputRule[0],
              "rule_message_type": inputRule[1],
              "rule_start_days": inputRule[2],
              "rule_end_days": inputRule[3],
              "rule_missing_message": inputRule[4]
            })
      
    if component['component_type'] == 'upload':
      component['upload_label'] = componentQ[8]
      component['upload_name'] = componentQ[9]
      component['upload_required'] = componentQ[10]
      component['upload_missing_message'] = componentQ[11]
      
    if component['component_type'] == 'select':
      component['select_name'] = componentQ[12]
      component['select_label'] = componentQ[13]
      component['select_initial_text'] = componentQ[14]
      component['is_select_required'] = componentQ[15]
      component['select_missing_message'] = componentQ[16]

      rawSelectOpts = dbGetAll(
        " SELECT select_option_label, select_option_value "
        "   FROM dynamic_component_select AS dc_select "
        "     JOIN dynamic_component_select_option AS dc_select_option ON dc_select.dynamic_component_id = dc_select_option.dynamic_component_select_id "
        "   WHERE dc_select.dynamic_component_id = %s; ",
        [(component['component_id'])])

      component['select_options'] = []

      for option in rawSelectOpts:
        component['select_options'].append({
          "option_label": option[0],
          "option_value": option[1]
        })
      
    if component['component_type'] == 'select_upload':
      component['select_id'] = componentQ[17]
      component['select_upload_name'] = componentQ[18]
      component['select_upload_label'] = componentQ[19]
      component['select_upload_initial_text'] = componentQ[20]
      component['select_upload_required'] = componentQ[21]
      component['select_upload_missing_message'] = componentQ[22]

      rawSelectUploadOptions = dbGetAll(
        " SELECT select_option_label, select_option_value "
        "   FROM dynamic_component_select AS dc_select "
        "     JOIN dynamic_component_select_option AS dc_select_option ON dc_select.dynamic_component_id = dc_select_option.dynamic_component_select_id "
        "   WHERE dc_select.dynamic_component_id = %s; ",
        [(component['select_id'])])

      component['select_upload_options'] = []

      for option in rawSelectUploadOptions:
        component['select_upload_options'].append({
          "label": option[0],
          "value": option[1]
        })

    if component['component_type'] == 'download':
      component['download_label'] = componentQ[23]
      component['download_from'] = componentQ[24]
      component['internal_upload_name'] = componentQ[25]
      component['internal_select_upload_name'] = componentQ[26]
      component['external_download_link'] = componentQ[27]
      
    if component['component_type'] == 'button':
      component['button_label'] = componentQ[28]
      component['button_color'] = componentQ[29]

      rawButtonTransiction = dbGetSingle(
        " SELECT sst.id, solicitation_state_id_from, solicitation_state_id_to "
        "   FROM dynamic_page AS dp "
        "     JOIN dynamic_page_has_component AS dphc ON dp.id = dphc.dynamic_page_id "
      
        "     JOIN solicitation_state_transition AS sst ON dphc.id = sst.dynamic_page_has_component_id "
        "       AND dphc.dynamic_component_id = sst.dynamic_page_has_component_button_id "
        
        "     WHERE dp.id = %s AND sst.dynamic_page_has_component_button_id = %s; ",
        [pageId, component['component_id']])
        
      component['transition_id'] = rawButtonTransiction[0]
    
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

    studentId = queryRes[0]
    advisorId = queryRes[1]

    if not "ADM" in tokenData["profile_acronyms"] and not "COO" in tokenData["profile_acronyms"]:
      if tokenData["user_id"] != studentId and tokenData["user_id"] != advisorId:
        abort(401, "Acesso a solicitação não permitido!")

    solicitationQuery = None
    try:
      solicitationQuery = dbGetSingle(
        " SELECT uc_stu.user_name, uc_stu.institutional_email, uc_stu.secondary_email, uc_stu.gender, "
        " uc_stu.phone, uc_stu.creation_datetime, uhpsd.matricula, uhpsd.course, "

        " uc_adv.user_name, uc_adv.institutional_email, uc_adv.secondary_email, uc_adv.gender, "
        " uc_adv.phone, uc_adv.creation_datetime, uhpad.siape, "

        " s.solicitation_name, "
        " ssprof.profile_acronym, ss.id, ss.state_description, ss.state_max_duration_days, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, "
        " uhss.id, uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " dp.id, dp.title "
        
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
      "user_name": solicitationQuery[0],
      "gender": solicitationQuery[3],
      "profiles": [{
        "profile_acronym":"STU",
        "matricula": solicitationQuery[6],
        "course": solicitationQuery[7]
      }]
    }
    
    pageId = solicitationQuery[27]
    pageComponents = loadPageComponents(pageId, studentParserToken)

    print("# Operation Done!")

    return {
      "student": {
        "user_name": solicitationQuery[0],
        "institutional_email": solicitationQuery[1],
        "secondary_email": solicitationQuery[2],
        "gender": solicitationQuery[3],
        "phone": solicitationQuery[4],
        "creation_datetime": str(solicitationQuery[5]),
        "matricula": solicitationQuery[6],
        "course": solicitationQuery[7]
      },
      "advisor": {
        "user_name": solicitationQuery[8],
        "institutional_email": solicitationQuery[9],
        "secondary_email": solicitationQuery[10],
        "gender": solicitationQuery[11],
        "phone": solicitationQuery[12],
        "creation_datetime": str(solicitationQuery[13]),
        "siape": solicitationQuery[14]
      },
      "solicitation":{
        "solicitation_name": solicitationQuery[15],
        "state_profile_editor_acronym": solicitationQuery[16],
        "state_description": solicitationQuery[18],
        "state_max_duration_days": solicitationQuery[19],
        "actual_solicitation_state_id": solicitationQuery[20],
        "solicitation_user_data": getFormatedMySQLJSON(solicitationQuery[21]),
        "user_has_state_id": solicitationQuery[22],
        "decision": solicitationQuery[23],
        "reason": solicitationQuery[24],
        "start_datetime": str(solicitationQuery[25]),
        "end_datetime": str(solicitationQuery[26]),
        "page": {
          "title": sistemStrParser(solicitationQuery[28], studentParserToken),
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
        " SELECT ss.id, ss.state_max_duration_days "
        "   FROM solicitation AS s JOIN solicitation_state AS ss ON s.id = ss.solicitation_id "
        "   WHERE s.id = %s AND ss.is_initial_state = TRUE; ",
        [(solicitationId)])

      if not queryRes:
        raise Exception("No initial state return for solicitation with id " + str(solicitationId))
      
      stateId = queryRes[0]
      stateMaxDurationDays = queryRes[1]

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
    try:
      # insert user solicitation
      dbExecute(
        " INSERT INTO user_has_solicitation "
        " (user_id, advisor_siape, solicitation_id, actual_solicitation_state_id, solicitation_user_data) VALUES "
        "   (%s, \"SIAPERENATO\", %s, %s, NULL); ",
        [userId, solicitationId, stateId], False)

      # select added user solicitation id
      queryRes = dbGetSingle(
        " SELECT uhs.id "
        "   FROM user_has_solicitation AS uhs "
        "   WHERE uhs.user_id = %s AND solicitation_id = %s; ",
        [userId, solicitationId], False)
      
      if not queryRes:
        raise Exception("No return for user_has_solicitation insertion ")

      userHasSolId = queryRes[0]

      # insert user solicitation state
      dbExecute(
        " INSERT INTO user_has_solicitation_state "
        " (user_has_solicitation_id, solicitation_state_id, decision, reason, start_datetime, end_datetime) VALUES "
        "   (%s, %s, \"Em analise\", \"Aguardando o envio de dados pelo aluno\", %s, %s); ",
        [userHasSolId, stateId, createdDate, finishDate], False)

      # select added user solicitation state id
      queryRes = dbGetSingle(
        " SELECT uhss.id "
        "   FROM user_has_solicitation_state AS uhss "
        "   WHERE uhss.user_has_solicitation_id = %s AND uhss.solicitation_state_id = %s; ",
        [userHasSolId, stateId], False)

      if not queryRes:
        raise Exception("No return for user_has_solicitation_state insertion ")
      
      userHasSolStateId = queryRes[0]
      
    except Exception as e:
      dbRollback()
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    dbCommit()
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
        " uhs.id, uhs.solicitation_id, uhs.actual_solicitation_state_id, uhs.solicitation_user_data, "
        " uhss.solicitation_state_id, uhss.decision, uhss.start_datetime, uhss.end_datetime, "
        " ssprof.profile_acronym, "
        " dp.id "
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

    studentId = queryRes[0]
    studentInsEmail = queryRes[1]
    studentSecEmail = queryRes[2]
    advisorId = queryRes[3]
    advisorInsEmail = queryRes[4]
    advisorSecEmail = queryRes[5]
    userHasSolId = queryRes[6]
    solicitationId = queryRes[7]
    actualSolStateId = queryRes[8]
    oldSolicitationUserData = getFormatedMySQLJSON(queryRes[9])
    stateId = queryRes[10]
    stateDecision = queryRes[11]
    stateStartDatetime = queryRes[12]
    stateEndDatetime = queryRes[13]
    stateProfileAcronymEditor = queryRes[14]
    pageId = queryRes[15]

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
      if component['component_type'] == 'input' and component['input_required']:
        found = False
        
        for userInput in solicitationUserData['inputs']:
          if userInput["input_name"] == component["input_name"]:
            found = True
          
        if not found:
          abort(401, "Input da solicitação está faltando!")

      # Checks if all required uploads are valid
      if component['component_type'] == 'upload' and component['upload_required']:
        found = False

        for userUpload in solicitationUserData['uploads']:

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
        else:
          # add to solicitation data without updating old ones upload names
          pass
              
      # Checks if all required select uploads are valid - incomplete
      if component['component_type'] == 'select_upload' and component['select_upload_required']:
        pass

    # get transiction data
    try:
      queryRes = dbGetSingle(
        " SELECT sst.transition_decision, sst.transition_reason, "
        "   ss.id, ss.state_max_duration_days, ssprof.profile_acronym "
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
    
    transitionDecision = queryRes[0]
    transitionReason = queryRes[1]
    nextStateId = queryRes[2]
    nextStateMaxDays = queryRes[3]
    nextStateProfileEditorAcronym = queryRes[4]

    # parse solicitation data
    newSolicitationUserData = None
    if oldSolicitationUserData:
      newSolicitationUserData = oldSolicitationUserData
    else:
      newSolicitationUserData = {
        'inputs': {},
        'uploads': {},
        'select_uploads': {}
      }

    if solicitationUserData:
      for input in solicitationUserData['inputs']:
        newSolicitationUserData['inputs'][input['input_name']] = input
      for upload in solicitationUserData['uploads']:
        newSolicitationUserData['uploads'][upload['upload_name']] = upload
      for selectUpload in solicitationUserData['select_uploads']:
        newSolicitationUserData['select_uploads'][selectUpload['select_upload_name']] = selectUpload
    
    newSolicitationUserData = json.dumps(newSolicitationUserData)
    
    print("# Updating and Inserting data in db")
    try:
      # updates actual user state
      dbExecute(
        " UPDATE user_has_solicitation_state "
        "   SET decision = %s, reason = %s "
        "   WHERE id = %s; ",
        [transitionDecision, transitionReason, userHasStateId], False)
      
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
          False)
        
        # updates user solicitation data and changes its actual state
        dbExecute(
          " UPDATE user_has_solicitation "
          "   SET actual_solicitation_state_id = %s, solicitation_user_data = %s "
          "   WHERE id = %s; ",
          [nextStateId, newSolicitationUserData, userHasSolId], False)

      # if next state not exists
      else:
        # updates only user solicitation data
        dbExecute(
          " UPDATE user_has_solicitation "
          "   SET solicitation_user_data = %s "
          "   WHERE id = %s; ",
          [newSolicitationUserData, userHasSolId], False)
        
    except Exception as e:
      dbRollback()
      print("# Database reading error:")
      traceback.print_exc()
      print(str(e))
      return "Erro na base de dados", 409

    dbCommit()
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
          "mailSubject": r[0],
          "mailBodyHtml": sistemStrParser(r[1], tokenData),
          "isSentToStudent": r[2],
          "isSentToAdvisor": r[3],
          "isSentToCoordinator": r[4]
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
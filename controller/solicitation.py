from datetime import datetime, timedelta
from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json
import traceback

from service.dynamicPageService import getDynamicPage
from service.scheduleService import scheduleTransitions
from service.sendMailService import sendSolicitationMails
from service.solicitationService import getDPageComponentsInvalidMsg, createProfileDataBySolStateData, getUserSolStateChangeInvalidMsg, \
  getSolStateChangeInvalidMsg, getSolStateDataByUserStateId, getTransitionSolStateData, getParsedSolicitationUserData, resolveSolStateChange
from service.transitionService import getTransitions

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.utils import getFormatedMySQLJSON

# Data from single solicitation
class Solicitation(Resource):

  # get single solicitation and associated dynamic page data
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("user_has_state_id", location="args", type=int, required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    userHasStateId = args["user_has_state_id"]

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
      print(e)
      traceback.print_exc()
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
        " uc_adv.secondary_email AS advisor_secondary_email, uc_adv.gender AS advisor_gender, uc_adv.phone AS advisor_phone, "
        " uc_adv.creation_datetime AS advisor_creation_datetime, uhpad.siape AS advisor_siape, 3 AS advisor_students, "

        " s.solicitation_name, "
        " ss.id AS state_id, ss.state_description, ss.state_max_duration_days, "
        " uhs.id AS user_has_solicitation_id, uhs.is_accepted_by_advisor, uhs.actual_solicitation_state_id, uhs.solicitation_user_data, "
        " uhss.id AS user_has_state_id, uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " ss.state_dynamic_page_id AS page_id, "
        " sspe.profile_acronyms "
        
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "

        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_state AS ss ON uhss.solicitation_state_id = ss.id "

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
        
        "   WHERE uc_stu.id = %s AND uhss.id = %s; ",
        [studentId, userHasStateId])
      
    except Exception as e:
      print("# Database reading error:")
      print(e)
      traceback.print_exc()
      return "Erro na base de dados", 409

    if not solicitationQuery:
      abort(401, "Usuario não possui o estado da solicitação!")

    # Tokens for parsing string
    studentParserToken={
      "user_name": solicitationQuery["student_name"],
      "gender": solicitationQuery["student_gender"],
      "profiles": [{
        "profile_acronym":"STU",
        "matricula": solicitationQuery["student_matricula"],
        "course": solicitationQuery["student_course"]
      }]
    }
    professorParserToken={
      "user_name": solicitationQuery["advisor_name"],
      "gender": solicitationQuery["advisor_gender"],
      "profiles": [{
        "profile_acronym":"ADV",
        "siape": solicitationQuery["advisor_siape"]
      }]
    }
    
    dynamicPage = None
    if solicitationQuery["page_id"]:
      dynamicPage = getDynamicPage(solicitationQuery["page_id"], studentParserToken, professorParserToken)
    
    transitions = getTransitions(solicitationQuery["state_id"])

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
        "siape": solicitationQuery["advisor_siape"],
        "advisor_students": solicitationQuery["advisor_students"]
      },
      "solicitation":{
        "solicitation_name": solicitationQuery["solicitation_name"],
        "state_profile_editor_acronyms": solicitationQuery["profile_acronyms"],
        "state_description": solicitationQuery["state_description"],
        "state_max_duration_days": solicitationQuery["state_max_duration_days"],
        "actual_solicitation_state_id": solicitationQuery["actual_solicitation_state_id"],
        "solicitation_user_data": getFormatedMySQLJSON(solicitationQuery["solicitation_user_data"]),
        "user_has_solicitation_id": solicitationQuery["user_has_solicitation_id"],
        "user_has_state_id": solicitationQuery["user_has_state_id"],
        "is_accepted_by_advisor": solicitationQuery["is_accepted_by_advisor"],
        "decision": solicitationQuery["decision"],
        "reason": solicitationQuery["reason"],
        "start_datetime": str(solicitationQuery["start_datetime"]),
        "end_datetime": str(solicitationQuery["end_datetime"]),
        "transitions": transitions,
        "page": dynamicPage
      },
    }, 200
  
  # put to create solicitations - only for students
  def put(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("solicitation_id", location="json", type=int, required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, studentData = isAuthTokenValid(args, ["STU"])
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting put Single Solicitation for " + studentData["institutional_email"] + "\n# Reading data from DB")
    
    stateId = None
    stateTransitions = None
    stateMaxDurationDays = None
    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT ss.id AS state_id, ss.state_max_duration_days "
        "   FROM solicitation AS s JOIN solicitation_state AS ss ON s.id = ss.solicitation_id "
        "   WHERE s.id = %s AND ss.is_initial_state = TRUE; ",
        [(args["solicitation_id"])])

      if not queryRes:
        raise Exception("No initial state return for solicitation with id " + str(args["solicitation_id"]))
      
      stateId = queryRes["state_id"]
      stateMaxDurationDays = queryRes["state_max_duration_days"]
      stateTransitions = getTransitions(stateId)

      queryRes = dbGetSingle(
        " SELECT s.id	FROM user_account AS us "
	      "   JOIN user_has_solicitation AS uhs ON us.id = uhs.user_id "
	      "   JOIN solicitation AS s ON uhs.solicitation_id = s.id "
	      "   WHERE s.id = %s AND us.id = %s; ",
        [args["solicitation_id"], studentData["user_id"]])

    except Exception as e:
      print("# Database reading error:")
      print(e)
      traceback.print_exc()
      return "Erro na base de dados", 409

    if queryRes:
      abort(401, "Você já possui essa solicitação!")
    
    # set created date and finish date based on max day interval from solicitation state
    createdDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    finishDate = None if not stateMaxDurationDays else (datetime.now() + timedelta(days=stateMaxDurationDays)).strftime("%Y-%m-%d %H:%M:%S")
    
    userHasSolId = None
    userHasStateId = None

    print("# Sending mails")
    mailsSended = sendSolicitationMails(args["solicitation_id"], studentData)
    if not mailsSended:
      raise Exception("Error while sending start solicitation mails")

    # start transaction
    dbObjectIns = dbStartTransactionObj()
    try:
      # insert user solicitation
      dbExecute(
        " INSERT INTO user_has_solicitation "
        " (user_id, advisor_siape, solicitation_id, actual_solicitation_state_id, solicitation_user_data) VALUES "
        "   (%s, NULL, %s, %s, NULL); ",
        [studentData["user_id"], args["solicitation_id"], stateId], True, dbObjectIns)

      # select added user solicitation id
      queryRes = dbGetSingle(
        " SELECT uhs.id "
        "   FROM user_has_solicitation AS uhs "
        "   WHERE uhs.user_id = %s AND solicitation_id = %s; ",
        [studentData["user_id"], args["solicitation_id"]], True, dbObjectIns)
      
      if not queryRes:
        raise Exception("No return for user_has_solicitation insertion ")

      userHasSolId = queryRes["id"]

      # insert user solicitation state
      dbExecute(
        " INSERT INTO user_has_solicitation_state "
        " (user_has_solicitation_id, solicitation_state_id, decision, reason, start_datetime, end_datetime) VALUES "
        "   (%s, %s, \"Em analise\", \"Aguardando o aluno\", %s, %s); ",
        [userHasSolId, stateId, createdDate, finishDate], True, dbObjectIns)

      # select added user solicitation state id
      queryRes = dbGetSingle(
        " SELECT uhss.id "
        "   FROM user_has_solicitation_state AS uhss "
        "   WHERE uhss.user_has_solicitation_id = %s AND uhss.solicitation_state_id = %s; ",
        [userHasSolId, stateId], True, dbObjectIns)

      if not queryRes:
        raise Exception("No return for user_has_solicitation_state insertion ")
      
      userHasStateId = queryRes["id"]

      # schedule transitions for initial state if any
      scheduleTransitions(userHasStateId, stateTransitions, True, dbObjectIns)

    except Exception as e:
      dbRollback(dbObjectIns)
      print("# Database reading error:")
      print(e)
      traceback.print_exc()
      return "Erro na base de dados", 409

    # ends transaction
    dbCommit(dbObjectIns)
    print("# Operation done!")
    return { "user_has_solicitation_id": userHasSolId, "user_has_state_id": userHasStateId }, 200
      
  # post to resolve solicitations
  def post(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("user_has_state_id", location="json", type=int, required=True)
    args.add_argument("solicitation_user_data", location="json", required=True)
    args.add_argument("transition_id", location="json", type=int, required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, userData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    # parsing args data
    userHasStateId = args["user_has_state_id"]
    solicitationUserData = args["solicitation_user_data"]
    transitionId = args["transition_id"]

    if solicitationUserData:
      solicitationUserData = json.loads(
        solicitationUserData.replace("\'", "\"") if isinstance(solicitationUserData, str) else solicitationUserData.decode("utf-8"))
    
    print("\n# Starting post to resolve solicitation for " + userData["institutional_email"] + "\n# Reading data from DB")

    # gets solicitation state(sstate) data
    solStateData, error = getSolStateDataByUserStateId(userHasStateId)
    if error:
      return error, 409
    elif not solStateData:
      return "Usuario não possui o estado da solicitação!", 401
    
    # parses sstate data to student and advisor data format
    studentData, advisorData = createProfileDataBySolStateData(solStateData)

    # Verify solicitation args correcteness
    print("# Validating data")
    
    errorMsg = getUserSolStateChangeInvalidMsg(userData, studentData, advisorData, solStateData)
    if errorMsg != None:
      return errorMsg, 401
    errorMsg = getSolStateChangeInvalidMsg(solStateData)
    if errorMsg != None:
      return errorMsg, 401
    
    # gets sstate transitions and validade
    transitions = getTransitions(solStateData["solicitation_state_id"])

    if not transitions or len(transitions) == 0:
      return "Solicitação inválida!", 401

    transition = None
    for ts in transitions:
      if ts["id"] == transitionId:
        transition = ts
        break
    
    if transition == None:
      return "Transição não encontrada para este estado!", 404
    
    if transition["type"] == "from_dynamic_page":

      dynamicPage = None
      try:
        dynamicPage = getDynamicPage(solStateData["page_id"])
      except Exception as e:
        print("# Database reading error:")
        print(e)
        traceback.print_exc()
        return "Erro na base de dados", 409

      errorMsg = getDPageComponentsInvalidMsg(userData["user_id"], dynamicPage["components"], solicitationUserData)
      if errorMsg != None:
        return errorMsg, 401

    # gets next sstate data
    nextSolStateData, error = getTransitionSolStateData(transitionId)
    if error:
      return error, 409
    elif not solStateData:
      return "Transição não encontrada para este estado!", 404
    
    # get parsed solicitation user data
    parsedSolicitationUserData = getParsedSolicitationUserData(solStateData, solicitationUserData)

    # resolve solicitation change
    print("# Updating and Inserting data in db for state change")
    response, status = resolveSolStateChange(solStateData, transition, nextSolStateData, parsedSolicitationUserData, studentData, advisorData)

    return response, status
from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.utils import getFormatedMySQLJSON

# Data from multiple solicitations - coordinator
class CoordinatorSolicitations(Resource):

  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ["ADM","COO"])
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get Coordinator Solicitations for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    returnData = []
    try:
      queryRes = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS solicitation_state_id, ss.state_description, ss.state_max_duration_days, "
        " ssp.profile_acronym, "
        " uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, uhss.id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_state AS ss ON ss.id = uhss.solicitation_state_id "
        "     LEFT JOIN profile AS ssp ON ss.state_profile_editor = ssp.id "
        "     LEFT JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
        "     LEFT JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
        "     LEFT JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
        "     ORDER BY start_datetime DESC; ")
    
      for solic in queryRes:
        returnData.append({
          "student_id": solic[0],
          "student_name": solic[1],
          "advisor_id": solic[2],
          "advisor_name": solic[3] if solic[3] else "---",
          "solicitation_id": solic[4],
          "solicitation_name": solic[5],
          "state_id": solic[6],
          "state_description": solic[7],
          "state_max_duration_days": solic[8],
          "state_profile_editor_acronym": solic[9],
          "state_decision": solic[10],
          "state_reason": solic[11],
          "state_start_datetime": str(solic[12]),
          "state_end_datetime": str(solic[13]),
          "state_active": solic[14] == solic[6],
          "actual_solicitation_state_id": solic[14],
          "solicitation_user_data": getFormatedMySQLJSON(solic[15]),
          "user_has_state_id": solic[16]
        })

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Operation done!")
    return returnData, 200

# Data from multiple solicitations - advisor
class AdvisorSolicitations(Resource):

  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ["ADV"])
    if not isTokenValid:
      abort(401, errorMsg)
    
    print("\n# Starting get Advisor Solicitations for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    returnData = []
    try:

      queryRes = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS solicitation_state_id, ss.state_description, ss.state_max_duration_days, "
        " ssp.profile_acronym, "
        " uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, uhss.id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_state AS ss ON ss.id = uhss.solicitation_state_id "
        "     JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
        "     JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
        "     JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
        "     LEFT JOIN profile AS ssp ON ss.state_profile_editor = ssp.id "
        "     WHERE  uc_adv.id = %s AND (profile_acronym = \"ADV\" OR profile_acronym IS NULL) "
        "     ORDER BY start_datetime DESC; ",
        [(tokenData["user_id"])])
    
      for solic in queryRes:
        returnData.append({
          "student_id": solic[0],
          "student_name": solic[1],
          "advisor_id": solic[2],
          "advisor_name": solic[3] if solic[3] else "---",
          "solicitation_id": solic[4],
          "solicitation_name": solic[5],
          "state_id": solic[6],
          "state_description": solic[7],
          "state_max_duration_days": solic[8],
          "state_profile_editor_acronym": solic[9],
          "state_decision": solic[10],
          "state_reason": solic[11],
          "state_start_datetime": str(solic[12]),
          "state_end_datetime": str(solic[13]),
          "state_active": solic[14] == solic[6],
          "actual_solicitation_state_id": solic[14],
          "solicitation_user_data": getFormatedMySQLJSON(solic[15]),
          "user_has_state_id": solic[16]
        })

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Operation done!")
    return returnData, 200

# Data from multiple solicitations - student
class StudentSolicitations(Resource):

  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ["STU"])
    if not isTokenValid:
      abort(401, errorMsg)
    
    print("\n# Starting get Student Solicitations for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    returnData = []
    try:
      queryRes = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS solicitation_state_id, ss.state_description, ss.state_max_duration_days, "
        " ssp.profile_acronym, "
        " uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, uhss.id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_state AS ss ON ss.id = uhss.solicitation_state_id "
        "     LEFT JOIN profile AS ssp ON ss.state_profile_editor = ssp.id "
        "     LEFT JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
        "     LEFT JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
        "     LEFT JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
        "     WHERE uc_stu.id = %s AND (profile_acronym = \"STU\" OR profile_acronym IS NULL) "
        "     ORDER BY start_datetime DESC; ",
        [(tokenData["user_id"])])
    
      for solic in queryRes:
        returnData.append({
          "student_id": solic[0],
          "student_name": solic[1],
          "advisor_id": solic[2],
          "advisor_name": solic[3] if solic[3] else "---",
          "solicitation_id": solic[4],
          "solicitation_name": solic[5],
          "state_id": solic[6],
          "state_description": solic[7],
          "state_max_duration_days": solic[8],
          "state_profile_editor_acronym": solic[9],
          "state_decision": solic[10],
          "state_reason": solic[11],
          "state_start_datetime": str(solic[12]),
          "state_end_datetime": str(solic[13]),
          "state_active": solic[14] == solic[6],
          "actual_solicitation_state_id": solic[14],
          "solicitation_user_data": getFormatedMySQLJSON(solic[15]),
          "user_has_state_id": solic[16]
        })

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Operation done!")
    return returnData, 200
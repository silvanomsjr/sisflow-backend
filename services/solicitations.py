import json

from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse

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

    solicitationsData = None
    try:
      solicitationsData = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS state_id, ss.state_description, ss.state_max_duration_days, ss.state_static_page_name, "
        " uhss.decision AS state_decision, uhss.reason AS state_reason, "
        " uhss.start_datetime AS state_start_datetime, uhss.end_datetime AS state_end_datetime, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, uhs.is_accepted_by_advisor, uhss.id AS user_has_state_id, "
        " sspe.profile_acronyms "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_state AS ss ON ss.id = uhss.solicitation_state_id "
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
    
        "     ORDER BY state_start_datetime DESC; ")
    
      for solicitation in solicitationsData:
        solicitation["advisor_name"] = solicitation["advisor_name"] if solicitation["advisor_name"] else "---"
        solicitation["state_start_datetime"] = str(solicitation["state_start_datetime"])
        solicitation["state_end_datetime"] = str(solicitation["state_end_datetime"])
        solicitation["solicitation_user_data"] = getFormatedMySQLJSON(solicitation["solicitation_user_data"])
        solicitation["state_active"] = solicitation["actual_solicitation_state_id"] == solicitation["state_id"]

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    print(solicitationsData)

    print("# Operation done!")
    return solicitationsData, 200

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

    solicitationsData = None
    try:
      solicitationsData = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS state_id, ss.state_description, ss.state_max_duration_days, ss.state_static_page_name, "
        " uhss.decision AS state_decision, uhss.reason AS state_reason, "
        " uhss.start_datetime AS state_start_datetime, uhss.end_datetime AS state_end_datetime, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, uhs.is_accepted_by_advisor, uhss.id AS user_has_state_id, "
        " sspe.profile_acronyms "
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

        "     LEFT JOIN ( "
        "       SELECT sspe.solicitation_state_id, "
        "         GROUP_CONCAT(sspe.state_profile_editor) AS state_profile_editors, "
        "         GROUP_CONCAT(p.profile_acronym) AS profile_acronyms "
        "           FROM solicitation_state_profile_editors sspe "
        "           JOIN profile p ON sspe.state_profile_editor = p.id "
        "           GROUP BY sspe.solicitation_state_id) sspe ON ss.id = sspe.solicitation_state_id "

        "     ORDER BY state_start_datetime DESC; ")
    
      for solicitation in solicitationsData:
        solicitation["advisor_name"] = solicitation["advisor_name"] if solicitation["advisor_name"] else "---"
        solicitation["state_start_datetime"] = str(solicitation["state_start_datetime"])
        solicitation["state_end_datetime"] = str(solicitation["state_end_datetime"])
        solicitation["solicitation_user_data"] = getFormatedMySQLJSON(solicitation["solicitation_user_data"])
        solicitation["state_active"] = solicitation["actual_solicitation_state_id"] == solicitation["state_id"]

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Operation done!")
    return solicitationsData, 200

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

    solicitationsData = None
    try:
      solicitationsData = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS state_id, ss.state_description, ss.state_max_duration_days, ss.state_static_page_name, "
        " uhss.decision AS state_decision, uhss.reason AS state_reason, "
        " uhss.start_datetime AS state_start_datetime, uhss.end_datetime AS state_end_datetime, "
        " uhs.actual_solicitation_state_id, uhs.solicitation_user_data, uhs.is_accepted_by_advisor, uhss.id AS user_has_state_id, "
        " sspe.profile_acronyms "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_state AS ss ON ss.id = uhss.solicitation_state_id "
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

        "     ORDER BY state_start_datetime DESC; ")

      for solicitation in solicitationsData:
        solicitation["advisor_name"] = solicitation["advisor_name"] if solicitation["advisor_name"] else "---"
        solicitation["state_start_datetime"] = str(solicitation["state_start_datetime"])
        solicitation["state_end_datetime"] = str(solicitation["state_end_datetime"])
        solicitation["solicitation_user_data"] = getFormatedMySQLJSON(solicitation["solicitation_user_data"])
        solicitation["state_active"] = solicitation["actual_solicitation_state_id"] == solicitation["state_id"]

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Operation done!")
    return solicitationsData, 200
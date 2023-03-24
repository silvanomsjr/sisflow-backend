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

    print("\n# Starting get Coordinator Solicitations for " + tokenData["institutional_email"] + '\n# Reading data from DB')

    queryRes = None
    returnData = []
    try:
      queryRes = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_pro.id AS professor_id, uc_pro.user_name AS professor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS solicitation_step_id, ss.step_order_in_solicitation, ss.step_description, ss.step_max_duration_days, "
        " ssp.profile_acronym, "
        " uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " uhs.actual_solicitation_step_order, uhs.solicitation_user_data, uhss.id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_step AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_step AS ss ON s.id = ss.solicitation_id  "
        "     JOIN profile AS ssp ON ss.step_profile_editor = ssp.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "     WHERE ss.step_order_in_solicitation <= uhs.actual_solicitation_step_order "
        "     ORDER BY start_datetime DESC; ")
    
      for solic in queryRes:
        returnData.append({
          "student_id": solic[0],
          "student_name": solic[1],
          "professor_id": solic[2],
          "professor_name": solic[3] if solic[3] else '---',
          "solicitation_id": solic[4],
          "solicitation_name": solic[5],
          "step_id": solic[6],
          "step_active": solic[15] == solic[7],
          "step_order_in_solicitation": solic[7],
          "step_description": solic[8],
          "step_max_duration_days": solic[9],
          "step_profile_editor_acronym": solic[10],
          "step_decision": solic[11],
          "step_reason": solic[12],
          "step_start_datetime": str(solic[13]),
          "step_end_datetime": str(solic[14]),
          "solicitation_user_data": getFormatedMySQLJSON(solic[16]),
          "user_has_step_id": solic[17]
        })

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Operation done!")
    return returnData, 200

# Data from multiple solicitations - professor
class ProfessorSolicitations(Resource):

  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ["PRO"])
    if not isTokenValid:
      abort(401, errorMsg)
    
    print("\n# Starting get Professor Solicitations for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    returnData = []
    try:
      queryRes = dbGetAll(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, "
        " uc_pro.id AS professor_id, uc_pro.user_name AS professor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS solicitation_step_id, ss.step_order_in_solicitation, ss.step_description, ss.step_max_duration_days, "
        " ssp.profile_acronym, "
        " uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " uhs.actual_solicitation_step_order, uhs.solicitation_user_data, uhss.id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_step AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_step AS ss ON s.id = ss.solicitation_id  "
        "     JOIN profile AS ssp ON ss.step_profile_editor = ssp.id "
        "     JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "     WHERE ss.step_order_in_solicitation <= uhs.actual_solicitation_step_order AND uc_pro.id = %s AND profile_acronym=\"PRO\" "
        "     ORDER BY start_datetime DESC; ",
        [(tokenData['user_id'])])
    
      for solic in queryRes:
        returnData.append({
          "student_id": solic[0],
          "student_name": solic[1],
          "professor_id": solic[2],
          "professor_name": solic[3] if solic[3] else '---',
          "solicitation_id": solic[4],
          "solicitation_name": solic[5],
          "step_id": solic[6],
          "step_active": solic[15] == solic[7],
          "step_order_in_solicitation": solic[7],
          "step_description": solic[8],
          "step_max_duration_days": solic[9],
          "step_profile_editor_acronym": solic[10],
          "step_decision": solic[11],
          "step_reason": solic[12],
          "step_start_datetime": str(solic[13]),
          "step_end_datetime": str(solic[14]),
          "solicitation_user_data": getFormatedMySQLJSON(solic[16]),
          "user_has_step_id": solic[17]
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
        " uc_pro.id AS professor_id, uc_pro.user_name AS professor_name, "
        " s.id AS solicitation_id, s.solicitation_name, "
        " ss.id AS solicitation_step_id, ss.step_order_in_solicitation, ss.step_description, ss.step_max_duration_days, "
        " ssp.profile_acronym, "
        " uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "
        " uhs.actual_solicitation_step_order, uhs.solicitation_user_data, uhss.id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_step AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_step AS ss ON s.id = ss.solicitation_id  "
        "     JOIN profile AS ssp ON ss.step_profile_editor = ssp.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "     WHERE ss.step_order_in_solicitation <= uhs.actual_solicitation_step_order AND uc_stu.id = %s AND profile_acronym=\"STU\" "
        "     ORDER BY start_datetime DESC; ",
        [(tokenData['user_id'])])
    
      for solic in queryRes:
        returnData.append({
          "student_id": solic[0],
          "student_name": solic[1],
          "professor_id": solic[2],
          "professor_name": solic[3] if solic[3] else '---',
          "solicitation_id": solic[4],
          "solicitation_name": solic[5],
          "step_id": solic[6],
          "step_active": solic[15] == solic[7],
          "step_order_in_solicitation": solic[7],
          "step_description": solic[8],
          "step_max_duration_days": solic[9],
          "step_profile_editor_acronym": solic[10],
          "step_decision": solic[11],
          "step_reason": solic[12],
          "step_start_datetime": str(solic[13]),
          "step_end_datetime": str(solic[14]),
          "solicitation_user_data": getFormatedMySQLJSON(solic[16]),
          "user_has_step_id": solic[17]
        })

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Operation done!")
    return returnData, 200
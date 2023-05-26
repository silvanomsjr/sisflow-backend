from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import traceback

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

def getSolicitationAdvisor(userHasSolicitationId):

  try:
    sAdvQuery = dbGetSingle(
      " SELECT ua.id AS user_id, institutional_email, secondary_email, user_name, gender, phone, siape, 3 AS advisor_students "
      "   FROM user_has_solicitation AS uhs "
      "   JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
      "   JOIN user_has_profile AS uhp ON uhpad.user_has_profile_id = uhp.id "
      "   JOIN user_account AS ua ON uhp.user_id = ua.id "
      "   WHERE uhs.id = %s; ",(userHasSolicitationId,))
  except Exception as e:
    print("# Database reading error:")
    print(str(e))
    traceback.print_exc()
    return "Erro na base de dados", 409
  
  return sAdvQuery

def putSolicitationAdvisor(userHasSolicitationId, advisorSiape):
  try:
    dbExecute(
      " UPDATE user_has_solicitation SET "
      "   advisor_siape = %s, "
      "   is_accepted_by_advisor = FALSE "
      "   WHERE id = %s ",
      (advisorSiape, userHasSolicitationId))
  except Exception as e:
    print("# Database insertion error:")
    print(str(e))
    traceback.print_exc()
    return "Erro na base de dados", 409

  return "", 201

def allowSolicitationAdvisor(userHasSolicitationId, advisorSiape):
  try:
    dbExecute(
      " UPDATE user_has_solicitation SET "
      "   is_accepted_by_advisor = TRUE "
      "   WHERE id = %s AND advisor_siape = %s; ",
      (userHasSolicitationId, advisorSiape))
  except Exception as e:
    print("# Database insertion error:")
    print(str(e))
    traceback.print_exc()
    return "Erro na base de dados", 409

  return "", 201

# Data from solicitation advisor
class SolicitationAdvisor(Resource):

  # get solicitation advisor
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("user_has_solicitation_id", location="args", type=int, help="User solicitation data id, required", required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get solicitation advisor\n# Reading data from DB")
    advData = getSolicitationAdvisor(args["user_has_solicitation_id"])
    print("# Operation Done!")
    
    if not advData:
      return 'Orientador não encontrado', 404
    
    return advData, 200

  # put solicitation advisor
  def put(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("user_has_solicitation_id", location="json", type=int, help="User solicitation data id, required", required=True)
    args.add_argument("advisor_siape", location="json", type=str, help="Advisor unique Siape, required", required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)
    
    return putSolicitationAdvisor(args['user_has_solicitation_id'], args['advisor_siape'])

  # patch to allow solicitation advisor
  def patch(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("user_has_solicitation_id", location="json", type=int, help="User solicitation data id, required", required=True)
    args.add_argument("advisor_siape", location="json", type=str, help="Advisor unique Siape, required", required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)
    
    return allowSolicitationAdvisor(args['user_has_solicitation_id'], args['advisor_siape'])
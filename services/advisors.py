from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import traceback

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

def getAdvisors(offset=None, limit=None, advisorName=None):

  dbFilterScrypt, dbFilterScryptNoLimit, dbFilterValues, dbFilterValuesNoLimit = dbGetSqlFilterScrypt([
    {'filterCollum':'user_name', 'filterOperator':'LIKE%_%', 'filterValue': advisorName},
  ], groupByCollumns='ua.id',limitValue=limit, offsetValue=offset, getFilterWithoutLimits=True)

  advQuery = None
  advQueryCount = None
  try:
    advQuery = dbGetAll(
      " SELECT ua.id AS user_id, institutional_email, secondary_email, user_name, gender, phone, siape "
      "   FROM user_account ua "
      "   JOIN user_has_profile uhp ON ua.id = uhp.user_id "
      "   JOIN user_has_profile_advisor_data uhpad ON uhp.id = uhpad.user_has_profile_id "
      + dbFilterScrypt, dbFilterValues)

    advQueryCount = dbGetSingle(
      " SELECT COUNT(*) as count "
      "   FROM user_account ua "
      "   JOIN user_has_profile uhp ON ua.id = uhp.user_id "
      "   JOIN user_has_profile_advisor_data uhpad ON uhp.id = uhpad.user_has_profile_id "
      + dbFilterScryptNoLimit, dbFilterValuesNoLimit)
  except Exception as e:
    print("# Database reading error:")
    print(str(e))
    traceback.print_exc()
    return "Erro na base de dados", 409

  print(advQueryCount)
  if not advQuery or not advQueryCount:
    return "Orientadores não encontrados", 404
  
  return {
    "count": advQueryCount["count"],
    "advisors": advQuery
  }

# Data from solicitation transitions (State machine)
class Advisors(Resource):

  # get dynamic page data
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("start_row", location="args", type=int, help="Database starting row(offset) for lazy load")
    args.add_argument("quantity_rows", location="args", type=int, help="Database quantity of rows(limit) for lazy load")
    args.add_argument("advisor_name", location="args", type=str, help="Advisor name for filter")
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get advisors\n# Reading data from DB")
    advData = getAdvisors(args["start_row"], args["quantity_rows"], args["advisor_name"])
    print("# Operation Done!")
    
    return advData, 200
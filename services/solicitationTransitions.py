from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

def getTransitions(solicitationStateIdFrom):

  tsQuery = None
  try:
    tsQuery = dbGetAll(
      " SELECT sst.id, sst.solicitation_state_id_from, sst.solicitation_state_id_to, "
      " sstm.solicitation_state_transition_id AS manual_transition_id, "
      " sstdp.solicitation_state_transition_id AS dynamic_page_transition_id, "
      " sstdp.dynamic_page_component, sstdp.transition_decision, sstdp.transition_reason "
      "   FROM solicitation_state_transition sst "
      "   LEFT JOIN solicitation_state_transition_manual sstm ON sst.id = sstm.solicitation_state_transition_id "
      "   LEFT JOIN solicitation_state_transition_from_dynamic_page sstdp ON sst.id = sstdp.solicitation_state_transition_id "
      "   WHERE sst.solicitation_state_id_from = %s; ",
      (solicitationStateIdFrom,))
  except Exception as e:
    print("# Database reading error:")
    print(str(e))
    return "Erro na base de dados", 409

  if not tsQuery:
    return []
  
  tsParsed = []
  for transition in tsQuery:
    obj = {
      "id": transition["id"],
      "solicitation_state_id_from": transition["solicitation_state_id_from"],
      "solicitation_state_id_to": transition["solicitation_state_id_to"]
    }
    if transition["manual_transition_id"]:
      obj["type"] = "manual"
    if transition["dynamic_page_transition_id"]:
      obj["type"] = "from_dynamic_page"
      obj["dynamic_page_component"] = transition["dynamic_page_component"]
      obj["transition_decision"] = transition["transition_decision"]
      obj["transition_reason"] = transition["transition_reason"]

    tsParsed.append(obj)
  
  return tsParsed

# Data from solicitation transitions (State machine)
class SolicitationTransitions(Resource):

  # get dynamic page data
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("solicitation_state_id_from", location="args", type=int)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get solicitation transitions\n# Reading data from DB")
    tsData = getTransitions(args["solicitation_state_id_from"])
    print("# Operation Done!")
    
    return tsData, 200
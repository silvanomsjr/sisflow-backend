from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import traceback

from service.transitionService import getTransitions

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

# Data from solicitation transitions (State machine)
class SolicitationTransitions(Resource):

  # get transitions data
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("solicitation_state_id_from", location="args", type=int)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, _ = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get solicitation transitions\n# Reading data from DB")
    tsData = getTransitions(args["solicitation_state_id_from"])
    print("# Operation Done!")
    
    return tsData, 200
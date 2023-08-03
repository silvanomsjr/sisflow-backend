from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse

from service.dynamicPageService import getDynamicPage

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.utils import sistemStrParser

# Data from dynamic pages
class DynamicPage(Resource):

  # get dynamic page data
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("advisor_data", location="args", type=object)
    args.add_argument("student_data", location="args", type=object)
    args.add_argument("page_id", location="args", type=int, required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get dynamic page\n# Reading data from DB")
    dpData = getDynamicPage(args["page_id"], args["student_data"], args["advisor_data"])
    print("# Operation Done!")
    
    return dpData, 200
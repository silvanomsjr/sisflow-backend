from flask import abort
from flask_restful import Resource, reqparse
import traceback

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

# Data from dynamic pages
class Reasons(Resource):

  # get dynamic page data
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("class_names", location="args", type=str, help="Reason class names separated by comma")
    args.add_argument("reason_id", location="args", type=str)
    args.add_argument("reason_content", location="args", type=str)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get reasons\n# Reading data filtered from DB")

    filterScrypt = None
    filterValues = None

    queryStr = (
      " SELECT rclass.config_id AS reason_class_id, rclass.class_name AS reason_class_name, "
      " r.id AS reason_id, r.inner_html AS reason_inner_html "
      "   FROM config_reason_class rclass "
      "   JOIN config_reason r ON rclass.config_id = r.reason_class_id "
    )

    if args.get("class_names"):
      classNames = ' (' + ''.join(map(lambda el : (",\'" if el[0] > 0 else "\'") + str(el[1]) + "\'", enumerate(args["class_names"].split(",")))) + ') '
      queryStr += " WHERE rclass.class_name IN " + classNames
      filterScrypt, filterValues = dbGetSqlFilterScrypt([
        {'filterCollum':'r.id', 'filterOperator':'=', 'filterValue': args.get("reason_id")},
        {'filterCollum':'r.inner_html', 'filterOperator':'LIKE%_%', 'filterValue': args.get("reason_content")}
      ], initialSqlJunctionClause="")

      print(queryStr)

    else:
      filterScrypt, filterValues = dbGetSqlFilterScrypt([
        {'filterCollum':'r.id', 'filterOperator':'=', 'filterValue': args.get("reason_id")},
        {'filterCollum':'r.inner_html', 'filterOperator':'LIKE%_%', 'filterValue': args.get("reason_content")}
      ])

    qRes = None
    try:
      print(queryStr + filterScrypt, filterValues)
      qRes = dbGetAll(queryStr + filterScrypt, filterValues)
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      traceback.print_exc()
      return "Erro na base de dados", 409
    
    print("# Operation Done!")

    return { "reasons": qRes }, 200
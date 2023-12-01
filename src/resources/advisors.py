"""
Define the REST HTTP verbs relative to the advisors
"""

from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
from repositories import AdvisorsRepository
from util import parse_params_with_user_authentication

logging = logging.getLogger(__name__)

class AdvisorsResource(Resource):
    """ HTTP methods relative to the advisors """

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("advisor_name", location="args", type=str, help="Advisor name for filtering."),
        Argument("quantity_rows", location="args", type=int, help="Database quantity of rows(limit) for lazy load."),
        Argument("start_row", location="args", type=int, help="Database starting row(offset) for lazy load.")
    ])
    def get(jwt_data, advisor_name=None, quantity_rows=None, start_row=None):
        """ Return a list of advisors """
        formated_advisors = AdvisorsRepository.read_advisors(advisor_name=advisor_name, limit=quantity_rows, offset=start_row)
        return formated_advisors, 200
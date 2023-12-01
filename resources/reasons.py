"""
Define the REST HTTP verbs for reasons and its classes
"""

from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
from repositories import ReasonsRepository, SolicitationRepository, UserProfileTokenRepository
from util import parse_params_with_user_authentication, sysconf

logging = logging.getLogger(__name__)

class ReasonsResource(Resource):
    """ HTTP methods relative to the reasons """

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("user_has_state_id", location="args", type=int, required=True, help="Required. Id of the user has state used to parse the result."),
        Argument("class_names", location="args", type=str, help="Reason class names separated by comma, used to filter the result."),
        Argument("reason_id", location="args", type=str, help="Reason id, used to filter the result."),
        Argument("reason_content", location="args", type=str, help="Reason inner substring, used to filter the result.")
    ])
    def get(jwt_data, user_has_state_id, class_names=None, reason_id=None, reason_content=None):
        """ Get a filtered list of reasons """
        
        # read user ids from solicitation state
        state_user_ids = SolicitationRepository.read_solicitation_state_user_ids(user_has_state_id)
        
        # read student and advisor tokens to parse the strings from reasons
        student_token = None
        advisor_token = None

        if(state_user_ids):
            student_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["student_id"])
            advisor_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["advisor_id"])

        # format the reasons
        formatted_reasons_response = ReasonsRepository.read_reasons(sysconf, student_token, advisor_token, class_names, reason_id, reason_content)
        return formatted_reasons_response, 200
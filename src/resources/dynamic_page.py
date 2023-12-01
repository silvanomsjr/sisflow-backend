"""
Define the REST HTTP verbs relative to the dynamic pages and its components
"""

from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
from repositories import DynamicPageRepository, SolicitationRepository, UserProfileTokenRepository
from util import parse_params_with_user_authentication, sysconf

logging = logging.getLogger(__name__)

class DynamicPageResource(Resource):
    """ HTTP methods relative to the dynamic page """

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("page_id", location="args", type=int, required=True, help="Required. Id of the dynamic page."),
        Argument("user_has_state_id", location="args", type=int, help="Id of the user has state used to parse the result."),
    ])
    def get(jwt_data, page_id, user_has_state_id=None):
        """ Get a dynamic page and its components """

        student_token = None
        advisor_token = None

        if user_has_state_id:
            
            # read user ids from solicitation state
            state_user_ids = SolicitationRepository.read_solicitation_state_user_ids(user_has_state_id)
        
            # read student and advisor tokens to parse the strings from reasons
            if(state_user_ids):
                student_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["student_id"])
                advisor_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["advisor_id"])

        formatted_dynamic_page = DynamicPageRepository.read_dynamic_page(sysconf, student_token, advisor_token, page_id)
        return formatted_dynamic_page, 200
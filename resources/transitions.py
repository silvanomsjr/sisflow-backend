"""
Define the REST HTTP verbs for transitions
"""

from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
from repositories import SolicitationStateTransitionsRepository
from util import parse_params_with_user_authentication

logging = logging.getLogger(__name__)

class SolicitationStateTransitionsResource(Resource):
    """ HTTP methods relative to transitions """

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("solicitation_state_id_from", location="args", type=int, required=True, help="Required. Id of the originating solicitation state.")
    ])
    def get(jwt_data, solicitation_state_id_from):
        """ Get a formatted list of transitions """
        formatted_transitions = SolicitationStateTransitionsRepository.read_solicitation_state_transitions(solicitation_state_id_from)
        return formatted_transitions, 200
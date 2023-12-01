"""
Define the REST HTTP verbs for solicitation advisors
"""
from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
from repositories import SolicitationRepository, UserRepository, UserProfileTokenRepository
from util import parse_params_with_user_authentication

logging = logging.getLogger(__name__)

class SolicitationAdvisorResource(Resource):
    """ HTTP methods relative to solicitation advisors """

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("user_has_solicitation_id", location="args", type=int, required=True, help="Required. Id of the user solicitation.")
    ])
    def get(jwt_data, user_has_solicitation_id):
        """ Get a advisor by its solicitation """

        solicitation_user_ids = SolicitationRepository.read_solicitation_user_ids(user_has_solicitation_id)
        if not solicitation_user_ids:
            return "Estado do orientador não encontrado", 404
        
        if not solicitation_user_ids["advisor_id"]:
            return "A solicitação não possui um orientador", 401
        
        advisor_token = UserProfileTokenRepository.read_user_profile_token(solicitation_user_ids["advisor_id"])
        if not advisor_token:
            return "Orientador não encontrado", 404

        return advisor_token, 200

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("user_has_solicitation_id", location="json", type=int, required=True, help="Required. Id of the user solicitation."),
        Argument("advisor_siape", location="json", type=str, required=True, help="Required. Advisor unique Siape")
    ])
    def put(jwt_data, user_has_solicitation_id, advisor_siape):
        """ A student put a advisor and waits for its aproval in patch """
        
        # read user ids from solicitation
        state_user_ids = SolicitationRepository.read_solicitation_user_ids(user_has_solicitation_id)
        if not state_user_ids:
            return "Estado do usuário não encontrado", 404

        # check if the user can perform the put
        if not "ADM" in jwt_data["profile_acronyms"] and not "COO" in jwt_data["profile_acronyms"]:
            if jwt_data["user_id"] != state_user_ids["student_id"] and jwt_data["user_id"] != state_user_ids["advisor_id"]:
                return "Acesso a solicitação não permitido", 401

        # check if siape exists
        advisor = UserRepository.read_advisor_profile_user(advisor_siape)
        if not advisor:
            return "Orientador com o SIAPE não encontrado", 404

        user_solicitation = SolicitationRepository.update_user_solicitation(user_has_solicitation_id, advisor_siape=advisor_siape)
        if not user_solicitation:
            return "Erro ao adicionar o orientador", 500

        return "", 201

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("user_has_solicitation_id", location="json", type=int, required=True, help="Required. Id of the user solicitation."),
        Argument("advisor_siape", location="json", type=str, required=True, help="Required. Advisor unique Siape")
    ])
    def patch(jwt_data, user_has_solicitation_id, advisor_siape):
        """ A student put a advisor and waits for its aproval in patch """

        # read user ids from solicitation
        state_user_ids = SolicitationRepository.read_solicitation_user_ids(user_has_solicitation_id)
        if not state_user_ids:
            return "Estado do usuário não encontrado", 404

        # check if the user can perform the put
        if not "ADM" in jwt_data["profile_acronyms"] and not "COO" in jwt_data["profile_acronyms"]:
            if jwt_data["user_id"] != state_user_ids["advisor_id"]:
                return "Acesso a solicitação não permitido", 401
        
        # check if siape exists
        advisor = UserRepository.read_advisor_profile_user(advisor_siape)
        if not advisor:
            return "Orientador com o SIAPE não encontrado", 404
        
        user_solicitation = SolicitationRepository.update_user_solicitation(user_has_solicitation_id, is_accepted_by_advisor=True)
        if not user_solicitation:
            return "Erro ao adicionar o orientador", 500

        return "", 201
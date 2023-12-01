"""
Define the REST HTTP verbs for solicitation
"""

from flask_restful import Resource
from flask_restful.reqparse import Argument

import json
import logging
from datetime import datetime, timedelta
from repositories import (
    DynamicPageRepository, SolicitationRepository, SolicitationStateTransitionsRepository, 
    UserProfileTokenRepository
)
from util import (
    is_solicitation_dynamic_page_components_valid, is_solicitation_profile_edition_allowed, 
    is_solicitation_edition_allowed, parse_new_old_solicitation_user_data, parse_params_with_user_authentication,
    resolve_solicitation_state_change, schedule_transitions, sysconf, SystemConfiguration, syssmtpserver
)

logging = logging.getLogger(__name__)

class SolicitationResource(Resource):
    """ HTTP methods relative to solicitation """

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("user_has_state_id", location="args", type=int, required=True, help="Required. Id of the user has state.")
    ])
    def get(jwt_data, user_has_state_id):
        """ Get data from a user solicitation state """

        # read user ids from solicitation state
        state_user_ids = SolicitationRepository.read_solicitation_state_user_ids(user_has_state_id)

        if not state_user_ids:
            return "Estado do usuário não encontrado", 404

        # get student and advisor tokens to parse the strings from dynamic page components and e-mails
        student_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["student_id"])
        advisor_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["advisor_id"])

        # check if user has access
        if not "ADM" in jwt_data["profile_acronyms"] and not "COO" in jwt_data["profile_acronyms"]:
            if jwt_data["user_id"] != state_user_ids["student_id"] and jwt_data["user_id"] != state_user_ids["advisor_id"]:
                return "Acesso a solicitação não permitido", 401

        # get user has solicitation state data formatted
        formatted_uhss = SolicitationRepository.read_user_solicitation_state(user_has_state_id)
        if not formatted_uhss:
            return "Usuario não possui o estado da solicitação", 404

        # get transitions and dynamic page
        transitions = SolicitationStateTransitionsRepository.read_solicitation_state_transitions(formatted_uhss["state_id"])
        dynamic_page = DynamicPageRepository.read_dynamic_page(sysconf, student_token, advisor_token, formatted_uhss["state_dynamic_page_id"])
        
        # get profile tokens
        student_token_profile = SystemConfiguration.get_user_token_profile(student_token, "STU")
        advisor_token_profile = SystemConfiguration.get_user_token_profile(advisor_token, "ADV") if advisor_token else None

        # format the response
        formatted_res = {
            "student": student_token,
            "advisor": advisor_token,
            "solicitation": formatted_uhss
        }
        formatted_res["student"]["matricula"] = student_token_profile["matricula"]
        formatted_res["student"]["course"] = student_token_profile["course"]
        if advisor_token:
            formatted_res["advisor"]["siape"] = advisor_token_profile["siape"]
            formatted_res["advisor"]["advisor_students"] = advisor_token_profile["advisor_students"]
        formatted_res["solicitation"]["transitions"] = transitions
        formatted_res["solicitation"]["page"] = dynamic_page
        
        return formatted_res, 200

    @staticmethod
    @parse_params_with_user_authentication(accepted_profiles=["STU"], reqparse_arguments=[
        Argument("solicitation_id", location="json", type=int, required=True, help="Required. Id of the solicitation to be created.")
    ])
    def put(jwt_data, solicitation_id):
        """ Put to create a student solicitation """

        # read solicitation data
        solicitation_data = SolicitationRepository.read_solicitation(solicitation_id)
        if not solicitation_data or not solicitation_data["solicitation"] or not solicitation_data["solicitation_initial_state"]:
            return "Dados da solicitação não encontrados", 404
        
        solicitation = solicitation_data["solicitation"]
        s_initial_state = solicitation_data["solicitation_initial_state"]
        s_initial_mails = solicitation_data["solicitation_initial_mails"]
        s_initial_state_transitions = SolicitationStateTransitionsRepository.read_solicitation_state_transitions(s_initial_state["id"])

        # checks if user has solicitation
        uhs = SolicitationRepository.read_user_solicitation(user_id=jwt_data["user_id"], solicitation_id=solicitation_id)
        if uhs != None:
            return "Você já possui essa solicitação", 401

        # set dates
        start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        end_datetime = None if not s_initial_state["state_max_duration_days"] \
            else (datetime.now() + timedelta(days=s_initial_state["state_max_duration_days"])).strftime("%Y-%m-%d %H:%M:%S")

        # send mails
        for mail in s_initial_mails:
      
            # parses mail subject and body
            parsed_subject = sysconf.sistem_str_parser(mail["mail_subject"], jwt_data)
            parsed_body = sysconf.sistem_str_parser(mail["mail_body_html"], jwt_data)

            # sends to student and coordinator profiles
            if mail["is_sent_to_student"]:
                syssmtpserver.add_email(jwt_data['institutional_email'], parsed_subject, parsed_body)
            if mail["is_sent_to_coordinator"]:
                syssmtpserver.add_email(sysconf.coordinator_email, parsed_subject, parsed_body)

        # creates the user solicitation
        user_has_solicitation = SolicitationRepository.create_user_solicitation(
            jwt_data["user_id"], None, solicitation["id"], s_initial_state["id"]
        )
        if not user_has_solicitation:
            return "Erro ao criar a solicitação do usuário", 500

        # creates the initial user solicitation state
        user_has_solicitation_state = SolicitationRepository.create_user_solicitation_state(
            user_has_solicitation.id, s_initial_state["id"], "Em analise", start_datetime, "Aguardando o aluno", end_datetime
        )
        if not user_has_solicitation_state:
            return "Erro ao criar o estado da solicitação do usuário", 500

        # schedule possible event transitions
        schedule_transitions(user_has_solicitation.id, s_initial_state_transitions)

        return {
            "user_has_solicitation_id": user_has_solicitation.id, 
            "user_has_state_id": user_has_solicitation_state.id 
        }, 200

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("user_has_state_id", location="json", type=int, required=True, help="Required. Id of user has solicitation state"),
        Argument("solicitation_user_data", location="json", required=True, help="Required. User has solicitation data json"),
        Argument("transition_id", location="json", type=int, required=True, help="Required. Id of the transition to be executed"),
        Argument("validate_dynamicpage_fields", location="json", type=int, help="If the validation is necessary")
    ])
    def post(jwt_data, user_has_state_id, solicitation_user_data, transition_id, validate_dynamicpage_fields=1):
        """ Post to update and transit in the state machine of a solicitation """

        # read user ids from solicitation state
        state_user_ids = SolicitationRepository.read_solicitation_state_user_ids(user_has_state_id)

        if not state_user_ids:
            return "Estado do usuário não encontrado", 404

        # get student and advisor tokens to parse the strings from dynamic page components and e-mails
        student_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["student_id"])
        advisor_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["advisor_id"])

        # parses the solicitation_user_data to a correct json format
        if solicitation_user_data:
            solicitation_user_data = json.loads(
                solicitation_user_data.replace("\'", "\"") if isinstance(solicitation_user_data, str) else solicitation_user_data.decode("utf-8"))
        
        if not "inputs" in solicitation_user_data or not "uploads" in solicitation_user_data or not "select_uploads" in solicitation_user_data:
            return "Dados do usuário inválidos", 401

        # gets user solicitation and state data 
        formatted_uhss = SolicitationRepository.read_user_solicitation_state(user_has_state_id, convert_dates_to_str=False)
        if not formatted_uhss:
            return "Estado do usuário não encontrado", 404

        # checks if the edition of the solicitation can be done
        is_allowed, error_msg = is_solicitation_profile_edition_allowed(jwt_data, student_token, advisor_token, formatted_uhss)
        if not is_allowed:
            return error_msg, 401
        is_allowed, error_msg = is_solicitation_edition_allowed(formatted_uhss)
        if not is_allowed:
            return error_msg, 401

        # gets sstate transitions and validade
        transitions = SolicitationStateTransitionsRepository.read_solicitation_state_transitions(formatted_uhss["state_id"])
        if not transitions or len(transitions) == 0:
            return "Transições da solicitação inválidas", 500

        # get transition and parses
        transition = None
        for ts in transitions:
            if ts["id"] == transition_id:
                transition = ts
                break
    
        if transition == None:
            return "Transição não encontrada para este estado", 404
        
        if transition["type"] == "from_dynamic_page":
            dynamic_page = DynamicPageRepository.read_dynamic_page(
                sysconf, student_token, advisor_token, formatted_uhss["state_dynamic_page_id"]
            )
            
            if validate_dynamicpage_fields:
                is_valid, error_msg = is_solicitation_dynamic_page_components_valid(
                    jwt_data["user_id"], dynamic_page["components"], solicitation_user_data
                )
                if not is_valid:
                    return error_msg, 401

        # gets next sstate data
        next_ss_data = SolicitationRepository.read_solicitation_state(transition["solicitation_state_id_to"])\
            if transition["solicitation_state_id_to"] else None

        # get parsed solicitation user data using old and new data
        parsed_user_Data = parse_new_old_solicitation_user_data(formatted_uhss["solicitation_user_data"], solicitation_user_data)

        # resolve solicitation change
        response, status = resolve_solicitation_state_change(formatted_uhss, transition, next_ss_data, parsed_user_Data, student_token, advisor_token)

        return response, status
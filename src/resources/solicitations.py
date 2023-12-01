"""
Define the REST HTTP verbs for solicitations
"""

from flask_restful import Resource

import logging
from repositories import UserRepository, SolicitationsRepository
from util import parse_params_with_user_authentication

logging = logging.getLogger(__name__)

def get_formated_user_solicitations(user_solicitations):
    """ Reusable function that formats all solicitation """

    # for each solicitation
    formated_user_solicitations = {"solicitations":[], "count": len(user_solicitations)}
    for us in user_solicitations:

        # get its users
        solicitation = us.solicitation
        us_student = UserRepository.read_user(id=us.user_id)
        us_advisor = UserRepository.read_advisor_profile_user(siape=us.advisor_siape)

        # format
        us_formatted = {
            "solicitation_id": us.solicitation_id,
            "solicitation_name": solicitation.solicitation_name,
            "student_id": us_student.id,
            "student_name": us_student.user_name,
            "advisor_id": us_advisor.id if us_advisor else None,
            "advisor_name": us_advisor.user_name if us_advisor else "---",
            "is_accepted_by_advisor": us.is_accepted_by_advisor,
            "solicitation_user_data": us.solicitation_user_data,
            "actual_solicitation_state_id": us.actual_solicitation_state_id,
            "states": []
        }

        # add profile acronyms
        for us_state in us.user_has_solicitation_state:

            state = us_state.solicitation_state
            state_profiles_acronyms = ""

            for state_profile in state.solicitation_state_profile_editors:
                state_profiles_acronyms += ("," if len(state_profiles_acronyms) else "") + state_profile.profile.profile_acronym

            us_state_formatted = {
                "user_has_state_id": us_state.id,
                "state_id": state.id,
                "state_description": state.state_description,
                "state_profile_acronyms": state_profiles_acronyms,
                "state_active": us.actual_solicitation_state_id == state.id,
                "state_max_duration_days": state.state_max_duration_days,
                "state_static_page_name": state.state_static_page_name,
                "state_decision": us_state.decision,
                "state_reason": us_state.reason,
                "state_start_datetime": us_state.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "state_end_datetime": us_state.end_datetime.strftime("%Y-%m-%d %H:%M:%S") if us_state.end_datetime else None,
            }

            # append all data
            us_formatted["states"].append(us_state_formatted)
        formated_user_solicitations["solicitations"].append(us_formatted)
    return formated_user_solicitations

class SolicitationsCoordinatorResource(Resource):
    """ HTTP methods relative to coordinator solicitations """

    @staticmethod
    @parse_params_with_user_authentication(accepted_profiles=["ADM","COO"])
    def get(jwt_data):
        """ Get list of all solicitations of a authorized coordinator or admin """
        all_user_solicitations = SolicitationsRepository.read_user_solicitations()
        response = get_formated_user_solicitations(all_user_solicitations)
        return response, 200

class SolicitationsAdvisorResource(Resource):
    """ HTTP methods relative to advisor solicitations """

    @staticmethod
    @parse_params_with_user_authentication(accepted_profiles=["ADV"])
    def get(jwt_data):
        """ Get list of all solicitations of a authorized advisor """
        advisor_solicitations = SolicitationsRepository.read_user_solicitations(advisor_id=jwt_data["user_id"])
        response = get_formated_user_solicitations(advisor_solicitations)
        return response, 200

class SolicitationsStudentResource(Resource):
    """ HTTP methods relative to student solicitations """

    @staticmethod
    @parse_params_with_user_authentication(accepted_profiles=["STU"])
    def get(jwt_data):
        """ Get list all solicitations of a authorized student """
        student_solicitations = SolicitationsRepository.read_user_solicitations(student_id=jwt_data["user_id"])
        response = get_formated_user_solicitations(student_solicitations)
        return response, 200
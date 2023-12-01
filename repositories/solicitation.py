""" Defines the User Solicitation repository """

import json
from datetime import datetime
from models import Solicitation, SolicitationState, UserHasProfileAdvisorData, UserHasSolicitation, UserHasSolicitationState

class SolicitationRepository:
    """ The repository for single user solicitations """

    @staticmethod
    def create_user_solicitation(user_id, advisor_siape, solicitation_id, actual_solicitation_state_id, is_accepted_by_advisor=False, solicitation_user_data=None):
        """ Create a user has solicitation """
        user_has_solicitation = UserHasSolicitation(user_id, advisor_siape, solicitation_id, actual_solicitation_state_id, is_accepted_by_advisor, solicitation_user_data)
        return user_has_solicitation.save()
    
    @staticmethod
    def create_user_solicitation_state(user_has_solicitation_id, solicitation_state_id, decision, start_datetime, reason=None, end_datetime=None):
        """ Create a user has solicitation state """
        user_has_solicitation_state = UserHasSolicitationState(user_has_solicitation_id, solicitation_state_id, decision, start_datetime, reason, end_datetime)
        return user_has_solicitation_state.save()

    @staticmethod
    def read_solicitation(solicitation_id, include_initial_state=True, include_initial_mails=True):
        """ Read and format a solicitation """

        # query solicitation
        solicitation_query = Solicitation.query.filter_by(id=solicitation_id)
        if solicitation_query.count() != 1:
            return None
        
        # returns if not include state and mail
        solicitation = solicitation_query.one()
        if not include_initial_state and not include_initial_mails:
            return solicitation
        
        # creates the data token
        solicitation_data = {
            "solicitation": solicitation.json,
        }

        # add initial state
        if include_initial_state:
            initial_state_query = SolicitationState.query.filter(SolicitationState.solicitation_id == solicitation_id, SolicitationState.is_initial_state)
            print('count', initial_state_query.count())
            initial_state = initial_state_query.one() if initial_state_query.count() == 1 else None
            solicitation_data["solicitation_initial_state"] = initial_state.json
        
        # add initial mails
        if include_initial_mails:
            initial_mails = solicitation.solicitation_start_mail
            formatted_initial_mails = []
            for mail in initial_mails:
                dynamic_mail = mail.dynamic_mail
                formatted_initial_mails.append(dynamic_mail.json)
            solicitation_data["solicitation_initial_mails"] = formatted_initial_mails

        return solicitation_data
    
    @staticmethod
    def read_solicitation_state(solicitation_state_id, include_profile_editors=True):
        """ Read and format a solicitation state """

        # query solicitation
        ss_query = SolicitationState.query.filter_by(id=solicitation_state_id)
        if ss_query.count() != 1:
            return None
        
        # returns if not include state and mail
        ss = ss_query.one()
        if not include_profile_editors:
            return ss
        
        # parses state profile editors
        ss_profile_editors = ss.solicitation_state_profile_editors
        state_profile_editor_acronyms = ""
        state_profile_editor_names = ""
        for ss_profile_editor in ss_profile_editors:
            profile = ss_profile_editor.profile
            state_profile_editor_acronyms += ("," if len(state_profile_editor_acronyms) > 0 else "") + profile.profile_acronym
            state_profile_editor_names += ("," if len(state_profile_editor_names) > 0 else "") + profile.profile_name

        # formats the result
        formatted_ss = ss.json
        formatted_ss["state_profile_editor_acronyms"] = state_profile_editor_acronyms
        formatted_ss["state_profile_editor_names"] = state_profile_editor_names

        return formatted_ss

    @staticmethod
    def read_user_solicitation(user_has_solicitation_id=None, user_id=None, solicitation_id=None):
        """ Read a user solicitation """

        # returns a user_has_solicitation given its user_has_solicitation_id
        if user_has_solicitation_id:
            uhs_query = UserHasSolicitation.query.filter_by(id=user_has_solicitation_id)
            return uhs_query.one() if uhs_query.count() == 1 else None
        
        # returns a user_has_solicitation given its user_id and solicitation_id
        elif user_id and solicitation_id:
            uhs_query = UserHasSolicitation.query.filter(UserHasSolicitation.user_id == user_id, UserHasSolicitation.solicitation_id == solicitation_id)
            return uhs_query.one() if uhs_query.count() == 1 else None
        
        return None
    
    @staticmethod
    def read_user_solicitation_state(user_has_state_id, format=True, convert_dates_to_str=True):
        """ Query user has solicitation state by its id """
        
        uhss_query = UserHasSolicitationState.query.filter_by(id=user_has_state_id)
        if uhss_query.count() != 1:
            return None

        uhss = uhss_query.one()
        if not format:
            return uhss

        # read other tables
        uhs = uhss.user_has_solicitation
        s_state = uhss.solicitation_state
        solicitation = s_state.solicitation
        ss_profile_editors = s_state.solicitation_state_profile_editors

        # parses state profile acronyms
        state_profile_editor_acronyms = ""
        state_profile_editor_names = ""
        for ss_profile_editor in ss_profile_editors:
            profile = ss_profile_editor.profile
            state_profile_editor_acronyms += ("," if len(state_profile_editor_acronyms) > 0 else "") + profile.profile_acronym
            state_profile_editor_names += ("," if len(state_profile_editor_names) > 0 else "") + profile.profile_name
        
        # parse dates
        start_datetime = uhss.start_datetime
        end_datetime = uhss.end_datetime
        if convert_dates_to_str:
            start_datetime = start_datetime.strftime("%Y-%m-%d %H:%M:%S") if start_datetime else ""
            end_datetime = end_datetime.strftime("%Y-%m-%d %H:%M:%S") if end_datetime else ""
        
        # parse user data
        solicitation_user_data = uhs.solicitation_user_data
        if isinstance(solicitation_user_data, str):
            solicitation_user_data = json.loads(solicitation_user_data)

        # parse and return the response
        return{
            "solicitation_id": solicitation.id,
            "solicitation_name": solicitation.solicitation_name,
            "state_id": s_state.id,
            "state_dynamic_page_id": s_state.state_dynamic_page_id,
            "state_profile_editor_acronyms": state_profile_editor_acronyms,
            "state_profile_editor_names": state_profile_editor_names,
            "state_description": s_state.state_description,
            "state_max_duration_days": s_state.state_max_duration_days,
            "actual_solicitation_state_id": uhs.actual_solicitation_state_id,
            "solicitation_user_data": solicitation_user_data,
            "user_has_solicitation_id": uhs.id,
            "user_has_state_id": uhss.id,
            "is_accepted_by_advisor": uhs.is_accepted_by_advisor,
            "decision": uhss.decision,
            "reason": uhss.reason,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
        }

    @staticmethod
    def read_solicitation_user_ids(user_has_solicitation_id):
        """ Query student and advisor ids from user has solicitation by its id """

        user_has_solicitation = SolicitationRepository.read_user_solicitation(user_has_solicitation_id)
        if not user_has_solicitation:
            return None

        # advisor
        uhpd_query = UserHasProfileAdvisorData.query.filter_by(siape=user_has_solicitation.advisor_siape)
        user_has_profile_advisor_data = uhpd_query.one() if uhpd_query.count() == 1 else None
        advisor_user_has_profile = user_has_profile_advisor_data.user_has_profile if user_has_profile_advisor_data else None

        response = {
            "student_id": user_has_solicitation.user_id,
            "advisor_id": advisor_user_has_profile.user_id if advisor_user_has_profile else None
        }
        
        return response
    
    @staticmethod
    def read_solicitation_state_user_ids(user_has_state_id):
        """ Query student and advisor ids from user has solicitation state by its id """

        user_has_solicitation_state = SolicitationRepository.read_user_solicitation_state(user_has_state_id, format=False)
        
        if not user_has_solicitation_state:
            return None

        # user    
        user_has_solicitation = user_has_solicitation_state.user_has_solicitation

        # advisor
        uhpd_query = UserHasProfileAdvisorData.query.filter_by(siape=user_has_solicitation.advisor_siape)
        user_has_profile_advisor_data = uhpd_query.one() if uhpd_query.count() == 1 else None
        advisor_user_has_profile = user_has_profile_advisor_data.user_has_profile if user_has_profile_advisor_data else None

        response = {
            "student_id": user_has_solicitation.user_id,
            "advisor_id": advisor_user_has_profile.user_id if advisor_user_has_profile else None
        }
        
        return response

    @staticmethod
    def update_user_solicitation(user_has_solicitation_id, solicitation_user_data=None, actual_solicitation_state_id=None, advisor_siape=None, is_accepted_by_advisor=None):
        """ Update a user solicitation """

        # read user has solicitation
        uhs = SolicitationRepository.read_user_solicitation(user_has_solicitation_id)
        if not uhs:
            return None

        # update its fields and save
        if solicitation_user_data:
            uhs.solicitation_user_data = solicitation_user_data
        if actual_solicitation_state_id:
            uhs.actual_solicitation_state_id = actual_solicitation_state_id
        if advisor_siape:
            uhs.advisor_siape = advisor_siape
        if is_accepted_by_advisor:
            uhs.is_accepted_by_advisor = is_accepted_by_advisor

        return uhs.save()
    
    @staticmethod
    def update_user_solicitation_state(user_has_state_id, decision, reason):
        """ Update a user solicitation state """

        # read user has solicitation state
        uhss = SolicitationRepository.read_user_solicitation_state(user_has_state_id, False)
        if not uhss:
            return None

        # update its fields and save    
        uhss.decision = decision
        uhss.reason = reason
        return uhss.save()
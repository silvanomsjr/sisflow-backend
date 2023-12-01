""" Defines the Transitions repository """

from models import SolicitationStateTransition

def format_solicitation_state_transition(sst):
    """ format each of the transitions by its type """
    formatted_sst = None

    if sst.solicitation_state_transition_manual:
        formatted_sst = format_sst_manual(sst)
    elif sst.solicitation_state_transition_from_dynamic_page:
        formatted_sst = format_sst_dynamic_page(sst)
    elif sst.solicitation_state_transition_scheduled:
        formatted_sst = format_sst_scheduled(sst)
    elif sst.solicitation_state_transition_mail:
        formatted_sst = format_sst_mail(sst)
    
    return formatted_sst

def format_sst_manual(sst):
    """ formats a manual transition """
    sst_manual = sst.solicitation_state_transition_manual
    return {
        "type": "manual",
        "transition_decision": sst_manual.transition_decision,
        "transition_reason": sst_manual.transition_reason
    }

def format_sst_dynamic_page(sst):
    """ formats a dynamic page transition """
    sst_dp = sst.solicitation_state_transition_from_dynamic_page
    return {
        "type": "from_dynamic_page",
        "dynamic_page_component": sst_dp.dynamic_page_component,
        "transition_decision": sst_dp.transition_decision,
        "transition_reason": sst_dp.transition_reason
    }

def format_sst_scheduled(sst):
    """ formats a scheduled transition """
    sst_scheduled = sst.solicitation_state_transition_scheduled
    return {
        "type": "scheduled",
        "transition_decision": sst_scheduled.transition_decision,
        "transition_reason": sst_scheduled.transition_reason,
        "transition_delay_seconds": sst_scheduled.transition_delay_seconds
    }

def format_sst_mail(sst):
    """ formats a mail transition """
    sst_mails = sst.solicitation_state_transition_mail

    formatted_sst_mails = {
        "type": "mail",
        "mails": []
    }
    for sst_mail in sst_mails:
        formatted_sst_mails["mails"].append({
            "mail_transition_id": sst_mail.id,
            "dynamic_mail_id": sst_mail.dynamic_mail_id
        })
        
    return formatted_sst_mails

class SolicitationStateTransitionRepository:
    """ The repository for a single solicitation state transition """

    @staticmethod
    def read_solicitation_state_transition_mails(transition_id):
        """ Query transition mails given transition id """

        # query the transitions
        sst_query = SolicitationStateTransition.query.filter_by(id=transition_id)
        if sst_query.count() != 1:
            return None
        
        sst = sst_query.one()
        sst_mails = sst.solicitation_state_transition_mail
        
        # returns if it is not to format
        formatted_sst_mails = []
        for mail in sst_mails:
            dynamic_mail = mail.dynamic_mail
            formatted_sst_mails.append(dynamic_mail.json)
        
        return formatted_sst_mails

class SolicitationStateTransitionsRepository:
    """ The repository for multiple solicitation state transitions """

    @staticmethod
    def read_solicitation_state_transitions(solicitation_state_id_from, format=True):
        """ Query all transitions from a originating solicitation state given its id """

        # query the solicitations
        ssts_query = SolicitationStateTransition.query.filter_by(solicitation_state_id_from=solicitation_state_id_from)
        if ssts_query.count() == 0:
            return None
        
        ssts = ssts_query.all()
        
        # returns if it is not to format
        if not format or not ssts:
            return ssts

        # format the ssts
        formatted_ssts = []
        for sst in ssts:
            formatted_sst = format_solicitation_state_transition(sst)
            formatted_sst["id"] = sst.id
            formatted_sst["transition_name"] = sst.transition_name
            formatted_sst["solicitation_state_id_from"] = sst.solicitation_state_id_from
            formatted_sst["solicitation_state_id_to"] = sst.solicitation_state_id_to

            formatted_ssts.append(formatted_sst)
        
        return formatted_ssts
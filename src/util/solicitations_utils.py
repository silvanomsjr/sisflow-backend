"""
Solicitations utils

Reusable pieces of code related to solicitations to avoid code duplication
"""

import json
import threading
import util
from datetime import datetime, timedelta
from repositories import (
    AttachmentRepository, SchedulingRepository, SchedulingsRepository, SolicitationRepository,
    SolicitationStateTransitionRepository, SolicitationStateTransitionsRepository, UserProfileTokenRepository
)

def is_solicitation_dynamic_page_components_valid(user_id, components, solicitation_user_data):

    for component in components:

        # Checks if required inputs are present
        if component["component_type"] == "input" and component["input_required"]:
            found = False

            for user_input in solicitation_user_data['inputs']:
                if user_input["input_name"] == component["input_name"]:
                    found = True
        
            if not found:
                return False, "Input da solicitação está faltando"

        # Checks if required uploads are valid
        if component["component_type"] == "upload" and component["upload_required"]:
            found = False

            for user_upload in solicitation_user_data["uploads"]:
                if user_upload["upload_name"] == component["upload_name"]:
                    if AttachmentRepository.read_attachment(user_upload["upload_hash_name"], user_id) != None:
                        found = True
                        break
              
            if not found:
                return False, "Anexo da solicitação está faltando"
            
        # incomplete: check if required select uploads are valid
        if component["component_type"] == "select_upload" and component["select_upload_required"]:
            pass

    return True, ""

# returns bool, message indicating if the user profile can edit the solicitation
def is_solicitation_profile_edition_allowed(user_data, student_token, advisor_token, s_state_data):

    # if not adm check if is student or advisor to edit the solicitation
    if not "ADM" in user_data["profile_acronyms"] and not "COO" in user_data["profile_acronyms"]:
        if user_data["user_id"] != student_token["user_id"] and user_data["user_id"] != advisor_token["user_id"]:
            return False, "Edição a solicitação não permitida, perfil não pertence a solicitação"
  
    # checks if profile is allowed to change solicitation
    profile_can_edit = False
    for profile_editor in s_state_data["state_profile_editor_acronyms"].split(','):
        if profile_editor in user_data["profile_acronyms"]:
            profile_can_edit = True

    if not profile_can_edit:
        return False, "Edição a solicitação não permitida, perfil inválido"
  
    # Valid
    return True, ""

# returns bool, message indicating if the solicitation can be edited
def is_solicitation_edition_allowed(s_state_data):

    # check if the actual changeable state is the requested state
    if s_state_data["actual_solicitation_state_id"] != s_state_data["state_id"]:
        return False, "Edição a solicitação não permitida, estado diferente do atual"

    # data validation
    if s_state_data["start_datetime"] and datetime.now() < s_state_data["start_datetime"]:
        return False, "Edição a solicitação não permitida, a etapa da solicitação não foi iniciada"
    if s_state_data["end_datetime"] and datetime.now() > s_state_data["end_datetime"]:
        return False, "Edição a solicitação não permitida, a etapa da solicitação foi expirada"
  
    # status validation
    if s_state_data["decision"] != "Em analise":
        return False, "Edição a solicitação não permitida, a solicitação já foi realizada"
  
    # Valid
    return True, ""

# parses the old user solicitation data by replacing old and adding new fields
def parse_new_old_solicitation_user_data(old_user_data, new_user_data):

    # parses solicitation data
    parsed_user_data = None
    if old_user_data:
        parsed_user_data = old_user_data
    else:
        parsed_user_data = {
            "inputs": {},
            "uploads": {},
            "select_uploads": {}
        }

    if new_user_data:
        for input in new_user_data["inputs"]:
            parsed_user_data["inputs"][input["input_name"]] = input
        for upload in new_user_data["uploads"]:
            parsed_user_data["uploads"][upload["upload_name"]] = upload
        for select_upload in new_user_data["select_uploads"]:
            parsed_user_data["select_uploads"][select_upload["select_upload_name"]] = select_upload
  
    parsed_user_data = json.dumps(parsed_user_data)
    return parsed_user_data

# Resolves solicitation change, made here to allow scheduler to call the function without circular import problems
def resolve_solicitation_state_change(uhss_data, transition, next_ss_data, parsed_user_data, student_token, advisor_token):
    
    # updates actual user state
    uhs = SolicitationRepository.update_user_solicitation_state(
        uhss_data["user_has_state_id"], transition["transition_decision"], transition["transition_reason"]
    )
    
    # remove old events from scheduler
    remove_scheduled_solicitations(uhss_data["user_has_state_id"])

    # if next state exists
    if transition["solicitation_state_id_to"]:
        next_state_created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_state_finish_date = None if not next_ss_data["state_max_duration_days"]\
            else (datetime.now() + timedelta(days=next_ss_data["state_max_duration_days"])).strftime("%Y-%m-%d %H:%M:%S")

        next_state_reason = ''
        send_profile_names = None
        if next_ss_data and next_ss_data["state_profile_editor_acronyms"]:
            if "STU" in next_ss_data["state_profile_editor_acronyms"]:
                send_profile_names = "aluno"
            if "ADV" in next_ss_data["state_profile_editor_acronyms"]:
                send_profile_names = "orientador" if not send_profile_names else send_profile_names + ", orientador"
            if "COO" in next_ss_data["state_profile_editor_acronyms"]:
                send_profile_names = "coordenação de estágios" if not send_profile_names else send_profile_names + ", coordenação de estágios"
            if "," in send_profile_names:
                lastIndex = send_profile_names.rfind(",")
                send_profile_names = send_profile_names[:lastIndex] + " e" + send_profile_names[lastIndex+1:]

            if send_profile_names == "coordenação de estágios":
                next_state_reason = "Aguardando a coordenação de estágios"
            else:
                next_state_reason = ("Aguardando o " + send_profile_names) if send_profile_names else None
        else:
            next_state_reason = "Finalizado"
        
        # inserts new user solicitation state
        user_has_next_ss = SolicitationRepository.create_user_solicitation_state(
            uhss_data["user_has_solicitation_id"], transition["solicitation_state_id_to"], 'Em analise',
            next_state_created_date, next_state_reason, next_state_finish_date
        )
        if not user_has_next_ss:
            return "Erro ao criar o novo estado da solicitação do usuário", 500

        next_ss_transitions = SolicitationStateTransitionsRepository.read_solicitation_state_transitions(transition["solicitation_state_id_to"])

        # updates user solicitation data and changes its actual state
        uhs = SolicitationRepository.update_user_solicitation(uhss_data["user_has_solicitation_id"], parsed_user_data, transition["solicitation_state_id_to"])
        if not uhs:
            return "Erro ao atualizar a solicitação do usuário", 500

        # sets new events in scheduler
        schedule_transitions(user_has_next_ss.id, next_ss_transitions)

    # if next state not exists
    else:
        # updates only user solicitation data
        uhs = SolicitationRepository.update_user_solicitation(uhss_data["user_has_solicitation_id"], parsed_user_data)
        if not uhs:
            return "Erro ao atualizar a solicitação do usuário", 500
    
    # send mails
    transition_mails = SolicitationStateTransitionRepository.read_solicitation_state_transition_mails(transition["id"])
    for mail in transition_mails:
      
        # parses mail subject and body
        parsed_subject = util.sysconf.sistem_str_parser(mail["mail_subject"], student_token, advisor_token)
        parsed_body = util.sysconf.sistem_str_parser(mail["mail_body_html"], student_token, advisor_token)

        # sends mail to profiles
        if mail["is_sent_to_student"]:
            util.syssmtpserver.add_email(student_token['institutional_email'], parsed_subject, parsed_body)
        if mail["is_sent_to_advisor"]:
            util.syssmtpserver.add_email(advisor_token['institutional_email'], parsed_subject, parsed_body)
        if mail["is_sent_to_coordinator"]:
            util.syssmtpserver.add_email(util.sysconf.coordinator_email, parsed_subject, parsed_body)

    return {}, 200

"""
Event scheduler with solicitations
"""
def schedule_transitions(user_has_state_id, state_transitions):

    # schedule each scheduled transition
    if state_transitions:
        for transition in state_transitions:
            if transition["type"] == "scheduled":

                send_date_time = (datetime.now() + timedelta(seconds=transition["transition_delay_seconds"]))
                send_datetime_formated = send_date_time.strftime("%Y-%m-%d %H:%M:%S")

                # insert scheduling
                scheduling = SchedulingRepository.create_scheduling("Solicitation State Transition", send_datetime_formated)
                if not scheduling:
                    return "Erro ao realizar o agendamento"

                # insert scheduling state transition
                scheduling_state_transition = SchedulingRepository.create_scheduling_state_transition(scheduling.id, transition["id"], user_has_state_id)
                if not scheduling_state_transition:
                    return "Erro ao realizar o agendamento da transição"

                # insert event to the scheduler
                util.sysscheduler.add_transition(scheduling.id, send_date_time, user_has_state_id, transition["id"], resolve_scheduled_solicitation)

                print(f"# Added transition {transition['id']} to event Scheduler!")

def remove_scheduled_solicitations(user_has_state_id):

    schedulings = SchedulingsRepository.read_schedulings(user_has_state_id)
    for sch in schedulings:
        util.sysscheduler.remove_event(sch.id)
        SchedulingRepository.update_scheduling(sch.id, "Canceled")

def resolve_scheduled_solicitation(event_id, user_has_state_id, transition_id):
    
    # read user ids from solicitation state
    state_user_ids = SolicitationRepository.read_solicitation_state_user_ids(user_has_state_id)

    if not state_user_ids:
        print(f"# EventScheduler thread {threading.get_ident()}: Error: Usuario não possui o estado da solicitação", 401)
        return

    # get student and advisor tokens to parse the strings from dynamic page components and e-mails
    student_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["student_id"])
    advisor_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["advisor_id"])

    # gets user solicitation and state data 
    formatted_uhss = SolicitationRepository.read_user_solicitation_state(user_has_state_id, convert_dates_to_str=False)
    if not formatted_uhss:
        print(f"# EventScheduler thread {threading.get_ident()}: Error: Estado do usuário não encontrado", 404)
        return "Estado do usuário não encontrado", 404

    # Verify solicitation args correcteness
    print(f"# EventScheduler thread {threading.get_ident()}: Validating data")
    is_allowed, error_msg = is_solicitation_edition_allowed(formatted_uhss)
    if not is_allowed:
        print(f"# EventScheduler thread {threading.get_ident()}: Error: {error_msg}", 401)
        return
    
    # gets sstate transitions and validade
    transitions = SolicitationStateTransitionsRepository.read_solicitation_state_transitions(formatted_uhss["state_id"])
    if not transitions or len(transitions) == 0:
        print(f"# EventScheduler thread {threading.get_ident()}: Error: Transições da solicitação inválidas", 500)
        return "", 500

    transition = None
    for ts in transitions:
        if ts["id"] == transition_id:
            transition = ts
            break

    if transition == None:
        print(f"# EventScheduler thread {threading.get_ident()}: Transição não encontrada para este estado", 404)
        return
    
    # gets next sstate data
    next_ss_data = SolicitationRepository.read_solicitation_state(transition["solicitation_state_id_to"])\
        if transition["solicitation_state_id_to"] else None

    # get parsed solicitation user data using old and new data
    parsed_user_Data = parse_new_old_solicitation_user_data(formatted_uhss["solicitation_user_data"], None)

    # resolve solicitation change
    response, status = resolve_solicitation_state_change(formatted_uhss, transition, next_ss_data, parsed_user_Data, student_token, advisor_token)

    # check for errors
    if status != 200:
        print(f"# EventScheduler thread {threading.get_ident()}: Scheduled solicitation resolve error: {response}")
        return
    else:
        # sends the event to finish it
        SchedulingRepository.update_scheduling(event_id, "Sended")
        print(f"# EventScheduler thread {threading.get_ident()}: Done without errors")
    
    return
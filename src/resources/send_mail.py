"""
Define the REST HTTP verbs for sending mails
"""

from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
from repositories import SolicitationRepository, UserProfileTokenRepository
from util import parse_params_with_user_authentication, sysconf, syssmtpserver

logging = logging.getLogger(__name__)

class SendMailResource(Resource):
    """ HTTP methods relative to sending mails """

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("user_has_state_id", location="json", type=int, required=True, help="Required. Id of the user has state used to parse the message."),
        Argument("mail_subject", location="json", type=str, required=True, help="Required. Mail subject."),
        Argument("mail_body", location="json", type=str, required=True, help="Required. Mail body."),
        Argument("is_sent_to_student", location="json", type=bool, help="If the mail is sent to student."),
        Argument("is_sent_to_advisor", location="json", type=bool, help="If the mail is sent to advisor."),
        Argument("is_sent_to_coordinator", location="json", type=bool, help="If the mail is sent to coordinator."),
    ])
    def post(jwt_data, user_has_state_id, mail_subject, mail_body, is_sent_to_student=False, is_sent_to_advisor=False, is_sent_to_coordinator=False):
        """ Post to send a mail """

        # read user ids from solicitation state
        state_user_ids = SolicitationRepository.read_solicitation_state_user_ids(user_has_state_id)
        
        # read student and advisor tokens to parse the strings in the mail message
        student_token = None
        advisor_token = None

        if not state_user_ids:
            return "Estado do usuário não encontrado", 404

        student_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["student_id"])
        advisor_token = UserProfileTokenRepository.read_user_profile_token(state_user_ids["advisor_id"])

        # parses the subject and the body
        parsed_subject = sysconf.sistem_str_parser(mail_subject, student_token, advisor_token)
        parsed_body = sysconf.sistem_str_parser(mail_body, student_token, advisor_token)

        # sends the e-mail messages
        if is_sent_to_student:
            syssmtpserver.add_email(student_token["institutional_email"], parsed_subject, parsed_body)
        if is_sent_to_advisor:
            syssmtpserver.add_email(advisor_token["institutional_email"], parsed_subject, parsed_body)
        if is_sent_to_coordinator:
            syssmtpserver.add_email(sysconf.coordinator_email, parsed_subject, parsed_body)
        
        return {}, 200
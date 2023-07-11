from flask import abort
from flask_restful import Resource, reqparse
import traceback

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.sistemConfig import getCoordinatorEmail
from utils.smtpMails import addToSmtpMailServer
from utils.utils import sistemStrParser

# Send mail with post
class SendMail(Resource):

  def post(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("user_has_state_id", location="json", type=int, required=True)
    args.add_argument("mail_subject", location="json", type=str, required=True)
    args.add_argument("mail_body", location="json", type=str, required=True)
    args.add_argument("is_sent_to_student", location="json", type=bool)
    args.add_argument("is_sent_to_advisor", location="json", type=bool)
    args.add_argument("is_sent_to_coordinator", location="json", type=bool)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting send Email\n# Reading data from DB")

    qUserRes = None
    try:
      # student and advisor data
      qUserRes = dbGetSingle(
        " SELECT uc_stu.id AS student_id, uc_stu.user_name AS student_name, uc_stu.institutional_email AS student_institutional_email, "
        " uc_stu.secondary_email AS student_secondary_email, uc_stu.gender AS student_gender, "
        " uc_stu.phone AS student_phone, uc_stu.creation_datetime AS student_creation_datetime, "
        " uhpsd.matricula AS student_matricula, uhpsd.course AS student_course, "

        " uc_adv.id AS advisor_id, uc_adv.user_name AS advisor_name, uc_adv.institutional_email AS advisor_institutional_email, "
        " uc_adv.secondary_email AS advisor_secondary_email, uc_adv.gender AS advisor_gender, uc_adv.phone AS advisor_phone, "
        " uc_adv.creation_datetime AS advisor_creation_datetime, uhpad.siape AS advisor_siape, 3 AS advisor_students, "

        " uhs.id AS user_has_solicitation_id, uhs.solicitation_id, uhs.actual_solicitation_state_id, uhs.solicitation_user_data, "
        " uhss.solicitation_state_id, uhss.decision, uhss.start_datetime, uhss.end_datetime, "
        " sspe.profile_acronyms, "
        " dp.id AS page_id "
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_state AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation_state AS ss ON uhss.solicitation_state_id = ss.id "
        "     LEFT JOIN dynamic_page AS dp ON ss.state_dynamic_page_id = dp.id "
        "     LEFT JOIN user_has_profile_advisor_data AS uhpad ON uhs.advisor_siape = uhpad.siape "
        "     LEFT JOIN user_has_profile AS uhp_adv ON uhpad.user_has_profile_id = uhp_adv.id "
        "     LEFT JOIN user_account AS uc_adv ON uhp_adv.user_id = uc_adv.id "
        "     LEFT JOIN ( "
        "       SELECT sspe.solicitation_state_id, "
        "         GROUP_CONCAT(sspe.state_profile_editor) AS state_profile_editors, "
        "         GROUP_CONCAT(p.profile_acronym) AS profile_acronyms "
        "           FROM solicitation_state_profile_editors sspe "
        "           JOIN profile p ON sspe.state_profile_editor = p.id "
        "           GROUP BY sspe.solicitation_state_id) sspe ON ss.id = sspe.solicitation_state_id "
        "   WHERE uhss.id = %s; ", (args["user_has_state_id"],)
      )
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      traceback.print_exc()
      return "Erro na base de dados", 409

    # Data used by parser
    studentData={
      "user_id": qUserRes["student_id"],
      "institutional_email": qUserRes["student_institutional_email"],
      "user_name": qUserRes["student_name"],
      "gender": qUserRes["student_gender"],
      "profiles": [{
        "profile_acronym":"STU",
        "matricula": qUserRes["student_matricula"],
        "course": qUserRes["student_course"]
      }]
    }
    advisorData={
      "user_id": qUserRes["advisor_id"],
      "institutional_email": qUserRes["advisor_institutional_email"],
      "user_name": qUserRes["advisor_name"],
      "gender": qUserRes["advisor_gender"],
      "profiles": [{
        "profile_acronym":"ADV",
        "siape": qUserRes["advisor_siape"]
      }]
    }

    print("# Sending Mail")
    
    # parse mail subject and body
    parsedSubject = sistemStrParser(args["mail_subject"], studentData, advisorData)
    parsedBody = sistemStrParser(args["mail_body"], studentData, advisorData)

    if args.get("is_sent_to_student") == True:
      addToSmtpMailServer(studentData['institutional_email'], parsedSubject, parsedBody)

    if args.get("is_sent_to_advisor") == True:
      addToSmtpMailServer(advisorData['institutional_email'], parsedSubject, parsedBody)

    if args.get("is_sent_to_coordinator") == True:
      addToSmtpMailServer(getCoordinatorEmail(), parsedSubject, parsedBody)

    print("# Sending Mail done!")

    return {}, 200
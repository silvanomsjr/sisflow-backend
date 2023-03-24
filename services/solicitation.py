from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json
import datetime

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.smtpMails import smtpSend
from utils.sistemConfig import getCoordinatorEmail
from utils.utils import getFormatedMySQLJSON, sistemStrParser

# Data from single solicitation
class Solicitation(Resource):

  # get single solicitation and associated dynamic page data
  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs.add_argument("user_has_step_id", location="args", type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    userHasStepId = solicitationsArgs["user_has_step_id"]

    print("\n# Starting get single solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT uhs.user_id, uc_pro.id AS professor_id "
        "   FROM user_has_solicitation_step AS uhss "
        "     JOIN user_has_solicitation AS uhs ON uhss.user_has_solicitation_id = uhs.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "   WHERE uhss.id = %s; ",
        [(userHasStepId)])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if not queryRes:
      abort(401, "Usuario não possui a etapa de solicitação!")

    studentId = queryRes[0]
    professorId = queryRes[1]

    if not "ADM" in tokenData["profile_acronyms"] and not "COO" in tokenData["profile_acronyms"]:
      if tokenData["user_id"] != studentId and tokenData["user_id"] != professorId:
        abort(401, "Acesso a solicitação não permitido!")

    try:
      queryRes = dbGetSingle(
        " SELECT uc_stu.user_name, uc_stu.institutional_email, uc_stu.secondary_email, uc_stu.gender, "
        " uc_stu.phone, uc_stu.creation_datetime, uhpsd.matricula, uhpsd.course, "

        " uc_pro.user_name, uc_pro.institutional_email, uc_pro.secondary_email, uc_pro.gender, "
        " uc_pro.phone, uc_pro.creation_datetime, uhppd.siape, "

        " s.solicitation_name, "
        " ssprof.profile_acronym, ss.step_order_in_solicitation, ss.step_description, ss.step_max_duration_days, "
        " uhs.actual_solicitation_step_order, uhs.solicitation_user_data, "
        " uhss.decision, uhss.reason, uhss.start_datetime, uhss.end_datetime, "

        " ssp.use_dynamic_page, ssp.static_page_name, "
        " dp.title, dp.top_inner_html, dp.mid_inner_html, dp.bot_inner_html, dp.inputs, dp.downloads, "
        " dp.uploads, dp.select_uploads, dp.is_solicitation_button_active "
        
        "   FROM user_account AS uc_stu "
        "     JOIN user_has_profile AS uhp_stu ON uc_stu.id = uhp_stu.user_id "
        "     JOIN user_has_profile_student_data AS uhpsd ON uhp_stu.id = uhpsd.user_has_profile_id "
        "     JOIN user_has_solicitation AS uhs ON uc_stu.id = uhs.user_id "
        "     JOIN user_has_solicitation_step AS uhss ON uhs.id = uhss.user_has_solicitation_id "
        "     JOIN solicitation AS s ON uhs.solicitation_id = s.id "
        "     JOIN solicitation_step AS ss ON s.id = ss.solicitation_id "
        "     JOIN profile AS ssprof ON ss.step_profile_editor = ssprof.id "
        "     JOIN solicitation_step_page AS ssp ON ss.id = ssp.solicitation_step_id "
        "     LEFT JOIN dynamic_page AS dp ON ssp.dynamic_page_id = dp.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "   WHERE uc_stu.id = %s AND uhss.id = %s; ",
        [studentId, userHasStepId])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    if not queryRes:
      abort(401, "Usuario não possui a etapa de solicitação!")

    print("# Operation Done!")
    print(tokenData)

    # Refactor this in future
    studentParserToken={
      "user_name": queryRes[0],
      "gender": queryRes[3],
      "profiles": [{
        "profile_acronym":"STU",
        "matricula": queryRes[6],
        "course": queryRes[7]
      }]
    }

    return {
      "student": {
        "user_name": queryRes[0],
        "institutional_email": queryRes[1],
        "secondary_email": queryRes[2],
        "gender": queryRes[3],
        "phone": queryRes[4],
        "creation_datetime": str(queryRes[5]),
        "matricula": queryRes[6],
        "course": queryRes[7]
      },
      "professor": {
        "user_name": queryRes[8],
        "institutional_email": queryRes[9],
        "secondary_email": queryRes[10],
        "gender": queryRes[11],
        "phone": queryRes[12],
        "creation_datetime": str(queryRes[13]),
        "siape": queryRes[14]
      },
      "solicitation":{
        "solicitation_name": queryRes[15],
        "step_profile_editor_acronym": queryRes[16],
        "step_order_in_solicitation": queryRes[17],
        "step_description": queryRes[18],
        "step_max_duration_days": queryRes[19],
        "actual_solicitation_step_order": queryRes[20],
        "solicitation_user_data": getFormatedMySQLJSON(queryRes[21]),
        "decision": queryRes[22],
        "reason": queryRes[23],
        "start_datetime": str(queryRes[24]),
        "end_datetime": str(queryRes[25]),
        "page": {
          "use_dynamic_page": queryRes[26],
          "static_page_name": queryRes[27],
          "title": sistemStrParser(queryRes[28], studentParserToken),
          "top_inner_html": sistemStrParser(queryRes[29], studentParserToken),
          "mid_inner_html": sistemStrParser(queryRes[30], studentParserToken),
          "bot_inner_html": sistemStrParser(queryRes[31], studentParserToken),
          "inputs": getFormatedMySQLJSON(queryRes[32]),
          "downloads": getFormatedMySQLJSON(queryRes[33]),
          "uploads": getFormatedMySQLJSON(queryRes[34]),
          "select_uploads": getFormatedMySQLJSON(queryRes[35]),
          "is_solicitation_button_active": queryRes[36]
        }
      },
    }, 200
  
  # put to create solicitations - works only for students
  def put(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    solicitationsArgs.add_argument("solicitation_id", location="json", type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ["STU"])
    if not isTokenValid:
      abort(401, errorMsg)

    solicitationId = solicitationsArgs["solicitation_id"]
    userId = tokenData["user_id"]

    print("\n# Starting put Single Solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")
    
    stepId = None
    stepMaxDurationDays = None
    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT ss.id, ss.step_max_duration_days "
        "   FROM solicitation AS s JOIN solicitation_step AS ss ON s.id = ss.solicitation_id "
        "   WHERE s.id = %s AND step_order_in_solicitation = 1; ",
        [(solicitationId)])

      if not queryRes:
        raise Exception("No step with code 1 return for solicitation with id " + str(solicitationId))
      
      stepId = queryRes[0]
      stepMaxDurationDays = queryRes[1]

      queryRes = dbGetSingle(
        " SELECT s.id	FROM user_account AS us "
	      "   JOIN user_has_solicitation AS uhs ON us.id = uhs.user_id "
	      "   JOIN solicitation AS s ON uhs.solicitation_id = s.id "
	      "   WHERE s.id = %s AND us.id = %s; ",
        [solicitationId, userId])

    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if queryRes:
      abort(401, "Você já possui essa solicitação!")
    
    # set created date and finish date based on max day interval from solicitation step
    createdDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    finishDate = None if not stepMaxDurationDays else (datetime.datetime.now() + datetime.timedelta(days=stepMaxDurationDays)).strftime("%Y-%m-%d %H:%M:%S")

    userHasSolId = None
    userHasSolStepId = None
    try:
      # insert user solicitation
      dbExecute(
        " INSERT INTO user_has_solicitation "
        " (user_id, professor_siape, solicitation_id, actual_solicitation_step_order, solicitation_user_data) VALUES "
        "   (%s, \"SIAPERENATO\", %s, 1, NULL); ",
        [userId, solicitationId], False)

      # select added user solicitation id
      queryRes = dbGetSingle(
        " SELECT uhs.id "
        "   FROM user_has_solicitation AS uhs "
        "   WHERE uhs.user_id = %s AND solicitation_id = %s; ",
        [userId, solicitationId], False)
      
      if not queryRes:
        raise Exception("No return for user_has_solicitation insertion ")

      userHasSolId = queryRes[0]

      # insert user solicitation step
      dbExecute(
        " INSERT INTO user_has_solicitation_step "
        " (user_has_solicitation_id, solicitation_step_id, decision, reason, start_datetime, end_datetime) VALUES "
        "   (%s, %s, \"Em analise\", \"Aguardando o envio de dados pelo aluno\", %s, %s); ",
        [userHasSolId, stepId, createdDate, finishDate], False)

      # select added user solicitation step id
      queryRes = dbGetSingle(
        " SELECT uhss.id "
        "   FROM user_has_solicitation_step AS uhss "
        "   WHERE uhss.user_has_solicitation_id = %s AND uhss.solicitation_step_id = %s; ",
        [userHasSolId, stepId], False)

      if not queryRes:
        raise Exception("No return for user_has_solicitation_step insertion ")
      
      userHasSolStepId = queryRes[0]
      
    except Exception as e:
      dbRollback()
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    dbCommit()
    print("# Operation done!")
    return { "user_has_solicitation_id": userHasSolId, "user_has_step_id": userHasSolStepId }, 200
      
  # post to resolve solicitations
  def post(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs.add_argument('user_has_step_id', location='json', type=int, required=True)
    solicitationsArgs.add_argument('decision', location='json', type=int, required=True)
    solicitationsArgs.add_argument('reason', location='json', required=True)
    solicitationsArgs.add_argument('solicitation_user_data', location='json', required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    userHasStepId = solicitationsArgs['user_has_step_id']
    decision = solicitationsArgs['decision']
    reason = solicitationsArgs['reason']
    solicitationUserData = solicitationsArgs['solicitation_user_data']

    if solicitationUserData:
      solicitationUserData = json.loads(
        solicitationUserData.replace("\'", "\"") if isinstance(solicitationUserData, str) else solicitationUserData.decode('utf-8'))
    
    print("\n# Starting post to resolve solicitation for " + tokenData["institutional_email"] + "\n# Reading data from DB")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT uhs.user_id AS student_id, uc_pro.id AS professor_id, "
        " uhs.solicitation_id, uhs.actual_solicitation_step_order, uhs.solicitation_user_data, "
        " uhss.solicitation_step_id, uhss.start_datetime, uhss.end_datetime, "
        " ss.step_order_in_solicitation, ssprof.profile_acronym, "
        " dp.inputs, dp.uploads, dp.select_uploads "
        "   FROM user_has_solicitation_step AS uhss "
        "     JOIN user_has_solicitation AS uhs ON uhss.user_has_solicitation_id = uhs.id "
        "     JOIN solicitation_step AS ss ON uhss.solicitation_step_id = ss.id "
        "     JOIN profile AS ssprof ON ss.step_profile_editor = ssprof.id "
        "     JOIN solicitation_step_page AS ssp ON ss.id = ssp.solicitation_step_id "
        "     LEFT JOIN dynamic_page AS dp ON ssp.dynamic_page_id = dp.id "
        "     LEFT JOIN user_has_profile_professor_data AS uhppd ON uhs.professor_siape = uhppd.siape "
        "     LEFT JOIN user_has_profile AS uhp_pro ON uhppd.user_has_profile_id = uhp_pro.id "
        "     LEFT JOIN user_account AS uc_pro ON uhp_pro.user_id = uc_pro.id "
        "   WHERE uhss.id = %s; ",
        [(userHasStepId)])
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409

    if not queryRes:
      abort(401, "Usuario não possui a etapa de solicitação!")
    
    studentId = queryRes[0]
    professorId = queryRes[1]
    solicitationId = queryRes[2]
    actualStepOrder = queryRes[3]
    oldSolicitationUserData = getFormatedMySQLJSON(queryRes[4])
    stepId = queryRes[5]
    stepStartDatetime = queryRes[6]
    stepEndDatetime = queryRes[7]
    stepOrder = queryRes[8]
    stepProfileAcronymEditor = queryRes[9]
    pageInputs = getFormatedMySQLJSON(queryRes[10])
    pageUploads = getFormatedMySQLJSON(queryRes[11])
    pageSelectUploads = getFormatedMySQLJSON(queryRes[12])

    # Verify solicitation args correcteness
    print('# Validating data')

    # user acess
    if not "ADM" in tokenData["profile_acronyms"] and not "COO" in tokenData["profile_acronyms"]:
      if tokenData["user_id"] != studentId and tokenData["user_id"] != professorId:
        abort(401, "Edição a solicitação não permitida!")

    if not stepProfileAcronymEditor in tokenData["profile_acronyms"]:
      abort(401, "Perfil editor a solicitação inválido!")
      
    if actualStepOrder!=stepOrder:
      abort(401, "Solicitação está fora de ordem!")

    # data validation
    if stepStartDatetime and datetime.datetime.now() < stepStartDatetime:
      abort(401, 'Esta etapa da solicitação não foi iniciada!')

    if stepEndDatetime and datetime.datetime.now() > stepEndDatetime:
      abort(401, 'Esta etapa da solicitação foi expirada!')
    
    # Checks if all required inputs are valid
    if pageInputs and pageInputs[0]:
      
      for pInp in pageInputs:
        if pInp['required']:
          found = False

          for solInp in solicitationUserData['inputs']:
            if solInp['label_txt'] == pInp['label_txt']:
              found = True
          
          if not found:
            abort(401, 'Input da solicitação está faltando!')

    # Checks if all required attachments are valid
    if pageUploads and pageUploads[0]:

      for pUpl in pageUploads:
        if pUpl['required']:
          found = False

          for solAtt in solicitationUserData['attachments']:
            if solAtt['file_abs_type'] == pUpl['file_abs_type']:
              try:
                if dbGetSingle(
                    ' SELECT an.hash_anexo ' \
                    '   FROM anexo AS an JOIN possui_anexo AS pan ON an.id = pan.id_anexo ' \
                    '   WHERE pan.id_usuario = %s AND an.hash_anexo = %s; ',
                    [userId, solAtt['name']]):
                  found = True
                  break
              except Exception as e:
                print('# Database reading error:')
                print(str(e))
                return 'Erro na base de dados', 409
              
          if not found:
            abort(401, 'Anexo da solicitação está faltando!')
    
    # Checks if all required select attachments are valid - incomplete
    if dinamicPageSelectFileAttachments and dinamicPageSelectFileAttachments[0]:
      pass

    profilePos = -1 if not solicitationProfileSeq else solicitationProfileSeq.find(solicitationActualProfile)

    # If another profile in step
    if profilePos != -1 and len(solicitationProfileSeq) > profilePos+1:

      nextProfile = solicitationProfileSeq[profilePos+1]
      decision = 'Em analise'
      reason = 'Aguardando o ' + ('professor orientador' if nextProfile == 'P' else 'coordenador de estágios')
      solicitationStepData = json.dumps(solicitationData)
      try:
        # updates actual step and its profile
        dbExecute(
          ' UPDATE possui_etapa_solicitacao ' \
          '   SET perfil_editor_atual = %s, decisao = %s, motivo = %s, json_dados = %s ' \
          '   WHERE id_usuario = %s AND id_etapa_solicitacao = %s; ',
          [nextProfile, decision, reason, solicitationStepData, userId, solicitationStepId],
          False)
      except Exception as e:
        dbRollback()
        print('# Database reading error:')
        print(str(e))
        return 'Erro na base de dados', 409

    # If another step
    else:
      try:
        queryRes = dbGetSingle(
          ' SELECT es.id, duracao_maxima_dias ' \
          '   FROM etapa_solicitacao AS es ' \
          '     INNER JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
          '     WHERE s.id = %s AND es.ordem_etapa_solicitacao = %s; ',
          [solicitationId, solicitationStepOrder+1])
      except Exception as e:
        print('# Database reading error:')
        print(str(e))
        return 'Erro na base de dados', 409
    
      nextStepId = None if not queryRes else queryRes[0]
      nextStepMaxDays = None if not queryRes else queryRes[1]

      # Later must be chosen by coordinator
      decision = 'Deferido'
      reason = 'Deferido pela coordenação de estágios'
      solicitationStepData = json.dumps(solicitationData)

      print('# Updating and Inserting data in db')

      try:
        # updates actual step
        dbExecute(
          ' UPDATE possui_etapa_solicitacao ' \
          '   SET decisao = %s, motivo = %s, json_dados = %s ' \
          '   WHERE id_usuario = %s AND id_etapa_solicitacao = %s; ',
          [decision, reason, solicitationStepData, userId, solicitationStepId],
          False)
        
        # inserts new step if exists
        if nextStepId:
          nextStepCreatedDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          nextStepFinishDate = None if not nextStepMaxDays else (datetime.datetime.now() + datetime.timedelta(days=nextStepMaxDays)).strftime('%Y-%m-%d %H:%M:%S')

          dbExecute(
            ' INSERT INTO possui_etapa_solicitacao ' \
            ' (id_usuario, siape_orientador, id_etapa_solicitacao, perfil_editor_atual, decisao, motivo, data_hora_inicio, data_hora_fim) VALUES ' \
            '   (%s, "SIAPERENATO", %s, \'S\', "Em analise", "Aguardando o envio de dados pelo aluno", %s, %s); ',
            [userId, nextStepId, nextStepCreatedDate, nextStepFinishDate],
            False)
          
      except Exception as e:
        dbRollback()
        print('# Database reading error:')
        print(str(e))
        return 'Erro na base de dados', 409

      dbCommit()
      print('# DB operations done')

    # mail messages - need to update to consider profile sending
    try:
      queryRes = dbGetAll(
        ' SELECT md.msg_assunto, md.msg_html, md.enviar_aluno, md.enviar_professor, md.enviar_coordenador ' \
        '   FROM etapa_solicitacao AS es ' \
        '     INNER JOIN etapa_solicitacao_mensagem AS esm ON es.id = esm.id_etapa_solicitacao ' \
        '     INNER JOIN mensagem_dinamica AS md ON esm.id_mensagem_dinamica = md.id ' \
        '     WHERE es.id = %s; ',
        [(solicitationStepId)])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    if queryRes:

      mailList = []
      for r in queryRes:
        mailList.append({
          'subject': r[0],
          'msgHtml': sistemStrParser(r[1], tokenData),
          'sendToStudent': r[2],
          'sendToTeacher': r[3],
          'sendToCoordinator': r[4]
        })

      print('# Sending mails')

      for mail in mailList:

        if mail['sendToStudent']:
          smtpSend(tokenData['email_ins'], mail['subject'], mail['msgHtml'])
          
        if mail['sendToTeacher']:
          smtpSend('professor@ufu.br', mail['subject'], mail['msgHtml'])

        if mail['sendToCoordinator']:
          smtpSend(getCoordinatorEmail(), mail['subject'], mail['msgHtml'])
      
      print('# Operation done!')

    return {}, 200
from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json
import datetime

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.smtpMails import smtpSend
from utils.sistemConfig import getCoordinatorMail
from utils.utils import getFormatedMySQLJSON, sistemStrParser

# Data from single solicitation
class Solicitation(Resource):

  # get single solicitation and associated dynamic page data
  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs.add_argument('student_id', location='args', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_id', location='args', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_step_order', location='args', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_profile', location='args', type=str, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)
    
    studentId = solicitationsArgs['student_id']
    solicitationId = solicitationsArgs['solicitation_id']
    solicitationStepOrder = solicitationsArgs['solicitation_step_order']
    solicitationProfile = solicitationsArgs['solicitation_profile']

    if not 'A' in tokenData['perfis'] and not 'C' in tokenData['perfis']:
      if solicitationProfile == 'C' or solicitationProfile == 'A':
        abort(401, 'Acesso a solicitação não permitido!')
      if solicitationProfile == 'P' and 'S' in tokenData['perfis']:
        abort(401, 'Acesso a solicitação não permitido!')

    print('\n# Starting get single solicitation for ' + tokenData['email_ins'] + '\n# Reading data from DB')
    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT s.nome AS nome_solicitacao, pes.decisao, pes.motivo, pes.data_hora_inicio, pes.data_hora_fim, ' \
        ' pes.json_dados AS dados_etapa_solicitacao, es.ordem_etapa_solicitacao, es.sequencia_perfis_editores, es.descricao, ' \
        ' es.duracao_maxima_dias, esp.nome_pagina_estatica, pes.perfil_editor_atual, esp.perfil_editor_pagina, pd.titulo, pd.top_inner_html, ' \
        ' pd.mid_inner_html, pd.bot_inner_html, pd.inputs, pd.downloads, pd.uploads, pd.select_uploads, pd.botao_solicitar ' \
        '   FROM conta_usuario AS us ' \
        '     INNER JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     INNER JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id ' \
        '     INNER JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
			  '     INNER JOIN etapa_solicitacao_pagina AS esp ON es.id = esp.id_etapa_solicitacao ' \
        '     LEFT JOIN pagina_dinamica AS pd ON esp.id_pagina_dinamica = pd.id ' \
        '     WHERE us.id=%s AND s.id=%s AND es.ordem_etapa_solicitacao=%s AND esp.perfil_editor_pagina=%s; ',
        [studentId, solicitationId, solicitationStepOrder, solicitationProfile])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    if not queryRes:
      abort(401, 'Usuario não possui a etapa de solicitação!')

    print('# Operation Done!')

    # resolve this line
    tokenData['perfil_aluno'] = {'curso':'BCC'}
    return {
      'etapa_solicitacao': {
        'nome_solicitacao': queryRes[0],
        'decisao': queryRes[1],
        'motivo': queryRes[2],
        'data_hora_inicio': str(queryRes[3]),
        'data_hora_fim': str(queryRes[4]),
        'dados_etapa_solicitacao': getFormatedMySQLJSON(queryRes[5]),
        'ordem_etapa_solicitacao': queryRes[6],
        'sequencia_perfis_editores': queryRes[7],
        'descricao': queryRes[8],
        'duracao_maxima_dias': queryRes[9],
        'nome_pagina_estatica': queryRes[10],
        'perfil_editor_atual': queryRes[11],
        'perfil_editor_pagina': queryRes[12]
      },
      'pagina_dinamica': {
        'titulo': sistemStrParser(queryRes[13], tokenData),
        'top_inner_html': sistemStrParser(queryRes[14], tokenData),
        'mid_inner_html': sistemStrParser(queryRes[15], tokenData),
        'bot_inner_html': sistemStrParser(queryRes[16], tokenData),
        'inputs': getFormatedMySQLJSON(queryRes[17]),
        'downloads': getFormatedMySQLJSON(queryRes[18]),
        'uploads': getFormatedMySQLJSON(queryRes[19]),
        'select_uploads' : getFormatedMySQLJSON(queryRes[20]),
        'botao_solicitar': queryRes[21]
      }
    }, 200
  
  # put to create solicitations - works only for students
  def put(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs.add_argument('id_solicitacao', type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    solicitationId = solicitationsArgs['id_solicitacao']

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ['S'])
    if not isTokenValid:
      abort(401, errorMsg)

    print('\n# Starting put Single Solicitation for ' + tokenData['email_ins'])
    
    queryRes = None
    userId = None
    try:
      print('# Reading data from DB')
      queryRes = dbGetSingle(
        ' SELECT id ' \
        '   FROM conta_usuario ' \
        '   WHERE email_ins = %s; ',
        [(tokenData['email_ins'])])

      if not queryRes:
        raise Exception('No userId return for user with ' + str(tokenData['email_ins']))
      
      userId = queryRes[0]

      queryRes = dbGetSingle(
        ' SELECT es.id, duracao_maxima_dias ' \
        '   FROM solicitacao AS s JOIN etapa_solicitacao AS es ON s.id = es.id_solicitacao ' \
        '   WHERE s.id = %s AND ordem_etapa_solicitacao = 1; ',
        [(solicitationId)])

      if not queryRes:
        raise Exception('No step with code 1 return for solicitation with ' + str(tokenData['email_ins']))
      
      solicitationStepId = queryRes[0]
      maxDurationDays = queryRes[1]

      print('# Parsing data')
      queryRes = dbGetSingle(
        ' SELECT s.id	FROM conta_usuario AS us ' \
	      '   JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
	      '   JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id ' \
	      '   JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
	      '   WHERE s.id = %s AND us.id = %s; ',
        [solicitationId, userId])

    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if queryRes:
      abort(401, 'Você já possui essa solicitação!')
    
    # set created date and finish date based on max day interval from solicitation step
    createdDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    finishDate = None if not maxDurationDays else (datetime.datetime.now() + datetime.timedelta(days=maxDurationDays)).strftime('%Y-%m-%d %H:%M:%S')

    try:
      dbExecute(
        ' INSERT INTO possui_etapa_solicitacao ' \
        ' (id_usuario, siape_orientador, id_etapa_solicitacao, perfil_editor_atual, decisao, motivo, data_hora_inicio, data_hora_fim) VALUES ' \
        '   (%s, "SIAPERENATO", %s, "S", "Em analise", "Aguardando o envio de dados pelo aluno", %s, %s); ',
        [userId, solicitationStepId, createdDate, finishDate])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Operation done!')
    return 'ok', 200
      
  # post to resolve solicitations
  def post(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs.add_argument('student_id', location='json', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_id', location='json', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_step_order', location='json', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_data', location='json', required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    studentId = solicitationsArgs['student_id']
    solicitationId = solicitationsArgs['solicitation_id']
    solicitationStepOrder = solicitationsArgs['solicitation_step_order']
    solicitationData = solicitationsArgs['solicitation_data']

    if solicitationData:
      solicitationData = json.loads(
        solicitationData.replace("\'", "\"") if isinstance(solicitationData, str) else solicitationData.decode('utf-8'))

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    print('\n# Starting post to resolve solicitation for ' + tokenData['email_ins'], solicitationId, solicitationStepOrder, solicitationData )

    print('# Reading data from DB')
    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT us.id, es.id, es.sequencia_perfis_editores, pes.perfil_editor_atual, pes.decisao, pes.data_hora_fim, pes.json_dados, pd.inputs, pd.uploads, pd.select_uploads ' \
        '   FROM conta_usuario AS us ' \
        '     INNER JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     INNER JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id ' \
        '     INNER JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
			  '     LEFT JOIN etapa_solicitacao_pagina AS esp ON es.id = esp.id_etapa_solicitacao ' \
        '     LEFT JOIN pagina_dinamica AS pd ON esp.id_pagina_dinamica = pd.id ' \
        '     WHERE us.id = %s AND s.id = %s AND es.ordem_etapa_solicitacao = %s; ',
        [studentId, solicitationId, solicitationStepOrder])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    if not queryRes:
      abort(401, 'Usuario não possui a etapa de solicitação!')
    
    print('# Validating data')

    userId = queryRes[0]
    solicitationStepId = queryRes[1]
    solicitationProfileSeq = queryRes[2]
    solicitationActualProfile = queryRes[3]
    decision = queryRes[4]
    solicitationStepEndDateTime = queryRes[5]
    solicitationStepData = getFormatedMySQLJSON(queryRes[6])
    dinamicPageInputs = getFormatedMySQLJSON(queryRes[7])
    dinamicPageFileAttachments = getFormatedMySQLJSON(queryRes[8])
    dinamicPageSelectFileAttachments = getFormatedMySQLJSON(queryRes[9])

    if decision != 'Em analise':
      abort(401, 'Esta solicitação está com status ' + str(decision) + '!')
    #if solicitationStepData:
    #  abort(401, 'Esta etapa da solicitação já foi realizada aguarde sua conclusão!')
    if solicitationStepEndDateTime and datetime.datetime.now() > solicitationStepEndDateTime:
      abort(401, 'Esta etapa da solicitação foi expirada!')
    
    # Checks if all required inputs are valid
    if dinamicPageInputs and dinamicPageInputs[0]:
      
      for dpInp in dinamicPageInputs:
        if dpInp['required']:
          found = False

          for solInp in solicitationData['inputs']:
            if solInp['label_txt'] == dpInp['label_txt']:
              found = True
          
          if not found:
            abort(401, 'Input da solicitação está faltando!')

    # Checks if all required attachments are valid
    if dinamicPageFileAttachments and dinamicPageFileAttachments[0]:

      for dpAtt in dinamicPageFileAttachments:
        if dpAtt['required']:
          found = False

          for solAtt in solicitationData['attachments']:
            if solAtt['file_abs_type'] == dpAtt['file_abs_type']:
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
          smtpSend(getCoordinatorMail(), mail['subject'], mail['msgHtml'])
      
      print('# Operation done!')

    return {}, 200
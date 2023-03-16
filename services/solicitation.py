from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json
import datetime

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.smtpMails import smtpSend
from utils.sistemConfig import getCoordinatorMail, sistemStrParser

# Data from single solicitation
class Solicitation(Resource):

  # get single solicitation and associated dynamic page data
  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs.add_argument('solicitation', location='args', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_step_order', location='args', type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    solicitationId = solicitationsArgs['solicitation']
    solicitationStepOrder = solicitationsArgs['solicitation_step_order']

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    print(tokenData)
    print('\n# Starting get single solicitation for ' + tokenData['email_ins'])

    print('# Reading data from DB')
    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT s.nome AS nome_solicitacao, pes.decisao, pes.motivo, pes.data_hora_inicio, pes.data_hora_fim, ' \
        ' pes.json_dados AS dados_etapa_solicitacao, es.ordem_etapa_solicitacao, es.descricao, es.duracao_maxima_dias, ' \
        ' esp.nome_pagina_estatica, pd.titulo, pd.perfis_permitidos, pd.top_inner_html, pd.mid_inner_html, pd.bot_inner_html, ' \
        ' pd.inputs, pd.anexos, pd.select_anexos, pd.botao_solicitar ' \
        '   FROM conta_usuario AS us ' \
        '     INNER JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     INNER JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id ' \
        '     INNER JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
			  '     INNER JOIN etapa_solicitacao_pagina AS esp ON es.id = esp.id_etapa_solicitacao ' \
        '     LEFT JOIN pagina_dinamica AS pd ON esp.id_pagina_dinamica = pd.id ' \
        '     WHERE us.email_ins = %s AND s.id = %s AND es.ordem_etapa_solicitacao = %s; ',
        [tokenData['email_ins'], solicitationId, solicitationStepOrder])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    if not queryRes:
      abort(401, 'Usuario não possui a etapa de solicitação!')

    dados_etapa_solicitacao = '' if not queryRes[5] else json.loads(
      queryRes[5] if isinstance(queryRes[5],str) else queryRes[5].decode('utf-8'))

    inputs = '' if not queryRes[15] else json.loads(
      queryRes[15] if isinstance(queryRes[15],str) else queryRes[15].decode('utf-8'))
    
    anexos = '' if not queryRes[16] else json.loads(
      queryRes[16] if isinstance(queryRes[16],str) else queryRes[16].decode('utf-8'))
    
    selectAnexos = '' if not queryRes[17] else json.loads(
      queryRes[17] if isinstance(queryRes[17],str) else queryRes[17].decode('utf-8'))

    print('# Operation Done!')

    return {
      'etapa_solicitacao': {
        'nome_solicitacao': queryRes[0],
        'decisao': queryRes[1],
        'motivo': queryRes[2],
        'data_hora_inicio': str(queryRes[3]),
        'data_hora_fim': str(queryRes[4]),
        'dados_etapa_solicitacao': dados_etapa_solicitacao,
        'ordem_etapa_solicitacao': queryRes[6],
        'descricao': queryRes[7],
        'duracao_maxima_dias': queryRes[8],
        'nome_pagina_estatica': queryRes[9]
      },
      'pagina_dinamica': {
        'titulo': sistemStrParser(queryRes[10], tokenData),
        'perfis_permitidos': queryRes[11],
        'top_inner_html': sistemStrParser(queryRes[12], tokenData),
        'mid_inner_html': sistemStrParser(queryRes[13], tokenData),
        'bot_inner_html': sistemStrParser(queryRes[14], tokenData),
        'inputs': inputs,
        'anexos': anexos,
        'select_anexos' : selectAnexos,
        'botao_solicitar': queryRes[18]
      }
    }, 200
  
  # put to create solicitations
  def put(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs.add_argument('id_solicitacao', type=int, required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    solicitationId = solicitationsArgs['id_solicitacao']

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs)
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
        ' (id_usuario, id_etapa_solicitacao, decisao, motivo, data_hora_inicio, data_hora_fim) VALUES ' \
        '   (%s, %s, "Em analise", "Aguardando o envio de dados pelo aluno", %s, %s); ',
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
    solicitationsArgs.add_argument('solicitation', location='json', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_step_order', location='json', type=int, required=True)
    solicitationsArgs.add_argument('solicitation_data', location='json', required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    solicitationId = solicitationsArgs['solicitation']
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
        ' SELECT us.id, es.id, pes.decisao, pes.data_hora_fim, pes.json_dados, pd.inputs, pd.anexos, pd.select_anexos ' \
        '   FROM conta_usuario AS us ' \
        '     INNER JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     INNER JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id ' \
        '     INNER JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
			  '     LEFT JOIN etapa_solicitacao_pagina AS esp ON es.id = esp.id_etapa_solicitacao ' \
        '     LEFT JOIN pagina_dinamica AS pd ON esp.id_pagina_dinamica = pd.id ' \
        '     WHERE us.email_ins = %s AND s.id = %s AND es.ordem_etapa_solicitacao = %s; ',
        [tokenData['email_ins'], solicitationId, solicitationStepOrder])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    if not queryRes:
      abort(401, 'Usuario não possui a etapa de solicitação!')
    
    print('# Validating data')

    userId = queryRes[0]
    solicitationStepId = queryRes[1]
    decision = queryRes[2]
    solicitationStepEndDateTime = queryRes[3]

    solicitationStepData = '' if not queryRes[4] else json.loads(
      queryRes[4] if isinstance(queryRes[4],str) else queryRes[4].decode('utf-8'))
    
    dinamicPageInputs = '' if not queryRes[5] else json.loads(
      queryRes[5] if isinstance(queryRes[5],str) else queryRes[5].decode('utf-8'))
    
    dinamicPageFileAttachments = '' if not queryRes[6] else json.loads(
      queryRes[6] if isinstance(queryRes[6],str) else queryRes[6].decode('utf-8'))
    
    dinamicPageSelectFileAttachments = '' if not queryRes[7] else json.loads(
      queryRes[7] if isinstance(queryRes[7],str) else queryRes[7].decode('utf-8'))

    if decision != 'Em analise':
      abort(401, 'Esta solicitação está com status ' + str(decision) + '!')

    if solicitationStepData:
      abort(401, 'Esta etapa da solicitação já foi realizada aguarde sua conclusão!')

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
    reason = 'Deferido automaticamente pelo sistema'
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
          ' (id_usuario, id_etapa_solicitacao, decisao, motivo, data_hora_inicio, data_hora_fim) VALUES ' \
          '   (%s, %s, "Em analise", "Aguardando o envio de dados pelo aluno", %s, %s); ',
          [userId, nextStepId, nextStepCreatedDate, nextStepFinishDate],
          False)
        
    except Exception as e:
      dbRollback()
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    dbCommit()
    print('# DB operations done')

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
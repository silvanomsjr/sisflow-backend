from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json
import datetime

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

# Data from multiple solicitations
class Solicitations(Resource):

  # get to verify solicitations - used by student and coordinator
  def get(self):

    solicitations_args = reqparse.RequestParser()
    solicitations_args.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitations_args = solicitations_args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitations_args, ['A', 'P'])
    if not isTokenValid:
      abort(401, errorMsg)
    
    queryRes = None
    returnData = []

    print('\n# Starting get Solicitations for ' + tokenData['email_ins'])

    print('# Reading data from DB')
    # if user is student return only its data
    if tokenData['siglas'] == 'A':
      try:
        queryRes = dbGetAll(
          ' SELECT s.id AS id_solicitacao, es.id AS id_etapa_solicitacao, s.nome AS nome_solicitacao, descricao, ' \
          ' ordem_etapa_solicitacao, decisao, motivo, data_hora_inicio, data_hora_fim, json_dados ' \
          '   FROM conta_usuario AS us ' \
          '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
          '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
          '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
          '     WHERE us.email_ins = %s ' \
          '     ORDER BY data_hora_inicio DESC; ',
          [(tokenData['email_ins'])])
        
        for solic in queryRes:
          returnData.append({
            'id_solicitacao': solic[0],
            'id_etapa_solicitacao': solic[1],
            'nome_solicitacao': solic[2],
            'descricao': solic[3],
            'ordem_etapa_solicitacao': solic[4],
            'decisao': solic[5],
            'motivo': solic[6],
            'data_hora_inicio': str(solic[7]),
            'data_hora_fim': str(solic[8]),
            'json_dados': '' if not solic[9] else json.loads(solic[9].decode('utf-8')) 
          })

      except Exception as e:
        print('# Database reading error:')
        print(str(e))
        return 'Erro na base de dados', 409
    
    # if user is coordinator return all data
    elif tokenData['siglas'] == 'P':
      try:
        queryRes = dbGetAll(
          ' SELECT s.id AS id_solicitacao, es.id AS id_etapa_solicitacao, us.nome AS nome_usuario, s.nome AS nome_solicitacao, descricao, ' \
          ' ordem_etapa_solicitacao, decisao, motivo, data_hora_inicio, data_hora_fim, json_dados ' \
          '   FROM conta_usuario AS us ' \
          '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
          '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
          '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
          '     ORDER BY data_hora_inicio DESC; ')
        
        for solic in queryRes:
          returnData.append({
            'id_solicitacao': solic[0],
            'id_etapa_solicitacao': solic[1],
            'nome_usuario': solic[2],
            'nome_solicitacao': solic[3],
            'descricao': solic[4],
            'ordem_etapa_solicitacao': solic[5],
            'decisao': solic[6],
            'motivo': solic[7],
            'data_hora_inicio': str(solic[8]),
            'data_hora_fim': str(solic[9]),
            'json_dados': '' if not solic[10] else json.loads(solic[10].decode('utf-8')) 
          })

      except Exception as e:
        print('# Database reading error:')
        print(str(e))
        return 'Erro na base de dados', 409

    print('# Operation done!')

    return returnData, 200

# Data from single solicitation
class Solicitation(Resource):

  # get single solicitation and associated dinamic page data
  def get(self):

    solicitations_args = reqparse.RequestParser()
    solicitations_args.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitations_args.add_argument('solicitation', location='args', type=int, required=True)
    solicitations_args.add_argument('solicitation_step', location='args', type=int, required=True)
    solicitations_args = solicitations_args.parse_args()

    id_solicitation = solicitations_args['solicitation']
    id_solicitation_step = solicitations_args['solicitation_step']

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitations_args)
    if not isTokenValid:
      abort(401, errorMsg)

    print('\n# Starting get single solicitation for ' + tokenData['email_ins'])

    print('# Reading data from DB')
    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT s.nome AS nome_solicitacao, ' \
        '   pes.decisao, pes.motivo, pes.data_hora_inicio, pes.data_hora_fim, pes.json_dados AS dados_etapa_solicitacao, ' \
        '   es.ordem_etapa_solicitacao, es.descricao, es.duracao_maxima_dias, es.nome_pagina_estatica, ' \
        '   espd.titulo, espd.perfis_permitidos, espd.top_inner_html, espd.mid_inner_html, espd.bot_inner_html, espd.anexos_solicitados ' \
        '     FROM conta_usuario AS us ' \
        '     INNER JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     INNER JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id ' \
        '     INNER JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
        '     LEFT JOIN etapa_solicitacao_pagina_dinamica AS espd ON es.id = espd.id_etapa_solicitacao ' \
        '     WHERE us.email_ins = %s AND s.id = %s AND es.id = %s; ',
        [tokenData['email_ins'], id_solicitation, id_solicitation_step])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    if not queryRes:
      print(tokenData['email_ins'], id_solicitation, id_solicitation_step)
      abort(401, 'Usuario não possui a etapa de solicitação!')

    dados_etapa_solicitacao = '' if not queryRes[5] else json.loads(
      queryRes[5] if isinstance(queryRes[5],str) else queryRes[5].decode('utf-8'))

    anexos_solicitados = '' if not queryRes[15] else json.loads(
      queryRes[15] if isinstance(queryRes[15],str) else queryRes[15].decode('utf-8'))

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
        'titulo': queryRes[10],
        'perfis_permitidos': queryRes[11],
        'top_inner_html': queryRes[12],
        'mid_inner_html': queryRes[13],
        'bot_inner_html': queryRes[14],
        'anexos_solicitados': anexos_solicitados,
        'enviar_requisicao': True
      }
      
    }, 200
  
  # put to create solicitations
  def put(self):

    solicitations_args = reqparse.RequestParser()
    solicitations_args.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitations_args.add_argument('id_solicitacao', type=int, required=True)
    solicitations_args = solicitations_args.parse_args()

    id_solicitacao = solicitations_args['id_solicitacao']
    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitations_args)
    if not isTokenValid:
      abort(401, errorMsg)

    print('\n# Starting put Single Solicitation for ' + tokenData['email_ins'])
    
    queryRes = None
    id_usuario = None

    try:
      print('# Reading data from DB')
      queryRes = dbGetSingle(
        ' SELECT id ' \
        '   FROM conta_usuario ' \
        '   WHERE email_ins = %s; ',
        [(tokenData['email_ins'])])

      if not queryRes:
        raise Exception('No id_user return for user with ' + str(tokenData['email_ins']))
      
      id_usuario = queryRes[0]

      queryRes = dbGetSingle(
        ' SELECT es.id, duracao_maxima_dias ' \
        '   FROM solicitacao AS s JOIN etapa_solicitacao AS es ON s.id = es.id_solicitacao ' \
        '   WHERE s.id = %s AND ordem_etapa_solicitacao = 1; ',
        [(id_solicitacao)])

      if not queryRes:
        raise Exception('No step with code 1 return for solicitation with ' + str(tokenData['email_ins']))
      
      id_etapa_solicitacao = queryRes[0]
      duracao_maxima_dias = queryRes[1]

      print('# Parsing data')
      queryRes = dbGetSingle(
        ' SELECT s.id	FROM conta_usuario AS us ' \
	      '   JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
	      '   JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id ' \
	      '   JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
	      '   WHERE s.id = %s AND us.id = %s; ',
        [id_solicitacao, id_usuario])

    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if queryRes:
      abort(401, 'Você já possui essa solicitação!')
    
    # set created date and finish date based on max day interval from solicitation step
    createdDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    finishDate = (datetime.datetime.now() + datetime.timedelta(days=duracao_maxima_dias)).strftime('%Y-%m-%d %H:%M:%S')

    try:
      dbExecute(
        ' INSERT INTO  possui_etapa_solicitacao ' \
        ' (id_usuario, id_etapa_solicitacao, decisao, motivo, data_hora_inicio, data_hora_fim) VALUES ' \
        '   (%s, %s, "Em analise", "Aguardando o envio de dados pelo aluno", %s, %s); ',
        [id_usuario, id_etapa_solicitacao, createdDate, finishDate])
    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Operation done!')

    return 'ok', 200

  # post to resolve solicitations
from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.utils import getFormatedMySQLJSON

# Data from multiple solicitations - coordinator
class CoordinatorSolicitations(Resource):

  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ['A','C'])
    if not isTokenValid:
      abort(401, errorMsg)

    print('\n# Starting get Coordinator Solicitations for ' + tokenData['email_ins'] + '\n# Reading data from DB')

    queryRes = None
    returnData = []
    try:
      queryRes = dbGetAll(
        ' SELECT us.id AS id_aluno, s.id AS id_solicitacao, es.id AS id_etapa_solicitacao, us.nome AS nome_aluno, ' \
        ' pus.nome AS nome_orientador, s.nome AS nome_solicitacao, es.descricao, es.ordem_etapa_solicitacao, ' \
        ' pes.perfil_editor_atual, pes.decisao, pes.motivo, pes.data_hora_inicio, pes.data_hora_fim, pes.json_dados, perfil_editor_pagina ' \
        '   FROM conta_usuario AS us ' \
        '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
        '     JOIN etapa_solicitacao_pagina AS esp ON es.id = esp.id_etapa_solicitacao ' \
        '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
        '     LEFT JOIN perfil_professor AS pprof ON pes.siape_orientador = pprof.siape ' \
        '     LEFT JOIN possui_perfil AS pper ON pprof.id = pper.id ' \
        '     LEFT JOIN conta_usuario AS pus ON pper.id_usuario = pus.id ' \
        '     WHERE esp.perfil_editor_pagina = \'C\' '
        '     ORDER BY data_hora_inicio DESC; ')
    
      for solic in queryRes:
        returnData.append({
          'id_aluno': solic[0],
          'id_solicitacao': solic[1],
          'id_etapa_solicitacao': solic[2],
          'nome_aluno': solic[3],
          'nome_orientador': solic[4] if solic[4] else '---',
          'nome_solicitacao': solic[5],
          'descricao': solic[6],
          'ordem_etapa_solicitacao': solic[7],
          'perfil_editor_atual': solic[8],
          'decisao': solic[9],
          'motivo': solic[10],
          'data_hora_inicio': str(solic[11]),
          'data_hora_fim': str(solic[12]),
          'json_dados': getFormatedMySQLJSON(solic[13]),
          'perfil_editor_pagina': solic[14]
        })

    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Operation done!')
    return returnData, 200

# Data from multiple solicitations - professor
class ProfessorSolicitations(Resource):

  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ['P'])
    if not isTokenValid:
      abort(401, errorMsg)
    
    print('\n# Starting get Professor Solicitations for ' + tokenData['email_ins'] + '\n# Reading data from DB')

    queryRes = None
    returnData = []
    try:
      queryRes = dbGetAll(
        ' SELECT us.id AS id_aluno, s.id AS id_solicitacao, es.id AS id_etapa_solicitacao, us.nome AS nome_aluno, ' \
        ' s.nome AS nome_solicitacao, es.descricao, es.ordem_etapa_solicitacao, ' \
        ' pes.perfil_editor_atual, pes.decisao, pes.motivo, pes.data_hora_inicio, pes.data_hora_fim, pes.json_dados, perfil_editor_pagina ' \
        '   FROM conta_usuario AS us ' \
        '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
        '     JOIN etapa_solicitacao_pagina AS esp ON es.id = esp.id_etapa_solicitacao ' \
        '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
        '     JOIN perfil_professor AS pprof ON pes.siape_orientador = pprof.siape ' \
        '     JOIN possui_perfil AS pper ON pprof.id = pper.id ' \
        '     JOIN conta_usuario AS pus ON pper.id_usuario = pus.id ' \
        '     WHERE pus.id = %s AND esp.perfil_editor_pagina = %s ' \
        '     ORDER BY data_hora_inicio DESC; ',
        [tokenData['email_ins'], 'C'])
    
      for solic in queryRes:
        returnData.append({
          'id_aluno': solic[0],
          'id_solicitacao': solic[1],
          'id_etapa_solicitacao': solic[2],
          'nome_aluno': solic[3],
          'nome_solicitacao': solic[4],
          'descricao': solic[5],
          'ordem_etapa_solicitacao': solic[6],
          'perfil_editor_atual': solic[7],
          'decisao': solic[8],
          'motivo': solic[9],
          'data_hora_inicio': str(solic[10]),
          'data_hora_fim': str(solic[11]),
          'json_dados': getFormatedMySQLJSON(solic[12]),
          'perfil_editor_pagina': solic[13]
        })

    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Operation done!')
    return returnData, 200

# Data from multiple solicitations - student
class StudentSolicitations(Resource):

  def get(self):

    solicitationsArgs = reqparse.RequestParser()
    solicitationsArgs.add_argument('Authorization', location='headers', type=str, help='Bearer with jwt given by server in user autentication, required', required=True)
    solicitationsArgs = solicitationsArgs.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(solicitationsArgs, ['S'])
    if not isTokenValid:
      abort(401, errorMsg)
    
    print('\n# Starting get Student Solicitations for ' + tokenData['email_ins'] + '\n# Reading data from DB')

    queryRes = None
    returnData = []
    try:
      queryRes = dbGetAll(
        ' SELECT s.id AS id_solicitacao, es.id AS id_etapa_solicitacao, s.nome AS nome_solicitacao, descricao, ' \
        ' ordem_etapa_solicitacao, perfil_editor_atual, decisao, motivo, data_hora_inicio, data_hora_fim, json_dados, perfil_editor_pagina ' \
        '   FROM conta_usuario AS us ' \
        '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
        '     JOIN etapa_solicitacao_pagina AS esp ON es.id = esp.id_etapa_solicitacao ' \
        '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
        '     WHERE us.email_ins = %s AND esp.perfil_editor_pagina = %s ' \
        '     ORDER BY data_hora_inicio DESC; ',
        [tokenData['email_ins'], 'S'])
      
      for solic in queryRes:
        returnData.append({
          'id_solicitacao': solic[0],
          'id_etapa_solicitacao': solic[1],
          'nome_solicitacao': solic[2],
          'descricao': solic[3],
          'ordem_etapa_solicitacao': solic[4],
          'perfil_editor_atual': solic[5],
          'decisao': solic[6],
          'motivo': solic[7],
          'data_hora_inicio': str(solic[8]),
          'data_hora_fim': str(solic[9]),
          'json_dados': getFormatedMySQLJSON(solic[10]),
          'perfil_editor_pagina': solic[11]
        })

    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Operation done!')
    return returnData, 200
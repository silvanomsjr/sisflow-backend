from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

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
        ' SELECT s.id AS id_solicitacao, es.id AS id_etapa_solicitacao, us.nome AS nome_aluno, ' \
        ' pus.nome AS nome_orientador, s.nome AS nome_solicitacao, es.descricao, es.ordem_etapa_solicitacao, ' \
        ' pes.decisao, pes.motivo, pes.data_hora_inicio, pes.data_hora_fim, pes.json_dados  ' \
        '   FROM conta_usuario AS us ' \
        '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
        '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
        '     LEFT JOIN perfil_professor AS pprof ON pes.siape_orientador = pprof.siape ' \
        '     LEFT JOIN possui_perfil AS pper ON pprof.id = pper.id ' \
        '     LEFT JOIN conta_usuario AS pus ON pper.id_usuario = pus.id ' \
        '     ORDER BY data_hora_inicio DESC; ')
    
      for solic in queryRes:
        returnData.append({
          'id_solicitacao': solic[0],
          'id_etapa_solicitacao': solic[1],
          'nome_aluno': solic[2],
          'nome_orientador': solic[3] if solic[3] else '---',
          'nome_solicitacao': solic[4],
          'descricao': solic[5],
          'ordem_etapa_solicitacao': solic[6],
          'decisao': solic[7],
          'motivo': solic[8],
          'data_hora_inicio': str(solic[9]),
          'data_hora_fim': str(solic[10]),
          'json_dados': '' if not solic[11] else json.loads(
            solic[11] if isinstance(solic[11],str) else solic[11].decode('utf-8'))
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
        ' SELECT s.id AS id_solicitacao, es.id AS id_etapa_solicitacao, us.nome AS nome_aluno, ' \
        ' s.nome AS nome_solicitacao, es.descricao, es.ordem_etapa_solicitacao, ' \
        ' pes.decisao, pes.motivo, pes.data_hora_inicio, pes.data_hora_fim, pes.json_dados  ' \
        '   FROM conta_usuario AS us ' \
        '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
        '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
        '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
        '     JOIN perfil_professor AS pprof ON pes.siape_orientador = pprof.siape ' \
        '     JOIN possui_perfil AS pper ON pprof.id = pper.id ' \
        '     JOIN conta_usuario AS pus ON pper.id_usuario = pus.id ' \
        '     WHERE pus.id = %s '
        '     ORDER BY data_hora_inicio DESC; ',
        [(tokenData['id_usuario'])])
    
      for solic in queryRes:
        returnData.append({
          'id_solicitacao': solic[0],
          'id_etapa_solicitacao': solic[1],
          'nome_aluno': solic[2],
          'nome_solicitacao': solic[3],
          'descricao': solic[4],
          'ordem_etapa_solicitacao': solic[5],
          'decisao': solic[6],
          'motivo': solic[7],
          'data_hora_inicio': str(solic[8]),
          'data_hora_fim': str(solic[9]),
          'json_dados': '' if not solic[10] else json.loads(
            solic[10] if isinstance(solic[10],str) else solic[10].decode('utf-8'))
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
          'json_dados': '' if not solic[9] else json.loads(
            solic[9] if isinstance(solic[9],str) else solic[9].decode('utf-8'))
        })

    except Exception as e:
      print('# Database reading error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Operation done!')
    return returnData, 200
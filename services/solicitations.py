from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import json

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid

class Solicitations(Resource):

  # get to verify solicitations
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

    # if user is student return only its data
    if tokenData['siglas'] == 'A':
      try:
        queryRes = dbGetAll(
          ' SELECT s.nome AS nome_solicitacao, descricao, ' \
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
            'nome_solicitacao': solic[0],
            'descricao': solic[1],
            'ordem_etapa_solicitacao': solic[2],
            'decisao': solic[3],
            'motivo': solic[4],
            'data_hora_inicio': str(solic[5]),
            'data_hora_fim': str(solic[6]),
            'json_dados': '' if not solic[7] else json.loads(solic[7].decode('utf-8')) 
          })

      except Exception as e:
        print('# Database reading error:')
        print(str(e))
    
    # if user is coordinator return all data
    elif tokenData['siglas'] == 'P':
      try:
        queryRes = dbGetAll(
          ' SELECT us.nome AS nome_usuario, s.nome AS nome_solicitacao, descricao, ' \
          ' ordem_etapa_solicitacao, decisao, motivo, data_hora_inicio, data_hora_fim, json_dados ' \
          '   FROM conta_usuario AS us ' \
          '     JOIN possui_etapa_solicitacao AS pes ON us.id = pes.id_usuario ' \
          '     JOIN etapa_solicitacao AS es ON pes.id_etapa_solicitacao = es.id  ' \
          '     JOIN solicitacao AS s ON es.id_solicitacao = s.id ' \
          '     ORDER BY data_hora_inicio DESC; ')
        
        for solic in queryRes:
          returnData.append({
            'nome_usuario': solic[0],
            'nome_solicitacao': solic[1],
            'descricao': solic[2],
            'ordem_etapa_solicitacao': solic[3],
            'decisao': solic[4],
            'motivo': solic[5],
            'data_hora_inicio': str(solic[6]),
            'data_hora_fim': str(solic[7]),
            'json_dados': '' if not solic[8] else json.loads(solic[8].decode('utf-8')) 
          })

      except Exception as e:
        print('# Database reading error:')
        print(str(e))

    print(queryRes)
    return returnData, 200
  
  # put to create solicitations

  # post to resolve solicitations
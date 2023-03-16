from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
from base64 import b64decode
import random
import string
import json
import os
import time

from utils.dbUtils import *
from utils.cryptoFunctions import jwtEncode, jwtDecode, getHashPassword
from utils.smtpMails import smtpSend

class Login(Resource):
    
  def post(self):
    
    loginArgs = reqparse.RequestParser()
    loginArgs.add_argument('Authorization', location='headers', type=str, help='Email and hash password of the user, used to authentication, required!', required=True)
    loginArgs = loginArgs.parse_args()

    mailIns, plainPassword = b64decode( loginArgs['Authorization'].replace('Basic ', '') ).decode('utf-8').split(':', 1)
    print('\n# Starting Login authentication for ' + str(mailIns))

    userRawData = None
    try:
      userRawData = dbGetSingle(
        " SELECT id, email_ins, email_sec, nome, sexo, telefone, hash_senha, salt_senha, data_hora_criacao " \
        "   FROM conta_usuario WHERE email_ins = %s; ",
        [(mailIns)])
    except Exception as e:
      print('# Database error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if userRawData == None or len(userRawData) != 9 or userRawData[6] == None:
      abort(401, 'Usuário não cadastrado!')
    print('# User found')
    
    hashP, _ = getHashPassword(plainPassword, userRawData[7])

    if hashP != userRawData[6]:
      abort(401, 'Senha incorreta!')
    print('# Password verifyed')

    # initial user data token creation
    userData = {
      'id_usuario': userRawData[0],
      'email_ins': userRawData[1],
      'email_sec': userRawData[2],
      'nome': userRawData[3],
      'sexo': userRawData[4],
      'telefone': userRawData[5],
      'data_hora_criacao': str(userRawData[8])
    }

    userRawProfiles = []
    try:
      userRawProfiles = dbGetAll(
        " SELECT p.id, p.data_hora_inicio, p.data_hora_fim, " \
        " padmin.id, " \
        " paluno.id, paluno.matricula, paluno.curso, " \
        " pprof.id, pprof.siape, " \
        " pcoor.id, pcoor.siape " \
        "   FROM conta_usuario AS us " \
        "   INNER JOIN possui_perfil AS p ON us.id = p.id_usuario " \
        "   LEFT JOIN perfil_admin AS padmin ON p.id = padmin.id " \
        "   LEFT JOIN perfil_aluno AS paluno ON p.id = paluno.id " \
        "   LEFT JOIN perfil_professor AS pprof ON p.id = pprof.id " \
        "   LEFT JOIN perfil_coordenador AS pcoor ON p.id = pcoor.id " \
        "   WHERE us.email_ins = %s; ",
      [(mailIns)])
    except Exception as e:
      print('# Database error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if userRawProfiles == None:
      abort(401, 'Usuário desativado, consulte o coordenador para reativar!')
      
    print(userRawProfiles)
    
    userProfiles = []
    for profile in userRawProfiles:
      # admin
      if profile[3]:
        userProfiles.append("A")
      # student
      elif profile[4]:
        userProfiles.append("S")
        userData['perfil_aluno'] = {
          'matricula' : profile[5],
          'curso' : profile[6]
        }
      # professor
      elif profile[7]:
        userProfiles.append("P")
        userData['perfil_professor'] = {
          'siape' : profile[8]
        }
      # coordinator
      elif profile[9]:
        userProfiles.append("C")
        userData['perfil_coordenador'] = {
          'siape' : profile[10]
        }

    userData['perfis'] = userProfiles

    jwtRoken = jwtEncode(userData)
    print('# User profile verifyed, authentication done')
    return jwtRoken, 200

class Sign(Resource):

  # post to create and send mail with sign code 
  def post(self):

    signArgs = reqparse.RequestParser()
    signArgs.add_argument('email_ins', type=str, required=True)
    signArgs = signArgs.parse_args()

    mailIns = signArgs['email_ins']
    print('\n# Starting user Get Authentication Code for ' + str(mailIns))
    print('# Verifying data consistency')

    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT email_ins, hash_senha FROM conta_usuario ' \
        '   WHERE email_ins = %s; ',
        [(mailIns)])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if queryRes == None:
      abort(404, 'Email institucional não encontrado no sistema!')

    if queryRes[1] != None:
      abort(401, 'Email já utilizado!')

    try:
      queryRes = dbGetSingle(
        ' SELECT email_ins, codigo FROM validacao_email ' \
        '   WHERE email_ins = %s; ',
        [(mailIns)])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Data ok, updating auth table')
    signCode = ''.join(
      random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
      for _ in range(10))

    sqlScrypt = ''
    if queryRes != None and len(queryRes) != 0:
      sqlScrypt = ' UPDATE validacao_email SET codigo = %s WHERE email_ins = %s; '
    else:
      sqlScrypt = ' INSERT INTO validacao_email (codigo, email_ins) VALUES (%s,%s); '
      
    try:
      dbExecute(sqlScrypt, [signCode, mailIns])
    except Exception as e:
      print('# Database insertion error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Sending mail')

    acessToken = jwtEncode({ 'email_ins': mailIns, 'cad_code': signCode })
    acessUrl = os.getenv('FRONT_BASE_URL') + 'sign?acess_token=' + acessToken
    
    innerMailHtml = f'''
      <p>Este é seu código de cadastro: {signCode} </p>
      <p>Você também pode continuar o cadastro ao clicar neste <a href="{acessUrl}">link</a></p>
    '''

    try:
      smtpSend(mailIns, 'Confirmação de cadastro Sisges', innerMailHtml)
    except Exception as e:
      print('# SMTP error:')
      print(str(e))
      return 'Erro ao enviar emails', 409

    print('# Operation done!')
    return '', 200
  
  # Get to verify cad code
  def get(self):

    signArgs = reqparse.RequestParser()
    signArgs.add_argument('acess_token', location='args', type=str)
    signArgs.add_argument('email_ins', location='args', type=str)
    signArgs.add_argument('cad_code', location='args', type=str)
    signArgs = signArgs.parse_args()

    print('\n# Starting user Sign code verification')

    if not signArgs['acess_token'] and (not signArgs['email_ins'] or not signArgs['cad_code']):
      abort(400, "Missing acess_token token or email_ins and cad_code")

    mailIns = None
    signCode = None
    
    if signArgs['acess_token']:
      try:
        acessToken = jwtDecode(signArgs['acess_token'])
      except Exception as e:
        print('# JWT decoding error:')
        print(str(e))
        return 'Codigo de acesso invalido', 401

      mailIns = acessToken['email_ins']
      signCode = acessToken['cad_code']

    else:
      mailIns = signArgs['email_ins']
      signCode = signArgs['cad_code']

    print('# Testing acess token for ' + str(mailIns))

    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT email_ins, codigo FROM validacao_email ' \
        '   WHERE email_ins = %s AND codigo = %s; ',
        [mailIns, signCode])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if queryRes and len(queryRes) == 2:
      print('# Verification ok')
      return { 'email_ins': mailIns , 'cad_code' : signCode}, 200

    print('# Verification not ok')
    return False, 401

  # put a new user given a cad code
  def put(self):
    
    signArgs = reqparse.RequestParser()
    signArgs.add_argument('email_ins', type=str, required=True)
    signArgs.add_argument('email_sec', type=str)
    signArgs.add_argument('telefone', type=str)
    signArgs.add_argument('senha', type=str, required=True)
    signArgs.add_argument('cad_code', type=str, required=True)
    signArgs = signArgs.parse_args()

    mailIns = signArgs['email_ins']
    mailSec = signArgs['email_sec'] if signArgs['email_sec'] else ""
    phoneNum = signArgs['telefone'] if signArgs['telefone'] else ""
    plainPass = signArgs['senha']
    signCode = signArgs['cad_code']
    
    print('\n# Starting user Sign Authentication for ' + str(mailIns))
    print('# Verifying data consistency')

    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT id, email_ins, hash_senha FROM conta_usuario ' \
        '   WHERE email_ins = %s; ',
        [(mailIns)])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if queryRes == None:
      abort(404, 'Email institucional não encontrado no sistema!')

    if queryRes[2] != None:
      abort(401, 'Email já utilizado!')

    try:
      queryRes = dbGetSingle(
        ' SELECT email_ins, codigo FROM validacao_email ' \
        '   WHERE email_ins = %s AND codigo = %s; ',
        [mailIns, signCode])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if queryRes == None or len(queryRes) != 2:
      abort(401, 'Chave de cadastro inválida para este email!')
      
    print('# Registering user')

    hashPass, saltPass = getHashPassword(plainPass)
    datetimeNow = time.strftime('%Y-%m-%d %H:%M:%S')
    
    sqlScrypt = ' UPDATE conta_usuario SET ' \
      ' email_sec = %s, ' \
      ' telefone = %s, ' \
      ' hash_senha = %s, ' \
      ' salt_senha = %s, ' \
      ' data_hora_criacao = %s ' \
      ' WHERE email_ins = %s '
    try:
      dbExecute(sqlScrypt, [mailSec, phoneNum, hashPass, saltPass, datetimeNow, mailIns])
    except Exception as e:
      print('# Database insertion error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# User sign complete!')
    return '', 201
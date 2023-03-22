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

    emailIns, plainPassword = b64decode( loginArgs['Authorization'].replace('Basic ', '') ).decode('utf-8').split(':', 1)
    print('\n# Starting Login authentication for ' + str(emailIns))

    userRawData = None
    try:
      userRawData = dbGetSingle(
        " SELECT id, institutional_email, secondary_email, user_name, gender, phone, password_hash, password_salt, creation_datetime " \
        "   FROM user_account WHERE email_ins = %s; ",
        [(emailIns)])
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
      "user_id": userRawData[0],
      "institutional_email": userRawData[1],
      "secondary_email": userRawData[2],
      "user_name": userRawData[3],
      "gender": userRawData[4],
      "phone": userRawData[5],
      "creation_datetime": str(userRawData[8])
    }

    userRawProfiles = []
    try:
      userRawProfiles = dbGetAll((
        " SELECT p.profile_name, p.profile_acronym, p.profile_dynamic_fields_metadata, "
        " uhp.user_dinamyc_profile_fields_data, uhp.start_datetime, uhp.end_datetime, "
        " uhpcoordinator.siape, "
        " uhpprofessor.siape, "
        " uhpstudent.matricula, uhpstudent.course, "
        "   FROM user_account AS us "
        "   INNER JOIN user_has_profile AS uhp ON us.id = uhp.user_id "
        "   INNER JOIN profile AS p ON uhp.profile_id = p.id "
        "   LEFT JOIN user_has_profile_coordinator_data AS uhpcoordinator ON uhp.id = uhpcoordinator.user_has_profile_id "
        "   LEFT JOIN user_has_profile_student_data AS uhpstudent ON uhp.id = uhpstudent.user_has_profile_id "
        "   LEFT JOIN user_has_profile_professor_data AS uhpprofessor ON uhp.id = uhpprofessor.user_has_profile_id "
        "   WHERE us.id = %s; "),
      [(userData["user_id"])])
    except Exception as e:
      print("# Database error:")
      print(str(e))
      return "Erro na base de dados", 409

    if userRawProfiles == None:
      abort(401, "Usuário desativado, consulte o coordenador para reativar!")
      
    print(userRawProfiles)
    
    userProfiles = []
    for profile in userRawProfiles:

      userProfile = {}
      userProfile["profile_name"] = profile[0]
      userProfile["profile_acronym"] = profile[1]
      userProfile["profile_dynamic_fields_metadata"] = profile[2]
      userProfile["user_dinamyc_profile_fields_data"] = profile[3]
      userProfile["start_datetime"] = profile[4]
      userProfile["end_datetime"] = profile[5]

      # coordinator
      if profile[6]:
        userProfile["siape"] = profile[6]

      # professor
      elif profile[7]:
        userProfile["siape"] = profile[7]

      # student
      elif profile[8]:
        userProfile["matricula"] = profile[8]
        userProfile["course"] = profile[9]
      
      userProfiles.append(userProfile)

    userData['profiles'] = userProfiles

    jwtToken = jwtEncode(userData)
    print('# User profile verifyed, authentication done')
    return jwtToken, 200

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
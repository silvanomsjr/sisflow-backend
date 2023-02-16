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
from utils.smtpMails import sendSignKey

class Login(Resource):
    
  def post(self):
    
    login_args = reqparse.RequestParser()
    login_args.add_argument('Authorization', location='headers', type=str, help='Email and hash password of the user, used to authentication, required!', required=True)
    login_args = login_args.parse_args()

    email_ins, plain_password = b64decode( login_args['Authorization'].replace('Basic ', '') ).decode('utf-8').split(':', 1)
    print('\n# Starting Login authentication for ' + str(email_ins))

    sqlScrypt = " SELECT id, email_ins, email_sec, nome, telefone, hash_senha, salt_senha, data_hora_criacao, siglas, jsons " \
      " FROM conta_usuario AS usuario JOIN ( " \
      "   SELECT id_usuario,  " \
      "     GROUP_CONCAT(sigla SEPARATOR ',') AS siglas, " \
      "     GROUP_CONCAT(json_dados SEPARATOR ',') AS jsons " \
      "     FROM possui_perfil AS pper JOIN perfil AS per ON pper.id = per.id  " \
      "           GROUP BY id_usuario " \
      " ) AS perfis ON usuario.id = perfis.id_usuario " \
      "   WHERE email_ins = %s; "
    try:
      r = dbGetSingle(sqlScrypt, [(email_ins)])
    except Exception as e:
      print('# Database error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if r == None or len(r) != 10:
      abort(401, 'Usuário não cadastrado!')
    print('# User found')
    
    hash_p, _ = getHashPassword(plain_password, r[6])

    if hash_p != r[5]:
      abort(401, 'Senha incorreta!')
    print('# Password verifyed')
    
    jsons = '' if not r[9] else json.loads(r[9].decode('utf-8'))
    token_data = {
      'email_ins': r[1],
      'email_sec': r[2],
      'nome': r[3],
      'telefone': r[4],
      'data_hora_criacao': str(r[7]),
      'siglas' : r[8], 
      'jsons': jsons
    }

    jwt_token = jwtEncode(token_data)

    print('# Authentication done!')
    return jwt_token, 200

class Sign(Resource):

  # post to create and send mail with sign code 
  def post(self):

    sign_args = reqparse.RequestParser()
    sign_args.add_argument('email_ins', type=str, required=True)
    sign_args = sign_args.parse_args()

    email_ins = sign_args['email_ins']
    print('\n# Starting user Get Authentication Code for ' + str(email_ins))
    
    cad_code = ''.join(
      random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
      for _ in range(10))

    print('# Verifying data consistency')

    r = None
    sqlScrypt = ' SELECT email_ins, hash_senha FROM conta_usuario ' \
      ' WHERE email_ins = %s; '
    try:
      r = dbGetSingle(sqlScrypt, [(email_ins)])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if r == None:
      abort(404, 'Email institucional não encontrado no sistema!')

    if r[1] != None:
      abort(401, 'Email já utilizado!')

    sqlScrypt = ' SELECT email_ins, codigo FROM validacao_email ' \
      ' WHERE email_ins = %s; '
    try:
      r = dbGetSingle(sqlScrypt, [(email_ins)])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Data ok, updating auth table')
    if r != None and len(r) != 0:
      sqlScrypt = ' UPDATE validacao_email SET codigo = %s WHERE email_ins = %s; '
    else:
      sqlScrypt = ' INSERT INTO validacao_email (codigo, email_ins) VALUES (%s,%s); '
      
    try:
      dbExecute(sqlScrypt, [cad_code, email_ins])
    except Exception as e:
      print('# Database insertion error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Sending mail')

    sendMailTo = email_ins
    sendInnerHtml = ''
    sendDebug = False
    token_data = {
      'email_ins': email_ins,
      'cad_code': cad_code
    }
    acess_token = jwtEncode(token_data)
    acess_url = os.getenv('FRONT_BASE_URL') + 'sign/acess_token=' + acess_token
    
    if os.getenv('SYS_DEBUG') == 'True':
      sendMailTo = os.getenv('SMTP_LOGIN')
      sendInnerHtml = f'''
      <p> Modo de testes ativo </p>
      <p> Deveria ser enviado a este email: {email_ins} </p>
      '''
      sendDebug = True

    try:
      sendSignKey(sendMailTo, cad_code, acess_url, sendInnerHtml, sendDebug)
    except Exception as e:
      print('# SMTP error:')
      print(str(e))
      return 'Erro ao enviar emails', 409

    print('# Operation done!')
    return '', 200
  
  # Get to verify cad code
  def get(self):

    sign_args = reqparse.RequestParser()
    sign_args.add_argument('acess_token', location='args', type=str)
    sign_args.add_argument('email_ins', location='args', type=str)
    sign_args.add_argument('cad_code', location='args', type=str)
    sign_args = sign_args.parse_args()

    print('\n# Starting user Sign code verification')

    if not sign_args['acess_token'] and (not sign_args['email_ins'] or not sign_args['cad_code']):
      abort(400, "Missing acess_token token or email_ins and cad_code")

    email_ins = None
    cad_code = None
    
    if sign_args['acess_token']:
      try:
        acess_token = jwtDecode(sign_args['acess_token'])
      except Exception as e:
        print('# JWT decoding error:')
        print(str(e))
        return 'Codigo de acesso invalido', 401

      email_ins = acess_token['email_ins']
      cad_code = acess_token['cad_code']

    else:
      email_ins = sign_args['email_ins']
      cad_code = sign_args['cad_code']

    print('# Testing acess token for ' + str(email_ins))

    sqlScrypt = ' SELECT email_ins, codigo FROM validacao_email ' \
      '  WHERE email_ins = %s AND codigo = %s; '
    try:
      r = dbGetSingle(sqlScrypt, [email_ins, cad_code])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# Verification done')
    if r and len(r) == 2:
      return True, 200

    return False, 401

  # put a new user given a cad code
  def put(self):
    
    sign_args = reqparse.RequestParser()
    sign_args.add_argument('email_ins', type=str, required=True)
    sign_args.add_argument('email_sec', type=str)
    sign_args.add_argument('telefone', type=str)
    sign_args.add_argument('senha', type=str, required=True)
    sign_args.add_argument('cad_code', type=str, required=True)
    sign_args = sign_args.parse_args()

    email_ins = sign_args['email_ins']
    email_sec = sign_args['email_sec'] if sign_args['email_sec'] else ""
    phone_num = sign_args['telefone'] if sign_args['telefone'] else ""
    plain_pass = sign_args['senha']
    cad_code = sign_args['cad_code']
    
    print('\n# Starting user Sign Authentication for ' + str(email_ins))
    print('# Verifying data consistency')

    r = None
    sqlScrypt = ' SELECT id, email_ins, hash_senha FROM conta_usuario ' \
      ' WHERE email_ins = %s; '
    try:
      r = dbGetSingle(sqlScrypt, [(email_ins)])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if r == None:
      abort(404, 'Email institucional não encontrado no sistema!')

    if r[2] != None:
      abort(401, 'Email já utilizado!')

    sqlScrypt = ' SELECT email_ins, codigo FROM validacao_email ' \
      '  WHERE email_ins = %s AND codigo = %s; '
    try:
      r = dbGetSingle(sqlScrypt, [email_ins, cad_code])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409

    if r == None or len(r) != 2:
      abort(401, 'Chave de cadastro inválida para este email!')
      
    print('# Registering user')

    hash_pass, salt_pass = getHashPassword(plain_pass)
    datetime_now = time.strftime('%Y-%m-%d %H:%M:%S')
    
    sqlScrypt = ' UPDATE conta_usuario SET ' \
      ' email_sec = %s, ' \
      ' telefone = %s, ' \
      ' hash_senha = %s, ' \
      ' salt_senha = %s, ' \
      ' data_hora_criacao = %s ' \
      ' WHERE email_ins = %s '
    try:
      dbExecute(sqlScrypt, [email_sec, phone_num, hash_pass, salt_pass, datetime_now, email_ins])
    except Exception as e:
      print('# Database insertion error:')
      print(str(e))
      return 'Erro na base de dados', 409

    print('# User sign complete!')
    return '', 201
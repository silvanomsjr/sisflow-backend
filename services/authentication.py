from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
from base64 import b64decode
import random
import os

from utils.dbUtils import *
from utils.jwtfunctions import jwtEncode
from utils.smtpMails import sendSignNumber
   
class Login(Resource):
    
  def post(self):
    
    login_args = reqparse.RequestParser()
    login_args.add_argument('Authorization', location='headers', type=str, help='Email and hash password of the user, used to authentication, required!', required=True)
    login_args = login_args.parse_args()

    email_ins, hash_password = b64decode( login_args['Authorization'].replace('Basic ', '') ).decode('utf-8').split(':', 1)

    sqlScrypt = ' SELECT hash_senha, id_usuario AS id, tipo, nome, telefone, email_ins, email_sec ' \
      ' FROM tbl_usuario us JOIN tbl_pessoa pes ON us.id_usuario = pes.id_pessoa ' \
      ' WHERE email_ins = %s; '
    
    r = dbGetSingle(sqlScrypt, [(email_ins)])
    
    if r == None or len(r) != 7:
      abort(401, 'Usuário não cadastrado!')
    
    if r[0] != hash_password:
      abort(401, 'Senha incorreta!')

    token_data = None

    if r[2] == 'P':
      token_data = {
        'siape': r[1], 
        'tipo' : r[2], 
        'nome': r[3], 
        'telefone': r[4],
        'email_ins': r[5],
        'email_sec': r[6]
      }
    else:
      token_data = { 
        'matricula': r[1], 
        'tipo' : r[2], 
        'nome': r[3], 
        'telefone': r[4], 
        'email_ins': r[5], 
        'email_sec': r[6] 
      }

    jwt_token = jwtEncode(token_data)

    return jwt_token, 200

class SignWithCode(Resource):

  # post to create and get a sign code 
  def post(self):

    sign_args = reqparse.RequestParser()
    sign_args.add_argument('email_ins', type=str, required=True)
    sign_args = sign_args.parse_args()

    email_ins = sign_args['email_ins']
    sign_code = random.randint(100000000, 999999999)

    sqlScrypt = ' SELECT email_ins ' \
    ' FROM tbl_usuario us JOIN tbl_pessoa pes ON us.id_usuario = pes.id_pessoa ' \
    ' WHERE email_ins = %s; '
    r = dbGetSingle(sqlScrypt, [(email_ins)])
    if r != None:
      abort(401, 'Email já utilizado!')

    sqlScrypt = ' SELECT id_pessoa AS id FROM tbl_pessoa WHERE email_ins = %s; '
    r = dbGetSingle(sqlScrypt, [(email_ins)])

    if r == None or len(r) != 1:
      abort(404, 'Email institucional não encontrado no sistema!')

    sqlScrypt = ' SELECT chave_cadastro FROM tbl_chave_cadastro WHERE email_ins = %s; '
    r = dbGetSingle(sqlScrypt, [(email_ins)])
    
    if r != None and len(r) != 0:
      sqlScrypt = ' UPDATE tbl_chave_cadastro SET chave_cadastro = %s WHERE email_ins = %s; '
    else:
      sqlScrypt = ' INSERT INTO tbl_chave_cadastro (chave_cadastro, email_ins) VALUES (%s,%s); '
    
    dbExecute(sqlScrypt, [sign_code, email_ins])

    if os.getenv('SYS_DEBUG') == 'True':
      innerHtml = f'''
      <p> Modo de testes ativo </p>
      <p> Deveria ser enviado a este email: {email_ins} </p>
      '''
      sendSignNumber(
        os.getenv('SMTP_LOGIN'),
        sign_code,
        innerHtml,
        True)

      return {'email_ins': email_ins, 'chave_cadastro': sign_code }, 200
    
    sendSignNumber(email_ins, sign_code)
    return '', 200
  
  # put a new user given a sign code
  def put(self):
    
    sign_args = reqparse.RequestParser()
    sign_args.add_argument('email_ins', type=str, required=True)
    sign_args.add_argument('email_sec', type=str)
    sign_args.add_argument('hash_senha', type=str, required=True)
    sign_args.add_argument('cad_code', type=str, required=True)
    sign_args = sign_args.parse_args()

    email_ins = sign_args['email_ins']
    hash_senha = sign_args['hash_senha']
    cad_code = sign_args['cad_code']
    if sign_args['email_sec']:
      email_sec = sign_args['email_sec']
    else:
      email_sec = ""
    
    sqlScrypt = ' SELECT email_ins ' \
    ' FROM tbl_usuario us JOIN tbl_pessoa pes ON us.id_usuario = pes.id_pessoa ' \
    ' WHERE email_ins = %s; '
    r = dbGetSingle(sqlScrypt, [(email_ins)])
    if r != None:
      abort(401, 'Email já utilizado!')
    
    sqlScrypt = ' SELECT id_pessoa AS id FROM tbl_pessoa WHERE email_ins = %s; '
    r = dbGetSingle(sqlScrypt, [(email_ins)])
    if r == None or len(r) != 1:
      abort(404, 'Email institucional não encontrado no sistema!')
    id_usuario = r[0]
    
    sqlScrypt = ' SELECT chave_cadastro FROM tbl_chave_cadastro ' \
      ' WHERE chave_cadastro = %s AND email_ins = %s; '
    r = dbGetSingle(sqlScrypt, [cad_code, email_ins])
    if r == None or len(r) != 1:
      abort(404, 'Chave de cadastro inválida para este email!')

    try:
      sqlScrypt = ' INSERT INTO tbl_usuario (id_usuario, hash_senha) VALUES (%s,%s); '
      dbExecute(sqlScrypt, [id_usuario, hash_senha], False)

      if email_sec != None:
        sqlScrypt = ' UPDATE tbl_pessoa SET email_sec = %s WHERE email_ins = %s; '
        dbExecute(sqlScrypt, [email_sec, email_ins], False)
      
      dbCommit()

    except Exception as e:

      dbRollback()
      return 'Erro ao criar o usuário ' + str(e), 409

    return '', 201
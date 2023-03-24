from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
from base64 import b64decode
import random
import string
import os
import time

from utils.dbUtils import *
from utils.cryptoFunctions import jwtEncode, jwtDecode, getHashPassword
from utils.smtpMails import smtpSend

class Login(Resource):
    
  def post(self):
    
    loginArgs = reqparse.RequestParser()
    loginArgs.add_argument("Authorization", location="headers", type=str, help="Email and hash password of the user, used to authentication, required!", required=True)
    loginArgs = loginArgs.parse_args()

    insEmail, plainPassword = b64decode( loginArgs["Authorization"].replace("Basic ", "") ).decode("utf-8").split(':', 1)
    print("\n# Starting Login authentication for " + str(insEmail))

    userRawData = None
    try:
      userRawData = dbGetSingle(
        " SELECT id, institutional_email, secondary_email, user_name, gender, phone, password_hash, password_salt, creation_datetime "
        "   FROM user_account WHERE institutional_email = %s; ",
        [(insEmail)])
    except Exception as e:
      print("# Database error:")
      print(str(e))
      return "Erro na base de dados", 409

    if userRawData == None or len(userRawData) != 9 or userRawData[6] == None:
      abort(401, "Usuário não cadastrado!")
    print("# User found")
    
    hashP, _ = getHashPassword(plainPassword, userRawData[7])

    if hashP != userRawData[6]:
      abort(401, "Senha incorreta!")
    print("# Password verifyed")

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
      userRawProfiles = dbGetAll(
        " SELECT p.profile_name, p.profile_acronym, p.profile_dynamic_fields_metadata, "
        " uhp.user_dinamyc_profile_fields_data, uhp.start_datetime, uhp.end_datetime, "
        " uhpcoordinator.siape, "
        " uhpprofessor.siape, "
        " uhpstudent.matricula, uhpstudent.course "
        "   FROM user_account AS us "
        "   INNER JOIN user_has_profile AS uhp ON us.id = uhp.user_id "
        "   INNER JOIN profile AS p ON uhp.profile_id = p.id "
        "   LEFT JOIN user_has_profile_coordinator_data AS uhpcoordinator ON uhp.id = uhpcoordinator.user_has_profile_id "
        "   LEFT JOIN user_has_profile_student_data AS uhpstudent ON uhp.id = uhpstudent.user_has_profile_id "
        "   LEFT JOIN user_has_profile_professor_data AS uhpprofessor ON uhp.id = uhpprofessor.user_has_profile_id "
        "   WHERE us.id = %s; ",
      [(userData["user_id"])])
    except Exception as e:
      print("# Database error:")
      print(str(e))
      return "Erro na base de dados", 409

    if userRawProfiles == None:
      abort(401, "Usuário desativado, consulte o coordenador para reativar!")
    
    userProfilesAcronyms = []
    userProfiles = []
    for profile in userRawProfiles:

      userProfile = {}
      userProfile["profile_name"] = profile[0]
      userProfile["profile_acronym"] = profile[1]
      userProfile["profile_dynamic_fields_metadata"] = profile[2]
      userProfile["user_dinamyc_profile_fields_data"] = profile[3]
      userProfile["start_datetime"] = str(profile[4])
      userProfile["end_datetime"] = str(profile[5])

      userProfilesAcronyms.append(userProfile["profile_acronym"])

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

    userData["profiles"] = userProfiles
    userData["profile_acronyms"] = userProfilesAcronyms

    jwtToken = jwtEncode(userData)
    print("# User profile verifyed, authentication done")
    return jwtToken, 200

class Sign(Resource):

  # post to create and send mail with sign code 
  def post(self):

    signArgs = reqparse.RequestParser()
    signArgs.add_argument("institutional_email", type=str, required=True)
    signArgs = signArgs.parse_args()

    insEmail = signArgs["institutional_email"]
    print("\n# Starting user Get Authentication Code for " + str(insEmail))
    print("# Verifying data consistency")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT institutional_email, password_hash FROM user_account "
        "   WHERE institutional_email = %s; ",
        [(insEmail)])
    except Exception as e:
      print("# Database searching error:")
      print(str(e))
      return "Erro na base de dados", 409

    if queryRes == None:
      abort(404, "Email institucional não encontrado no sistema!")

    if queryRes[1] != None:
      abort(401, "Email já utilizado!")

    try:
      queryRes = dbGetSingle(
        " SELECT institutional_email, validation_code FROM mail_validation "
        "   WHERE institutional_email = %s; ",
        [(insEmail)])
    except Exception as e:
      print("# Database searching error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Data ok, updating auth table")
    signCode = "".join(
      random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
      for _ in range(10))

    sqlScrypt = ""
    if queryRes != None and len(queryRes) != 0:
      sqlScrypt = " UPDATE mail_validation SET validation_code = %s WHERE institutional_email = %s; "
    else:
      sqlScrypt = " INSERT INTO mail_validation (validation_code, institutional_email) VALUES (%s,%s); "
      
    try:
      dbExecute(sqlScrypt, [signCode, insEmail])
    except Exception as e:
      print("# Database insertion error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Sending mail")

    acessToken = jwtEncode({ "institutional_email": insEmail, "validation_code": signCode })
    acessUrl = os.getenv("FRONT_BASE_URL") + "sign?acess_token=" + acessToken
    
    innerMailHtml = f'''
      <p>Este é seu código de cadastro: {signCode} </p>
      <p>Você também pode continuar o cadastro ao clicar neste <a href="{acessUrl}">link</a></p>
    '''

    try:
      smtpSend(insEmail, "Confirmação de cadastro Sisges", innerMailHtml)
    except Exception as e:
      print("# SMTP error:")
      print(str(e))
      return "Erro ao enviar emails", 409

    print("# Operation done!")
    return "", 200
  
  # Get to verify cad code
  def get(self):

    signArgs = reqparse.RequestParser()
    signArgs.add_argument("acess_token", location="args", type=str)
    signArgs.add_argument("institutional_email", location="args", type=str)
    signArgs.add_argument("validation_code", location="args", type=str)
    signArgs = signArgs.parse_args()

    print("\n# Starting user Sign code verification")

    if not signArgs["acess_token"] and (not signArgs["institutional_email"] or not signArgs["validation_code"]):
      abort(400, "Missing acess_token token or institutional_email and validation_code")

    insEmail = None
    valCode = None
    
    if signArgs["acess_token"]:
      try:
        acessToken = jwtDecode(signArgs["acess_token"])
      except Exception as e:
        print("# JWT decoding error:")
        print(str(e))
        return "Codigo de acesso invalido", 401

      insEmail = acessToken["institutional_email"]
      valCode = acessToken["validation_code"]

    else:
      insEmail = signArgs["institutional_email"]
      valCode = signArgs["validation_code"]

    print("# Testing acess token for " + str(insEmail))

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT institutional_email, validation_code FROM mail_validation "
        "   WHERE institutional_email = %s AND validation_code = %s; ",
        [insEmail, valCode])
    except Exception as e:
      print("# Database searching error:")
      print(str(e))
      return "Erro na base de dados", 409

    if queryRes and len(queryRes) == 2:
      print("# Verification ok")
      return { "institutional_email": insEmail , "validation_code" : valCode}, 200

    print("# Verification not ok")
    return False, 401

  # put a new user given a cad code
  def put(self):
    
    signArgs = reqparse.RequestParser()
    signArgs.add_argument("institutional_email", type=str, location="json", required=True)
    signArgs.add_argument("secondary_email", type=str, location="json")
    signArgs.add_argument("phone", type=str, location="json")
    signArgs.add_argument("plain_password", type=str, location="json", required=True)
    signArgs.add_argument("validation_code", type=str, location="json", required=True)
    signArgs = signArgs.parse_args()

    insEmail = signArgs["institutional_email"]
    secEmail = signArgs["secondary_email"] if signArgs["secondary_email"] else ""
    phoneNum = signArgs["phone"] if signArgs["phone"] else ""
    plainPass = signArgs["plain_password"]
    valCode = signArgs["validation_code"]
    
    print("\n# Starting user Sign Authentication for " + str(insEmail))
    print("# Verifying data consistency")

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT id, institutional_email, password_hash FROM user_account "
        "   WHERE institutional_email = %s; ",
        [(insEmail)])
    except Exception as e:
      print("# Database searching error:")
      print(str(e))
      return "Erro na base de dados", 409

    if queryRes == None:
      abort(404, "Email institucional não encontrado no sistema!")

    if queryRes[2] != None:
      abort(401, "Email já utilizado!")

    try:
      queryRes = dbGetSingle(
        " SELECT institutional_email, validation_code FROM mail_validation "
        "   WHERE institutional_email = %s AND validation_code = %s; ",
        [insEmail, valCode])
    except Exception as e:
      print("# Database searching error:")
      print(str(e))
      return "Erro na base de dados", 409

    if queryRes == None or len(queryRes) != 2:
      abort(401, "Chave de cadastro inválida para este email!")
      
    print("# Registering user")

    hashPass, saltPass = getHashPassword(plainPass)
    datetimeNow = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
      dbExecute(
        " UPDATE user_account SET "
        "   secondary_email = %s, "
        "   phone = %s, "
        "   password_hash = %s, "
        "   password_salt = %s, "
        "   creation_datetime = %s "
        "   WHERE institutional_email = %s ", 
        [secEmail, phoneNum, hashPass, saltPass, datetimeNow, insEmail])
    except Exception as e:
      print("# Database insertion error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# User sign complete!")
    return "", 201
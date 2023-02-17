from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import werkzeug

from utils.dbUtils import *
import os.path
import random
import string

def verifyAndCreateDirs(userName, docType):
  
  path = './Document'
  if(not os.path.isdir(path)):
    os.makedirs(path)
  
  path = path + '/' + userName
  if(not os.path.isdir(path)):
    os.makedirs(path)

  path = path + '/' + docType
  if(not os.path.isdir(path)):
    os.makedirs(path)
  
  return path

class ReceiveFile(Resource):
    
  def post(self):
    
    upload_args = reqparse.RequestParser()
    upload_args.add_argument('file', location='files', type=werkzeug.datastructures.FileStorage)
    upload_args.add_argument('file_user_name', location='form', type=str)
    upload_args.add_argument('file_dir_name', location='form', type=str)
    upload_args.add_argument('user_mail_ins', location='form', type=str)
    upload_args = upload_args.parse_args()

    file = upload_args['file']
    fileUserName = upload_args['file_user_name']
    fileDirName = upload_args['file_dir_name']
    userMailIns = upload_args['user_mail_ins']

    print('# Starting download to server request for ' + str(userMailIns))

    if file:
      
      print('# Checking file data')
      # calculates file size without saving file in disk
      file.seek(0, os.SEEK_END)
      fileSize = round((file.tell()/1024/1024), 2)
      file.seek(0, os.SEEK_SET)

      if '.pdf' not in file.filename:
        return 'Error: File must be an pdf', 400

      if fileSize > 10.0:
        return 'Error: File size must not exceed 10MB', 400

      r = None
      sqlScrypt = ' SELECT id, email_ins FROM conta_usuario ' \
        ' WHERE email_ins = %s; '
      try:
        r = dbGetSingle(sqlScrypt, [(userMailIns)])
      except Exception as e:
        print('# Database searching error:')
        print(str(e))
        return 'Erro na base de dados', 409
      
      if r == None:
        abort(404, 'Email institucional não encontrado no sistema!')
      userId = r[0]

      # calculates file path hash
      print('# Saving file data')
      path = verifyAndCreateDirs(fileUserName, fileDirName)

      pathIsFile = True
      while pathIsFile:

        hashPdfCode = ''.join(
          random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
          for _ in range(10)) + '.pdf'

        tmpPath = path + '/' + hashPdfCode
        pathIsFile = os.path.isfile(tmpPath)
      
      path = tmpPath

      sqlScrypt = ' INSERT INTO anexo (hash_anexo, id_usuario) VALUES ' \
	      ' (%s, %s); '
      try:
        dbExecute(sqlScrypt, [path.replace('/','_').replace('._Document_',''), userId])
      except Exception as e:
        print('# Database insertion error:')
        print(str(e))
        return 'Erro na base de dados', 409
      
      file.save(tmpPath)
      print('# File saved')
      return 'ok', 200
    
    return 'Error: Missing request file', 400
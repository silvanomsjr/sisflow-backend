from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import werkzeug

from utils.dbUtils import *
from utils.sistemConfig import getUserFilesPath
import random
import string

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
      
      # check file data without saving file in disk
      print('# Checking file data')
      
      file.seek(0, os.SEEK_END)
      fileSize = round((file.tell()/1024/1024), 2)
      file.seek(0, os.SEEK_SET)

      if '.pdf' not in file.filename:
        return 'Erro: O arquivo deve estar no formato pdf', 400

      if fileSize > 10.0:
        return 'Erro: O tamanho do arquivo nao pode ultrapassar 10MB', 400

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
      print('# Generating file hash name')

      userFilePath = None
      userFileName = None
      pathIsFile = True
      while pathIsFile:

        hashPdfCode = ''.join(
          random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
          for _ in range(10)) + '.pdf'

        userFileName = fileUserName + '_' + fileDirName + '_' + hashPdfCode
        userFilePath = getUserFilesPath(userFileName)
        pathIsFile = userFilePath.is_file()

      try:
        dbExecute(
          ' INSERT INTO anexo (hash_anexo, id_usuario) VALUES ' \
	        ' (%s, %s); ',
          [userFileName, userId])
      except Exception as e:
        print('# Database insertion error:')
        print(str(e))
        return 'Erro na base de dados', 409
      
      print('# Saving file: ' + userFileName)

      try:
        file.save(userFilePath)
      except Exception as e:
        print('# Sistem directory insertion error:')
        print(str(e))
        return 'Erro no servidor', 409

      print('# File saved')
      return 'ok', 200
    
    return 'Error: Missing request file', 400
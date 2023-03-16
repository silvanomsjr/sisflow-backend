from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse
import werkzeug

from utils.dbUtils import *
from utils.sistemConfig import getUserFilesPath
import random
import string

class ReceiveFile(Resource):
    
  def post(self):
    
    uploadArgs = reqparse.RequestParser()
    uploadArgs.add_argument('file', location='files', type=werkzeug.datastructures.FileStorage)
    uploadArgs.add_argument('file_user_name', location='form', type=str)
    uploadArgs.add_argument('file_dir_name', location='form', type=str)
    uploadArgs.add_argument('user_mail_ins', location='form', type=str)
    uploadArgs = uploadArgs.parse_args()

    file = uploadArgs['file']
    fileUserName = uploadArgs['file_user_name']
    fileDirName = uploadArgs['file_dir_name']
    userMailIns = uploadArgs['user_mail_ins']

    print('# Starting upload request for ' + str(userMailIns))

    if not file:
      return 'Error: Missing request file', 400
      
    # check file data without saving file in disk
    print('# Checking file data')
    
    file.seek(0, os.SEEK_END)
    fileSize = round((file.tell()/1024/1024), 2)
    file.seek(0, os.SEEK_SET)

    if '.pdf' not in file.filename:
      return 'Erro: O arquivo deve estar no formato pdf', 400

    if fileSize > 10.0:
      return 'Erro: O tamanho do arquivo nao pode ultrapassar 10MB', 400

    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT id, email_ins FROM conta_usuario WHERE email_ins = %s; ',
        [(userMailIns)])
    except Exception as e:
      print('# Database searching error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    if queryRes == None:
      abort(404, 'Email institucional não encontrado no sistema!')
    userId = queryRes[0]

    # calculates file path hash
    print('# Generating file hash name')

    filePath = None
    fileName = None
    pathIsFile = True
    while pathIsFile:

      hashPdfCode = ''.join(
        random.choice(string.ascii_letters if random.uniform(0, 1) > 0.25 else string.digits) 
        for _ in range(10)) + '.pdf'

      fileName = fileUserName + '_' + fileDirName + '_' + hashPdfCode
      filePath = getUserFilesPath(fileName)
      pathIsFile = filePath.is_file()

    try:
      dbExecute(
        ' INSERT INTO anexo (hash_anexo) VALUES (%s); ',
        [fileName], False)

      queryRes = dbGetSingle(
        ' SELECT id FROM anexo WHERE hash_anexo = %s; ',
        [(fileName)], False)
      
      if not queryRes or len(queryRes) != 1:
        raise Exception()
      
      fileId = queryRes[0]

      dbExecute(
        ' INSERT INTO possui_anexo (id_usuario, id_anexo) VALUES (%s, %s); ',
        [userId, fileId], False)
      
    except Exception as e:
      dbRollback()
      print('# Database error:')
      print(str(e))
      return 'Erro na base de dados', 409
    
    dbCommit()
    print('# Saving file: ' + fileName)

    try:
      file.save(filePath)
    except Exception as e:
      print('# Sistem directory insertion error:')
      print(str(e))
      return 'Erro no servidor', 409

    print('# File saved')
    return { 'user_file_name' : fileName }, 200
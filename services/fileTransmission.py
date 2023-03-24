from flask import Flask, abort, request, send_file
from flask_restful import Resource, Api, reqparse
import werkzeug

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.sistemConfig import getUserFilesPath
import random
import string

class FileTransmission(Resource):

  # get to download
  def get(self):

    downloadArgs = reqparse.RequestParser()
    downloadArgs.add_argument("bearer", location="args", type=str, help="Bearer token in url, used to authentication, required!", required=True)
    downloadArgs.add_argument("file_name", location="args", type=str, required=True)
    downloadArgs = downloadArgs.parse_args()

    # verify jwt and its signature correctness
    downloadArgs["Authorization"] = "Bearer " + downloadArgs["bearer"]
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(downloadArgs)
    if not isTokenValid:
      abort(401, errorMsg)

    userId = tokenData["user_id"]
    fileName = downloadArgs["file_name"]

    # checks if file exists
    fileFound = False
    try:
      if dbGetSingle(
          " SELECT hash_name FROM attachment WHERE hash_name = %s; ",
          [fileName]):
        fileFound = True
    except Exception as e:
      print("# Database reading error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    if not fileFound:
      return "Arquivo não encontrado na base de dados!", 404

    # checks user acess
    fileAcessAllowed = False

    if "ADM" in tokenData["profile_acronyms"] or "COO" in tokenData["profile_acronyms"]:
      fileAcessAllowed = True
    else:
      try:
        if dbGetSingle(
            " SELECT at.hash_name "
            "   FROM attachment AS at JOIN user_has_attachment AS uhat ON at.id = uhat.attachment_id "
            "   WHERE uhat.user_id = %s AND at.hash_name = %s; ",
            [userId, fileName]):
          fileAcessAllowed = True
      except Exception as e:
        print("# Database reading error:")
        print(str(e))
        return "Erro na base de dados", 409

    if not fileAcessAllowed:
      return "Acesso ao arquivo não permitido!", 401

    # removes hash part of name if possible
    simpleFileName = "download.pdf"

    findOneUnd = fileName.find('_')
    if findOneUnd != -1:

      findTwoUnd = fileName.find('_', findOneUnd+1)
      if findTwoUnd != -1:
        simpleFileName = fileName[0:findTwoUnd] + ".pdf"

    filePath = getUserFilesPath(fileName)

    if not filePath.is_file():
      return "Arquivo não encontrado na pasta do usuário!", 404

    return send_file(filePath, as_attachment = True, download_name = simpleFileName)
  
  # post to upload
  def post(self):
    
    uploadArgs = reqparse.RequestParser()
    uploadArgs.add_argument("file", location="files", type=werkzeug.datastructures.FileStorage)
    uploadArgs.add_argument("file_user_name", location="form", type=str)
    uploadArgs.add_argument("file_content_name", location="form", type=str)
    uploadArgs.add_argument("user_institutional_email", location="form", type=str)
    uploadArgs = uploadArgs.parse_args()

    file = uploadArgs["file"]
    fileUserName = uploadArgs["file_user_name"]
    fileContentName = uploadArgs["file_content_name"]
    userInsEmail = uploadArgs["user_institutional_email"]

    print("# Starting upload request for " + str(userInsEmail))

    if not file:
      return "Error: Missing request file", 400
      
    # check file data without saving file in disk
    print("# Checking file data")
    
    file.seek(0, os.SEEK_END)
    fileSize = round((file.tell()/1024/1024), 2)
    file.seek(0, os.SEEK_SET)

    if ".pdf" not in file.filename:
      return "Erro: O arquivo deve estar no formato pdf", 400

    if fileSize > 10.0:
      return "Erro: O tamanho do arquivo nao pode ultrapassar 10MB", 400

    queryRes = None
    try:
      queryRes = dbGetSingle(
        " SELECT id, institutional_email FROM user_account WHERE institutional_email = %s; ",
        [(userInsEmail)])
    except Exception as e:
      print("# Database searching error:")
      print(str(e))
      return "Erro na base de dados", 409
    
    if queryRes == None:
      abort(404, "Email institucional não encontrado no sistema!")
    userId = queryRes[0]

    # calculates file path hash
    print("# Generating file hash name")

    filePath = None
    fileName = None
    pathIsFile = True
    while pathIsFile:

      hashPdfCode = ''.join(
        random.choice(string.ascii_letters if random.uniform(0, 1) > 0.25 else string.digits) 
        for _ in range(10)) + ".pdf"

      fileName = fileUserName + '_' + fileContentName + '_' + hashPdfCode
      filePath = getUserFilesPath(fileName)
      pathIsFile = filePath.is_file()

    try:
      dbExecute(
        " INSERT INTO attachment (hash_name) VALUES (%s); ",
        [fileName], False)

      queryRes = dbGetSingle(
        " SELECT id FROM attachment WHERE hash_name = %s; ",
        [(fileName)], False)
      
      if not queryRes or len(queryRes) != 1:
        raise Exception()
      
      fileId = queryRes[0]

      dbExecute(
        " INSERT INTO user_has_attachment (user_id, attachment_id) VALUES (%s, %s); ",
        [userId, fileId], False)
      
    except Exception as e:
      dbRollback()
      print("# Database error:")
      print(str(e))
      return "Erro na base de dados", 409

    print("# Saving file: " + fileName)

    try:
      file.save(filePath)
    except Exception as e:
      dbRollback()
      print("# Sistem directory insertion error:")
      print(str(e))
      return "Erro no servidor", 409
    
    # only commits after saving in db and in server
    dbCommit()

    print("# File saved")
    return { "user_file_name" : fileName }, 200
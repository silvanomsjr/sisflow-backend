"""
Define the REST HTTP verbs relative to the file transmition with download and upload
"""

from flask import send_file
from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
import os
import random
import string
import werkzeug
from repositories import AttachmentRepository, UserRepository
from util import parse_params, parse_params_with_user_authentication, sysconf, syssecurity

logging = logging.getLogger(__name__)

class FileTransmitionResource(Resource):
    """ HTTP methods relative to the file transmition """

    @staticmethod
    @parse_params(
        Argument("bearer", location="args", type=str, required=True, help="Bearer token in url, used to authentication, required!"),
        Argument("file_name", location="args", type=str, required=True, help="Required. File name to download."),
    )
    def get(bearer, file_name):
        """ Get to download a file given its name """

        # checks if user is allowed and get jwt data
        acess_allowed, error_message, jwt_data = syssecurity.is_auth_token_valid(bearer)
        if not acess_allowed:
            return error_message, 401

        # checks if file exists
        file_attachment = AttachmentRepository.read_attachment(file_name)
        if not file_attachment:
            return "Arquivo não encontrado na base de dados", 404
        
        # incomplete: check user access, need to allow advisor access to student files
        """
        # if the profile is admin or coo, the access is allowed
        if "ADM" not in jwt_data["profile_acronyms"] and "COO" not in jwt_data["profile_acronyms"]:
            
            # if not, user access is verified
            file_attachment = AttachmentRepository.read_attachment(file_name, jwt_data["user_id"])
            if not file_attachment:
                return "Acesso ao arquivo não permitido", 401
        """

        # removes hash part of name if possible
        simple_file_name = "download.pdf"

        # the file hash name is: fileusername_filecontentname_hashpdfcode
        find_one_und = file_name.find('_')
        if find_one_und != -1:

            find_two_und = file_name.find('_', find_one_und+1)
            if find_two_und != -1:
                simple_file_name = file_name[0:find_two_und] + ".pdf"

        file_path = sysconf.get_user_file_path(file_name)

        if not file_path.is_file():
            return "Arquivo não encontrado na pasta do usuário", 404
        
        print(simple_file_name)
        return send_file(file_path, as_attachment=True, download_name=simple_file_name)

    @staticmethod
    @parse_params_with_user_authentication(reqparse_arguments=[
        Argument("file", location="files", type=werkzeug.datastructures.FileStorage, required=True, help="Required. File data."),
        Argument("file_user_name", location="form", type=str, help="User name to create hash name."),
        Argument("file_content_name", location="form", type=str, help="File content name to create hash name."),
        Argument("user_institutional_email", location="form", type=str, help="User institutional email.")
    ])
    def post(jwt_data, file, file_user_name, file_content_name, user_institutional_email):
        """ Post to upload a file to the server """

        # check file data without saving file in disk
        file.seek(0, os.SEEK_END)
        fileSize = round((file.tell()/1024/1024), 2)
        file.seek(0, os.SEEK_SET)

        if ".pdf" not in file.filename:
            return "Erro: O arquivo deve estar no formato pdf", 400

        if fileSize > 10.0:
            return "Erro: O tamanho do arquivo nao pode ultrapassar 10MB", 400
        
        # check user email
        user = UserRepository.read_user(institutional_email=user_institutional_email)
        if not user:
            return "Email institucional não encontrado no sistema", 404
        
        # calculates file path hash
        file_path = None
        file_name = None
        path_is_file = True

        # stops when the path is not a file, avoids overwriting old files
        while path_is_file:

            # creates a code with random letters and digits
            hash_pdf_code = ''.join(
                random.choice(string.ascii_letters if random.uniform(0, 1) > 0.25 else string.digits) 
                for _ in range(10)) + ".pdf"

            # the hash name: fileusername_filecontentname_hashpdfcode
            file_name = file_user_name + '_' + file_content_name + '_' + hash_pdf_code
            file_path = sysconf.get_user_file_path(file_name)
            path_is_file = file_path.is_file()
        
        # creates the attachment
        attachment = AttachmentRepository.create_attachment(file_name)
        if not attachment:
            return "Erro ao salvar os dados do download na base de dados", 500
        
        # associates with its user
        # incomplete: need to associate to the advisor of the solicitation
        user_has_attachment = UserRepository.create_user_has_attachment(user.id, attachment.id)
        if not user_has_attachment:
            return "Erro ao salvar os dados do usuário do download na base de dados", 500
        
        # saves the file in server
        try:
            file.save(file_path)
        except Exception as e:
            return "Erro ao salvar o arquivo no servidor", 500

        return { "user_file_name" : file_name }, 200
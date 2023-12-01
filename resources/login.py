"""
Define the REST HTTP verbs for user login
"""

from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
from base64 import b64decode
from repositories import UserRepository, UserProfileTokenRepository
from util import parse_params
from util import syssecurity

logging = logging.getLogger(__name__)

class LoginResource(Resource):
    """ HTTP methods relative to the user login """
  
    @staticmethod
    @parse_params(
        Argument("Authorization", location="headers", type=str, required=True, help="Required. Email and hash password of the user, used to authentication.")
    )
    def post(Authorization):

        # parse authorization fields
        login_institutional_email, login_plain_password = b64decode(Authorization.replace("Basic ", "")).decode("utf-8").split(':', 1)
        logging.info(f"Starting Login authentication for {login_institutional_email}")

        db_user = UserRepository.read_user(institutional_email=login_institutional_email)

        # checks for user data in db
        if db_user == None:
            logging.info(f"A user authentication failed, for {login_institutional_email}, no user found")
            return "Usuário não encontrado no sistema", 401

        if db_user.password_hash == None:
            logging.info(f"A user authentication failed, for {login_institutional_email}, not signed")
            return "Usuário não cadastrado", 401

        # verifies password
        login_password_hash, _ = syssecurity.get_password_hash(login_plain_password, db_user.password_salt)

        if login_password_hash != db_user.password_hash:
            logging.info(f"A user authentication failed, for {login_institutional_email}, incorrect password")
            return "Senha incorreta", 401

        # creates resoponse object with user profiles to make the jwt
        user_profile_token = UserProfileTokenRepository.read_user_profile_token(db_user.id)

        # creates the jwt
        jwt_token = syssecurity.jwt_encode(user_profile_token)

        logging.info(f"User authentication for {login_institutional_email} done")
        return jwt_token, 200
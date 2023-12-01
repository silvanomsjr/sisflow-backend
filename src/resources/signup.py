"""
Define the REST HTTP verbs for user signup
"""
from flask_restful import Resource
from flask_restful.reqparse import Argument

import logging
import os
import random
import string
from datetime import datetime
from repositories import UserRepository, MailValidationRepository
from util import parse_params, syssecurity, syssmtpserver

logging = logging.getLogger(__name__)

class SignupResource(Resource):
    """ HTTP methods relative to user signup """

    @staticmethod
    @parse_params(
        Argument("institutional_email", location="json", type=str, required=True, help="Required. Institutional email of the user")
    )
    def post(institutional_email):
        """ Post to create and send mail with signup code """

        logging.info(f"Starting user Get Authentication Code for {institutional_email}")

        # checks for user data in db
        db_user = UserRepository.read_user(institutional_email=institutional_email)

        if db_user == None:
            logging.info(f"Error, user {institutional_email} not found")
            return "Email institucional não encontrado no sistema", 404

        if db_user.password_hash != None:
            logging.info(f"Error, user {institutional_email} already registered")
            return "Email já utilizado", 401

        # creates a random validation code
        validation_code = "".join(
            random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
            for _ in range(10))
        logging.info(f"Validation code for {institutional_email} created")

        # checks for older mail validation and updates or inserts the new code
        if MailValidationRepository.read_mail_validation(institutional_email=institutional_email) != None:
            MailValidationRepository.update_mail_validation(institutional_email, validation_code)
        else:
            MailValidationRepository.create_mail_validation(institutional_email, validation_code)

        # creates e-mail inner_html with tokens and send
        acess_token = syssecurity.jwt_encode({"institutional_email": institutional_email, "validation_code": validation_code})
        acess_url = os.getenv("FRONT_URL") + "sign?acess_token=" + acess_token
        inner_mail_html = f'''
        <p>Este é seu código de cadastro: {validation_code} </p>
        <p>Você também pode continuar o cadastro ao clicar neste <a href="{acess_url}">link</a></p>
        '''
        syssmtpserver.add_email(institutional_email, "Confirmação de cadastro no SisFlow", inner_mail_html)

        logging.info(f"Mail sended to {institutional_email} with signup code")
        return "", 200
  
    @staticmethod
    @parse_params(
        Argument("acess_token", location="args", type=str, help="Access token for user signup"),
        Argument("institutional_email", location="args", type=str, help="User institutional email"),
        Argument("validation_code", location="args", type=str, help="Validation code for user signup")
    )
    def get(acess_token=None, institutional_email=None, validation_code=None):
        """ Get to verify the validation code """

        logging.info(f"Starting user get verification code")

        # checks if the args are correct for either way of sending the validation code
        if not acess_token and (not institutional_email or not validation_code):
            logging.info(f"Missing acess_token token or institutional_email and validation_code")
            return "Codigo de acesso inválido", 400

        # parse the token if needed
        if acess_token:
            acess_token_data = None
            try:
                acess_token_data = syssecurity.jwt_decode(acess_token)
            except Exception as e:
                logging.info(f"JWT decoding error:", e)
                return "Codigo de acesso inválido", 401

            institutional_email = acess_token_data["institutional_email"]
            validation_code = acess_token_data["validation_code"]

        logging.info(f"Testing validation code for {institutional_email}")

        # returns if the validation code is valid
        if MailValidationRepository.read_mail_validation(institutional_email=institutional_email, validation_code=validation_code) == None:
            logging.info(f"Invalid validation code for {institutional_email}")
            return False, 401
        else:
            logging.info(f"Valid validation code for {institutional_email}")
            return {"institutional_email": institutional_email , "validation_code" : validation_code}, 200

    @staticmethod
    @parse_params(
        Argument("validation_code", location="json", type=str, required=True, help="Required. Validation code for signup"),
        Argument("institutional_email", location="json", type=str, required=True, help="Required. User institutional email"),
        Argument("plain_password", location="json", type=str, required=True, help="Required. User plain password"),
        Argument("secondary_email", location="json", type=str, help="User secundary email"),
        Argument("phone", location="json", type=str, help="User phone")
    )
    def put(validation_code, institutional_email, plain_password, secondary_email=None, phone=None):
        """ Put with user data fields and the validation code for the signup """
        
        logging.info(f"Starting user put signup for {institutional_email}")

        # checks for user data in db
        db_user = UserRepository.read_user(institutional_email=institutional_email)

        if db_user == None:
            logging.info(f"Error, user {institutional_email} not found")
            return "Email institucional não encontrado no sistema", 404

        if db_user.password_hash != None:
            logging.info(f"Error, user {institutional_email} already registered")
            return "Email já utilizado", 401

        # checks if the validation code is invalid
        if MailValidationRepository.read_mail_validation(institutional_email=institutional_email, validation_code=validation_code) == None:
            logging.info(f"Invalid validation code for {institutional_email}")
            return "Chave de cadastro inválida para este email", 401

        # register the user
        password_hash, password_salt = syssecurity.get_password_hash(plain_password)
        datetime_now = datetime.now()

        UserRepository.update_user(
            institutional_email=institutional_email,
            secondary_email=secondary_email,
            phone=phone,
            password_hash=password_hash,
            password_salt=password_salt,
            creation_datetime=datetime_now
        )

        logging.info(f"User signup complete for {institutional_email}")
        return "", 201
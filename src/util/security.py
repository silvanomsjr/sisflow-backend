"""
Security

Handles security topics
"""
import hashlib
import jwt
import logging
import random
import string

from Crypto.PublicKey import RSA

logging = logging.getLogger(__name__)

class Security:
    
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def load_keys(self, private_key_Path, public_key_Path):

        # when first executed generate key pair
        if not private_key_Path.is_file() or not public_key_Path.is_file():
            self.__generate_keys(private_key_Path, public_key_Path)
        
        self.private_key = open(private_key_Path).read()
        self.public_key = open(public_key_Path).read()

        logging.info(f'Application key pair loaded for JWT authentication')
    
    def __generate_keys(self, private_key_Path, public_key_Path):

        # generate private key file
        pvk = RSA.generate(2048)
        pvk_str = pvk.exportKey()
        with open(private_key_Path, 'w') as pvk_file:
            print("{}".format(pvk_str.decode()), file=pvk_file)

        # generate public key file
        pbk = pvk.publickey()
        pbk_str = pbk.exportKey()
        with open(public_key_Path, 'w') as pbk_file:
            print("{}".format(pbk_str.decode()), file=pbk_file)
        
        logging.info(f'Application key pair generated for JWT authentication')
    
    # Encode a json data to creates a jwt token with signature
    def jwt_encode(self, token_json_data):
        token_jwt = jwt.encode(token_json_data, self.private_key, algorithm="RS256")
        return token_jwt

    # Decode a jwt token verifying its signature
    def jwt_decode(self, token_jwt):
        jwt_data = jwt.decode(token_jwt, self.public_key, algorithms=["RS256"])
        return jwt_data
    
    # Verify if an jwt token given in request bearer is valid based on jwt signature and its profile
    def is_auth_token_valid(self, bearer_token, allowed_profiles_acronyms=None):

        token_jwt = bearer_token.replace("Bearer ", "")

        jwt_data = None
        try:
            jwt_data = self.jwt_decode(token_jwt)
        except:
            return False, "Falha ao autenticar, token de autenticação inválido", None
        
        if not jwt_data:
            return False, "Token inválido", None

        if allowed_profiles_acronyms:
            token_profiles = jwt_data["profiles"]

            acess_allowed = False

            for profile in token_profiles:
                if profile["profile_acronym"] in allowed_profiles_acronyms:
                    acess_allowed = True
            
            if not acess_allowed:
                return False, "tipo de usuário incorreto", None

        return True, "", jwt_data

    # hashes password with random or given salt using sha256
    @staticmethod
    def get_password_hash(password, salt=None):

        pass_salt = None
        if salt:
            pass_salt = salt
        else:
            pass_salt = ''.join(
                random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
                for _ in range(16)
            )

        pass_bytes = bytes(password + pass_salt, "utf-8")
        hash_pass = hashlib.sha256(pass_bytes).hexdigest()

        return hash_pass, pass_salt
import hashlib
import jwt
from Crypto.PublicKey import RSA

from utils.sistemConfig import getKeysFilePath
import random
import string

private_key = None
public_key = None

# load or create and load keys
def loadGenerateKeys():

  global private_key, public_key

  privatek_path = getKeysFilePath('private-key.pem')
  publick_path = getKeysFilePath('public-key.pem')

  # when first executed generate key pair
  if not privatek_path.is_file() or not publick_path.is_file():
    
    # private key
    pvk = RSA.generate(2048)
    pvk_str = pvk.exportKey()
    with open(privatek_path, "w") as pvk_file:
      print("{}".format(pvk_str.decode()), file=pvk_file)

    # public key
    pbk = pvk.publickey()
    pbk_str = pbk.exportKey()
    with open(publick_path, "w") as pbk_file:
      print("{}".format(pbk_str.decode()), file=pbk_file)
    
    print('# Private and public keys generated')

  private_key = open(privatek_path).read()
  public_key = open(publick_path).read()

# hashes password with random or given salt using sha256
def getHashPassword(password, salt=None):

  passSalt = None
  if salt:
    passSalt = salt
  else:
    passSalt = ''.join(
      random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
      for _ in range(16))

  passBytes = bytes(password + passSalt, 'utf-8')
  hashPass = hashlib.sha256(passBytes).hexdigest()

  return hashPass, passSalt

# Encode a json data to creates a jwt token with signature
def jwtEncode(token_json_data):

  global private_key

  if not private_key:
    loadGenerateKeys()

  token_jwt = jwt.encode(token_json_data, private_key, algorithm="RS256")
  return token_jwt

# Decode a jwt token verifying its signature
def jwtDecode(token_jwt):

  global public_key

  if not public_key:
    loadGenerateKeys()
    
  token_data = jwt.decode(token_jwt, public_key, algorithms=["RS256"])
  return token_data
  
# Verify if an token given in request bearer is valid based on jwt signature
def isAuthTokenValid(args, user_types_required=None):

  token_jwt = args['Authorization'].replace('Bearer ', '')

  token_data = None
  try:
    token_data = jwtDecode(token_jwt)
  except:
    return False, 'Falha ao decifrar o token, token inválido!', None
  
  if not token_data:
    return False, 'Token inválido!', None

  if user_types_required:
    token_user_type = token_data['siglas']
    if token_user_type not in user_types_required:
      return False, 'tipo de usuário incorreto!', None

  return True, '', token_data
from pathlib import Path
import jwt
from Crypto.PublicKey import RSA

# when first executed generate key pairs
privatek_path = Path('./secrets/private-key.pem')
publick_path = Path('./secrets/public-key.pem')

if not privatek_path.is_file() or not publick_path.is_file():
  
  # private key
  pvk = RSA.generate(2048)
  pvk_str = pvk.exportKey()
  print(pvk_str)
  with open (privatek_path, "w") as pvk_file:
    print("{}".format(pvk_str.decode()), file=pvk_file)

  # public key
  pbk = pvk.publickey()
  pbk_str = pbk.exportKey()
  print(pbk_str)
  with open (publick_path, "w") as pbk_file:
    print("{}".format(pbk_str.decode()), file=pbk_file)
  
  print('# private and public keys generated')

private_key = open('./secrets/private-key.pem').read()
public_key = open('./secrets/public-key.pem').read()

def jwtEncode(token_json_data):

  token_jwt = jwt.encode(token_json_data, private_key, algorithm="RS256")
  return token_jwt

def jwtDecode(token_jwt):
    
  token_data = jwt.decode(token_jwt, public_key, algorithms=["RS256"])
  return token_data
    
def isAuthTokenValid(args, user_types_required):

  token_jwt = args['Authorization'].replace('Bearer ', '')

  try:
    token_data = jwtDecode(token_jwt)
  except:
    return (False, 'Falha ao decifrar o token, token inválido!')
  
  if not token_data:
    return (False, 'Token inválido!')
  
  token_user_type = token_data['tipo']

  if token_user_type not in user_types_required:
    return (False, 'tipo de usuário incorreto!')

  return (True, '')
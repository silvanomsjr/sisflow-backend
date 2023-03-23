import hashlib
import jwt
from Crypto.PublicKey import RSA

from utils.sistemConfig import getKeysFilePath
import random
import string

privateKey = None
publicKey = None

# load or create and load keys
def loadGenerateKeys():

  global privateKey, publicKey

  privateKPath = getKeysFilePath("private-key.pem")
  publicKPath = getKeysFilePath("public-key.pem")

  # when first executed generate key pair
  if not privateKPath.is_file() or not publicKPath.is_file():
    
    # private key
    pvk = RSA.generate(2048)
    pvkStr = pvk.exportKey()
    with open(privateKPath, 'w') as pvkFile:
      print("{}".format(pvkStr.decode()), file=pvkFile)

    # public key
    pbk = pvk.publickey()
    pbkStr = pbk.exportKey()
    with open(publicKPath, 'w') as pbkFile:
      print("{}".format(pbkStr.decode()), file=pbkFile)
    
    print("# Private and public keys generated")

  privateKey = open(privateKPath).read()
  publicKey = open(publicKPath).read()

# hashes password with random or given salt using sha256
def getHashPassword(password, salt=None):

  passSalt = None
  if salt:
    passSalt = salt
  else:
    passSalt = ''.join(
      random.choice(string.ascii_letters if random.uniform(0,1) > 0.25 else string.digits) 
      for _ in range(16))

  passBytes = bytes(password + passSalt, "utf-8")
  hashPass = hashlib.sha256(passBytes).hexdigest()

  return hashPass, passSalt

# Encode a json data to creates a jwt token with signature
def jwtEncode(tokenJsonData):

  global privateKey

  if not privateKey:
    loadGenerateKeys()

  tokenJwt = jwt.encode(tokenJsonData, privateKey, algorithm="RS256")
  return tokenJwt

# Decode a jwt token verifying its signature
def jwtDecode(tokenJwt):

  global publicKey

  if not publicKey:
    loadGenerateKeys()
    
  token_data = jwt.decode(tokenJwt, publicKey, algorithms=["RS256"])
  return token_data
  
# Verify if an jwt token given in request bearer is valid based on jwt signature and its profile
def isAuthTokenValid(args, allowedProfilesAcronyms=None):

  tokenJwt = args["Authorization"].replace("Bearer ", "")

  tokenData = None
  try:
    tokenData = jwtDecode(tokenJwt)
  except:
    return False, "Falha ao decifrar o token, token inválido!", None
  
  if not tokenData:
    return False, "Token inválido!", None

  if allowedProfilesAcronyms:
    tokenProfiles = tokenData["profiles"]

    acessAllowed = False

    for profile in tokenProfiles:
      if profile["profile_acronym"] in allowedProfilesAcronyms:
        acessAllowed = True
    
    if not acessAllowed:
      return False, "tipo de usuário incorreto!", None

  return True, "", tokenData
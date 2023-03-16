from utils.dbUtils import *
from pathlib import Path
# pathlib paths works both for windows and unix OSs

coordinatorMail = None
keyFilesPath = None
userFilesPath = None

def getMissingEnvironmentVar():

  if not os.getenv('FRONT_BASE_URL'):
    return 'FRONT_BASE_URL'
  
  if not os.getenv('SQL_HOST'):
    return 'SQL_HOST'
  if not os.getenv('SQL_SCHEMA'):
    return 'SQL_SCHEMA'
  if not os.getenv('SQL_PORT'):
    return 'SQL_PORT'
  if not os.getenv('SQL_USER'):
    return 'SQL_USER'
  if not os.getenv('SQL_PASSWORD'):
    return 'SQL_PASSWORD'
  
  if not os.getenv('SMTP_HOST'):
    return 'SMTP_HOST'
  if not os.getenv('SMTP_PORT'):
    return 'SMTP_PORT'
  if not os.getenv('SMTP_LOGIN'):
    return 'SMTP_LOGIN'
  if not os.getenv('SMTP_PASSWORD'):
    return 'SMTP_PASSWORD'

  if not os.getenv('SYS_DEBUG'):
    return 'SYS_DEBUG'

  return None

def sisConfigStart():
  loadMails()
  loadPaths()

def loadMails():

  global coordinatorMail
  
  if not coordinatorMail:

    queryRes = None
    try:
      queryRes = dbGetSingle(
        ' SELECT mail_str ' \
	      '   FROM config AS c JOIN config_mail AS cm ON c.id = cm.config_id ' \
        '   WHERE c.nome = \'coordinator mail\'; ')
      
      if not queryRes:
        raise Exception('No return for sistem root config mail for coordinator ' + str(queryRes))
    
    except Exception as e:
      print('# Database config reading error:')
      print(str(e))
    
    coordinatorMail = queryRes[0]

    print('# Coordinator mail: ' + str(coordinatorMail))

def loadPaths():

  global keyFilesPath, userFilesPath
  
  if not keyFilesPath or not userFilesPath:

    keyFilesPath = None
    userFilesPath = None

    queryRes = []
    try:
      queryRes = dbGetAll(
        ' SELECT nome, path_str ' \
	      '   FROM config AS c JOIN config_path AS cp ON c.id = cp.config_id; ')
      
      if not queryRes:
        raise Exception('No return for sistem root config path query ' + str(queryRes))

      # Set root path for both OSs
      for cpath in queryRes:
        if cpath[0] == 'root path key files':
          keyFilesPath = Path(cpath[1])
        elif cpath[0] == 'root path user files':
          userFilesPath = Path(cpath[1])
      
      if not keyFilesPath or not userFilesPath:
        raise Exception('Missing config paths')
    
    except Exception as e:
      print('# Database config reading error:')
      print(str(e))
    
    # creates paths if not exists
    keyFilesPath.mkdir(parents=True, exist_ok=True)
    userFilesPath.mkdir(parents=True, exist_ok=True)

    print('# Key files path: ' + str(keyFilesPath.resolve()))
    print('# User file storage root path: ' + str(userFilesPath.resolve()))

def getParserSubstring(str):
  
  substrStart = str.find('[[[')
  if substrStart == -1:
    return None
  
  substrEnd = str.find(']]]',substrStart)
  if substrEnd == -1:
    print('# Warning, Error while parsing an string, parser not closed')
    return None

  return str[substrStart:substrEnd+3]

# parses a given string changing text options based on user data
def sistemStrParser(str, userData):

  if not str:
    return None
  
  substrP = getParserSubstring(str)
  while substrP:
    command = substrP.replace('[[[','').replace(']]]','').strip()

    # put user name
    if 'userName' in command:
      str = str.replace(substrP, userData['nome'])

    # gender differences
    if 'ifMale?' in command:
      str = str.replace(substrP, command.replace('ifMale?','').split(':::')[ 0 if userData['sexo'] == 'M' else 1 ])

    # course differences, works only users with student profiles
    if 'ifBCC?' in command:
      if userData['perfil_aluno'] and userData['perfil_aluno']['curso']:
        str = str.replace(substrP, command.replace('ifBCC?','').split(':::')[ 0 if userData['perfil_aluno']['curso'] == 'BCC' else 1 ])
      else:
        str = str.replace(substrP, '')
    
    # avoid loops when not configured correctly
    else:
      str = str.replace(substrP, '')

    substrP = getParserSubstring(str)
  
  return str

def getCoordinatorMail():
  global coordinatorMail
  return coordinatorMail

def getKeysFilePath(keyFileName):
  global keyFilesPath
  return keyFilesPath / keyFileName

def getUserFilesPath(userFileHash):
  global userFilesPath
  return userFilesPath / userFileHash
from utils.dbUtils import *
from pathlib import Path

# pathlib paths works both for windows and unix OSs

keyFilesPath = None
userFilesPath = None

def sisConfigStart():
  loadPaths()

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

def getKeysFilePath(keyFileName):
  global keyFilesPath
  return keyFilesPath / keyFileName

def getUserFilesPath(userFileHash):
  global userFilesPath
  return userFilesPath / userFileHash
import datetime
from pathlib import Path
import os
import requests
import traceback

import utils.dbUtils

# pathlib paths works both for windows and unix OSs

coordinatorEmail = None
coordinatorName = None
keyFilesPath = None
userFilesPath = None
holidayData = None

def getMissingEnvironmentVar():

  if not os.getenv("FRONT_BASE_URL"):
    return "FRONT_BASE_URL"
  
  if not os.getenv("SQL_HOST"):
    return "SQL_HOST"
  if not os.getenv("SQL_SCHEMA"):
    return "SQL_SCHEMA"
  if not os.getenv("SQL_PORT"):
    return "SQL_PORT"
  if not os.getenv("SQL_USER"):
    return "SQL_USER"
  if not os.getenv("SQL_PASSWORD"):
    return "SQL_PASSWORD"
  
  if not os.getenv("SMTP_HOST"):
    return "SMTP_HOST"
  if not os.getenv("SMTP_PORT"):
    return "SMTP_PORT"
  if not os.getenv("SMTP_LOGIN"):
    return "SMTP_LOGIN"
  if not os.getenv("SMTP_PASSWORD"):
    return "SMTP_PASSWORD"

  if not os.getenv("SYS_DEBUG"):
    return "SYS_DEBUG"

  return None

def sisConfigStart():
  loadMails()
  loadPaths()
  loadHolidays()

def loadMails():

  global coordinatorEmail, coordinatorName
  
  if not coordinatorEmail:

    queryRes = None
    try:
      queryRes = utils.dbUtils.dbGetSingle(
        " SELECT mail, mail_name "
	      "   FROM config AS c JOIN config_mail AS cm ON c.id = cm.config_id "
        "   WHERE c.config_name = \'coordinator mail\'; ")
      
      if not queryRes:
        raise Exception("No return for coordinator config email " + str(queryRes))
    
    except Exception as e:
      print("# Database config reading error:")
      print(e)
    
    coordinatorEmail = queryRes["mail"]
    coordinatorName = queryRes["mail_name"]

    print("# Coordinator " + str(coordinatorName) + " email: " + str(coordinatorEmail))

def loadPaths():

  global keyFilesPath, userFilesPath
  
  if not keyFilesPath or not userFilesPath:

    keyFilesPath = None
    userFilesPath = None

    queryRes = []
    try:
      queryRes = utils.dbUtils.dbGetAll(
        " SELECT config_name, system_path "
	      "   FROM config AS c JOIN config_system_path AS csp ON c.id = csp.config_id; ")
      
      if not queryRes:
        raise Exception("No return for sistem root config path query " + str(queryRes))

      # Set root path for both OSs
      for cpath in queryRes:
        if cpath["config_name"] == "root path key files":
          keyFilesPath = Path(cpath["system_path"])
        elif cpath["config_name"] == "root path user files":
          userFilesPath = Path(cpath["system_path"])
      
      if not keyFilesPath or not userFilesPath:
        raise Exception("Missing config paths")
    
    except Exception as e:
      print("# Database config reading error:")
      print(e)
    
    # creates paths if not exists
    keyFilesPath.mkdir(parents=True, exist_ok=True)
    userFilesPath.mkdir(parents=True, exist_ok=True)

    print("# Key files path: " + str(keyFilesPath.resolve()))
    print("# User file storage root path: " + str(userFilesPath.resolve()))

def loadHolidays():

  global holidayData

  actualYear = str(datetime.datetime.today().year)

  queryRes = None
  try:
    queryRes = utils.dbUtils.dbGetSingle(
      " SELECT year FROM config_year WHERE year = %s; ",
      [(actualYear)])
  except Exception as e:
    print("# Database reading error:")
    print(e)
    return "Erro na base de dados", 409

  if not queryRes:
    print("# Loading holidays from external API")
  
    holidaysRes = None
    try:
      holidaysRes = requests.get('https://brasilapi.com.br/api/feriados/v1/' + actualYear).json()
    except Exception as e:
      print("# Error trying to load holidays from external API")
      print(e)
      return "Error reading brasilapi, consider using another holiday api if this error continues"

    # start transaction
    dbObjectIns = utils.dbUtils.dbStartTransactionObj()
    try:
      utils.dbUtils.dbExecute(
        " INSERT INTO config (config_name) VALUES (%s); ",
        [(str("year " + actualYear))], True, dbObjectIns)

      configQuery = utils.dbUtils.dbGetSingle(
        " SELECT id FROM config WHERE config_name = %s; ",
        [(str("year " + actualYear))], True, dbObjectIns)

      if not configQuery:
        raise Exception(" No configId return for inserted actual year")

      utils.dbUtils.dbExecute(
        " INSERT INTO config_year (config_id, year) VALUES (%s, %s); ",
        [configQuery["id"], actualYear], True, dbObjectIns)
      
      for holiday in holidaysRes:
        utils.dbUtils.dbExecute(
          " INSERT INTO config_year_holiday (year, get_by, holiday_name, holiday_date) VALUES "
          "   (%s, 'API', %s, %s); ",
          [actualYear, holiday["name"], holiday["date"]], True, dbObjectIns)
    except Exception as e:
      utils.dbUtils.dbRollback(dbObjectIns)
      print("# Database reading error:")
      print(e)
      return "Erro na base de dados", 409
    # ends transaction
    utils.dbUtils.dbCommit(dbObjectIns)

  try:
    holidayData = utils.dbUtils.dbGetAll(
      " SELECT year, get_by, holiday_name, holiday_date FROM config_year_holiday WHERE year = %s; ",
      [(actualYear)])
  except Exception as e:
    print("# Database reading error:")
    print(e)
    return "Erro na base de dados", 409
  
  print("# Holidays configurated")
    
def getCoordinatorEmail():
  global coordinatorEmail
  return coordinatorEmail

def getCoordinatorName():
  global coordinatorName
  return coordinatorName

def getKeysFilePath(keyFileName):
  global keyFilesPath
  return keyFilesPath / keyFileName

def getUserFilesPath(userFileHash):
  global userFilesPath
  return userFilesPath / userFileHash

def getHolidayData():
  global holidayData
  return holidayData
import mysql.connector
import os
import time

# db variables
myDB = None
myCursor = None

# used to refresh db connection
connTimeOutMin = 10
lastRequestTime = None

def dbStart():

  global lastRequestTime, myDB, myCursor

  if not myDB == None and not myDB.is_connected():
    return

  myDB = mysql.connector.connect(
    host = os.getenv('SQL_HOST'),
    port = os.getenv('SQL_PORT'),
    user = os.getenv('SQL_USER'),
    passwd = os.getenv('SQL_PASSWORD'),
    auth_plugin='mysql_native_password')

  if myDB:
    print('# Connection to database successfull')
  else:
    print('# Connection to database failed')
    return

  myCursor = myDB.cursor(buffered=True)
  myCursor.execute('show databases')

  schemaFound = False
  for db in myCursor:
    if os.getenv('SQL_SCHEMA') == db[0]:
      schemaFound = True
      break

  if not schemaFound:
    print('# Schema ' + str(os.getenv('SQL_SCHEMA')) + ' not found! creating schema and tables')
    dbCreate()
    print('# Schema ' + str(os.getenv('SQL_SCHEMA')) + ' and tables created')
  else:
    print('# Schema ' + str(os.getenv('SQL_SCHEMA')) + ' is in database')

  myDB = mysql.connector.connect(
    host = os.getenv('SQL_HOST'),
    port = os.getenv('SQL_PORT'),
    user = os.getenv('SQL_USER'),
    passwd = os.getenv('SQL_PASSWORD'),
    database = os.getenv('SQL_SCHEMA'),
    auth_plugin = 'mysql_native_password')

  myCursor = myDB.cursor(buffered=True)

def isConnectedToDb():

  global connTimeOutMin, lastRequestTime, myDB, myCursor

  if myDB is None or myCursor is None or not myDB.is_connected():
    return False
  
  # if the last time a request runs plus timestamp is less than actual time refresh connection if necessary
  actualTime = time.time()
  if not lastRequestTime or (lastRequestTime+connTimeOutMin*60 < actualTime):
    try:
      dbGetSingle('SELECT 1;')
    except Exception as e:
      return False
      
  lastRequestTime = actualTime
  return True

def getSqlScrypt(name):

  textFile = open('./sql/' + name + '.sql', 'r')
  strFile = textFile.read()
  textFile.close()

  return strFile

def dbRollback():

  global myDB, myCursor

  if not isConnectedToDb():
    dbStart()
  
  myDB.rollback()

def dbCommit():

  global myDB, myCursor

  if not isConnectedToDb():
    dbStart()

  myDB.commit()

def dbExecute(sqlScrypt, values=None, commit=True):

  global myDB, myCursor

  if not isConnectedToDb():
    dbStart()
      
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)
  
  if(commit):
    print('# Operation Commited')
    myDB.commit()

def dbExecuteMany(sqlScrypt, values=None, commit=True):

  global myDB, myCursor

  if not isConnectedToDb():
    dbStart()
  
  if values != None:
    myCursor.executemany(sqlScrypt, values)
  else:
    myCursor.executemany(sqlScrypt)
  
  if(commit):
    print('# Operation Commited')
    myDB.commit()

def dbGetSingle(sqlScrypt, values=None, commitToUpdate=True):

  global myDB, myCursor

  if not isConnectedToDb():
    dbStart()
  
  if(commitToUpdate):
    myDB.commit()
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchone()

def dbGetAll(sqlScrypt, values=None, commitToUpdate=True):

  global myDB, myCursor

  if not isConnectedToDb():
    dbStart()

  if(commitToUpdate):
    myDB.commit()
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchall()

def dbCreate():

  global myDB, myCursor

  if myDB is None:
    dbStart()

  myCursor = myDB.cursor(buffered=True)
  myCursor.execute('create schema ' + str(os.getenv('SQL_SCHEMA')))

  myDB = mysql.connector.connect(
    host = os.getenv('SQL_HOST'),
    port = os.getenv('SQL_PORT'),
    user = os.getenv('SQL_USER'),
    passwd = os.getenv('SQL_PASSWORD'),
    database = os.getenv('SQL_SCHEMA'),
    auth_plugin = 'mysql_native_password')

  # opens and close cursor to avoid sync problens
  myCursor = myDB.cursor(buffered=True)
  myCursor.execute(getSqlScrypt('sisges_create'))
  myCursor.close()
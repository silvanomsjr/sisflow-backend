import mysql.connector
import os

myDB = None
myCursor = None

def dbStart():

  global myDB, myCursor

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

  myCursor = myDB.cursor()
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

  myCursor = myDB.cursor()

def getSqlScrypt(name):

  textFile = open('./sql/' + name + '.sql', 'r')
  strFile = textFile.read()
  textFile.close()

  return strFile

def dbRollback():

  global myDB, myCursor

  if myDB is None or myCursor is None or not myDB.is_connected():
    dbStart()
  
  myDB.rollback()

def dbCommit():

  global myDB, myCursor

  if myDB is None or myCursor is None or not myDB.is_connected():
    dbStart()

  myDB.commit()

def dbExecute(sqlScrypt, values=None, commit=True):

  global myDB, myCursor

  if myDB is None or myCursor is None or not myDB.is_connected():
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

  if myDB is None or myCursor is None or not myDB.is_connected():
    dbStart()
  
  if values != None:
    myCursor.executemany(sqlScrypt, values)
  else:
    myCursor.executemany(sqlScrypt)
  
  if(commit):
    print('# Operation Commited')
    myDB.commit()

def dbGetSingle(sqlScrypt, values=None):

  global myDB, myCursor

  if myDB is None or myCursor is None or not myDB.is_connected():
    dbStart()
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchone()

def dbGetAll(sqlScrypt, values=None):

  global myDB, myCursor

  if myDB is None or myCursor is None or not myDB.is_connected():
    dbStart()
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchall()

def dbCreate():

  global myDB, myCursor

  if myDB is None:
    dbStart()

  myCursor = myDB.cursor()
  myCursor.execute('create schema ' + str(os.getenv('SQL_SCHEMA')))

  myDB = mysql.connector.connect(
    host = os.getenv('SQL_HOST'),
    port = os.getenv('SQL_PORT'),
    user = os.getenv('SQL_USER'),
    passwd = os.getenv('SQL_PASSWORD'),
    database = os.getenv('SQL_SCHEMA'),
    auth_plugin = 'mysql_native_password')

  # opens and close cursor to avoid sync problens
  myCursor = myDB.cursor()
  myCursor.execute(getSqlScrypt('sisges_create'))
  myCursor.close()
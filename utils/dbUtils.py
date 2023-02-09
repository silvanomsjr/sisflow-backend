import mysql.connector

myDB = None
myCursor = None

def dbStart(SQL_HOST, SQL_PORT, SQL_SCHEMA, SQL_USER, SQL_PASSWORD):

  global myDB, myCursor

  if myDB is not None:
    return

  myDB = mysql.connector.connect(host=SQL_HOST, port=SQL_PORT, user=SQL_USER, passwd=SQL_PASSWORD)

  if myDB:
    print('# Connection to database successfull')
  else:
    print('# Connection to database failed')
    return

  myCursor = myDB.cursor()
  myCursor.execute('show databases')

  schemaFound = False
  for db in myCursor:
    if SQL_SCHEMA == db[0]:
      schemaFound = True
      break

  if not schemaFound:
    print('# schema ' + str(SQL_SCHEMA) + ' not found! creating schema and tables')
    dbCreate(SQL_HOST, SQL_PORT, SQL_SCHEMA, SQL_USER, SQL_PASSWORD)
  else:
    print('# schema ' + str(SQL_SCHEMA) + ' is in database')
    myDB = mysql.connector.connect(host=SQL_HOST, port=SQL_PORT, user=SQL_USER, passwd=SQL_PASSWORD, database=SQL_SCHEMA, auth_plugin='mysql_native_password')

  myCursor = myDB.cursor()

def getSqlScrypt(name):

  textFile = open('./sql/' + name + '.sql', 'r')
  strFile = textFile.read()
  textFile.close()

  return strFile

def dbRollback():

  global myDB, myCursor

  if myDB is None or myCursor is None:
    print('# Error, database connection not established')
    return
  
  myDB.rollback()

def dbCommit():

  global myDB, myCursor

  if myDB is None or myCursor is None:
    print('# Error, database connection not established')
    return
  
  myDB.commit()

def dbExecute(sqlScrypt, values=None, commit=True):

  global myDB, myCursor

  if myDB is None or myCursor is None:
    print('# Error, database connection not established')
    return
      
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)
  
  if(commit):
    myDB.commit()

def dbExecuteMany(sqlScrypt, values=None, commit=True):

  global myDB, myCursor

  if myDB is None or myCursor is None:
    print('# Error, database connection not established')
    return
  
  if values != None:
    myCursor.executemany(sqlScrypt, values)
  else:
    myCursor.executemany(sqlScrypt)
  
  if(commit):
    myDB.commit()

def dbGetSingle(sqlScrypt, values=None):

  global myDB, myCursor

  if myDB is None or myCursor is None:
    print('# Error, database connection not established')
    return
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchone()

def dbGetAll(sqlScrypt, values=None):

  global myDB, myCursor

  if myDB is None or myCursor is None:
    print('# Error, database connection not established')
    return
  
  if values != None:
    myCursor.execute(sqlScrypt, values)
  else:
    myCursor.execute(sqlScrypt)

  return myCursor.fetchall()

def dbCreate(SQL_HOST, SQL_PORT, SQL_SCHEMA, SQL_USER, SQL_PASSWORD):

  global myDB, myCursor

  if myDB is None:
    print('# Error, database connection not established')
    return

  myCursor = myDB.cursor()
  myCursor.execute('create schema ' + str(SQL_SCHEMA))

  myDB = mysql.connector.connect(host=SQL_HOST, port=SQL_PORT, user=SQL_USER, passwd=SQL_PASSWORD, database=SQL_SCHEMA, auth_plugin='mysql_native_password')
  myCursor = myDB.cursor()

  myCursor.execute(getSqlScrypt('tbl_pessoa'))
  myCursor.execute(getSqlScrypt('tbl_aluno'))
  myCursor.execute(getSqlScrypt('tbl_professor'))
  myCursor.execute(getSqlScrypt('tbl_usuario'))
  myCursor.execute(getSqlScrypt('tbl_chave_cadastro'))
import mysql.connector
import os

def dbCheckCreate():

  dbObject = dbStartTransactionObj(False)

  if dbObject.dbConnection:
    print("# Connection to database successfull")
  else:
    print("# Connection to database failed")
    return

  dbObject.dbCursor.execute("show databases")

  schemaFound = False
  for db in dbObject.dbCursor:
    if os.getenv("SQL_SCHEMA") == db["Database"]:
      schemaFound = True
      break
  dbCloseTransactionObj(dbObject)

  if not schemaFound:
    print("# Schema " + str(os.getenv("SQL_SCHEMA")) + " not found! creating schema and tables")
    dbCreate()
    print("# Schema " + str(os.getenv("SQL_SCHEMA")) + " and tables created")
  else:
    print("# Schema " + str(os.getenv("SQL_SCHEMA")) + " is in database")

def dbStartTransactionObj(withSchema=True):

  dbConnection = None

  if withSchema:
    dbConnection = mysql.connector.connect(
      host = os.getenv("SQL_HOST"),
      port = os.getenv("SQL_PORT"),
      user = os.getenv("SQL_USER"),
      passwd = os.getenv("SQL_PASSWORD"),
      database = os.getenv("SQL_SCHEMA"),
      auth_plugin = "mysql_native_password")
  else:
    dbConnection = mysql.connector.connect(
      host = os.getenv("SQL_HOST"),
      port = os.getenv("SQL_PORT"),
      user = os.getenv("SQL_USER"),
      passwd = os.getenv("SQL_PASSWORD"),
      auth_plugin="mysql_native_password")

  dbCursor = dbConnection.cursor(buffered=True, dictionary=True)

  return dbObject(dbConnection, dbCursor, True)

def dbCloseTransactionObj(dbObjectIns):

  if not isinstance(dbObjectIns, dbObject):
    print("# Failed to close connection, db instance not a db class object")
    return
  
  if dbObjectIns.dbTransactionDone == False:
    print("# Warning, closing connection withot a commit or rollback, forced a commit to close the connection")
    dbObjectIns.dbConnection.commit()

  dbObjectIns.dbCursor.close()
  dbObjectIns.dbConnection.close()

def dbRollback(dbObjectIns):

  if not isinstance(dbObjectIns, dbObject):
    print("# Failed to rollback, db instance not a db class object")
    return
  
  dbObjectIns.dbTransactionDone = True
  dbObjectIns.dbConnection.rollback()
  dbCloseTransactionObj(dbObjectIns)

def dbCommit(dbObjectIns):

  if not isinstance(dbObjectIns, dbObject):
    print("# Failed to commit, db instance not a db class object")
    return
  
  dbObjectIns.dbTransactionDone = True
  dbObjectIns.dbConnection.commit()
  dbCloseTransactionObj(dbObjectIns)

def dbExecute(sqlScrypt, values=None, transactionMode=False, dbObjectIns=None):

  if transactionMode:
    if not dbObjectIns:
      print("# Error during transaction, db instance cannot be null")
      return
    elif not isinstance(dbObjectIns, dbObject):
      print("# Error during transaction, db instance not a db class object")
      return
    dbObjectIns.dbTransactionDone = False
    
  if not transactionMode:
    dbObjectIns = dbStartTransactionObj()
    dbObjectIns.dbConnection.commit()
      
  if values != None:
    dbObjectIns.dbCursor.execute(sqlScrypt, values)
  else:
    dbObjectIns.dbCursor.execute(sqlScrypt)
  
  if not transactionMode:
    dbCommit(dbObjectIns)

def dbExecuteMany(sqlScrypt, values=None, transactionMode=False, dbObjectIns=None):

  if transactionMode:
    if not dbObjectIns:
      print("# Error during transaction, db instance cannot be null")
      return
    elif not isinstance(dbObjectIns, dbObject):
      print("# Error during transaction, db instance not a db class object")
      return
    dbObjectIns.dbTransactionDone = False
    
  if not transactionMode:
    dbObjectIns = dbStartTransactionObj()
    dbObjectIns.dbConnection.commit()
  
  if values != None:
    dbObjectIns.dbCursor.executemany(sqlScrypt, values)
  else:
    dbObjectIns.dbCursor.executemany(sqlScrypt)
  
  if not transactionMode:
    dbCommit(dbObjectIns)

def dbGetSingle(sqlScrypt, values=None, transactionMode=False, dbObjectIns=None):

  if transactionMode:
    if not dbObjectIns:
      print("# Error during transaction, db instance cannot be null")
      return
    elif not isinstance(dbObjectIns, dbObject):
      print("# Error during transaction, db instance not a db class object")
      return
    dbObjectIns.dbTransactionDone = False
    
  if not transactionMode:
    dbObjectIns = dbStartTransactionObj()
    dbObjectIns.dbConnection.commit()
  
  if values != None:
    dbObjectIns.dbCursor.execute(sqlScrypt, values)
  else:
    dbObjectIns.dbCursor.execute(sqlScrypt)

  return dbObjectIns.dbCursor.fetchone()

def dbGetAll(sqlScrypt, values=None, transactionMode=False, dbObjectIns=None):

  if transactionMode:
    if not dbObjectIns:
      print("# Error during transaction, db instance cannot be null")
      return
    elif not isinstance(dbObjectIns, dbObject):
      print("# Error during transaction, db instance not a db class object")
      return
    dbObjectIns.dbTransactionDone = False
    
  if not transactionMode:
    dbObjectIns = dbStartTransactionObj()
    dbObjectIns.dbConnection.commit()
  
  if values != None:
    dbObjectIns.dbCursor.execute(sqlScrypt, values)
  else:
    dbObjectIns.dbCursor.execute(sqlScrypt)

  return dbObjectIns.dbCursor.fetchall()

def dbGetSqlFilterScrypt(argsObj, groupByCollumns=None, orderByCollumns=None, limitValue=None, offsetValue=None, initialSqlJunctionClause=" WHERE ", filterEnding=";", getFilterWithoutLimits=False):

  filterScrypt = ""
  filterScryptNoLimit = None
  filterValues = []
  filterValuesNoLimit = []
  sqlJunctionClause = initialSqlJunctionClause

  for args in argsObj:
    if not args.get("filterCollum") or not args.get("filterOperator"):
      return "Erro ao criar os filtros, args invalido"
    
    if args.get("filterValue"):

      if "LIKE" in args["filterOperator"]:

        filterScrypt += sqlJunctionClause + args["filterCollum"] + " LIKE %s "

        if "%_%" in args["filterOperator"]:
          filterValues.append(f'''%{args["filterValue"]}%''')
        elif "_%" in args["filterOperator"]:
          filterValues.append(f'''{args["filterValue"]}%''')
        elif "%_" in args["filterOperator"]:
          filterValues.append(f'''%{args["filterValue"]}''')
        else:
          filterValues.append(f'''{args["filterValue"]}''')
          
      else:
        filterScrypt += sqlJunctionClause + args["filterCollum"] + " " + args["filterOperator"] + " %s "
        filterValues.append(args["filterValue"])

      sqlJunctionClause = " AND "
  
  if getFilterWithoutLimits:
    filterScryptNoLimit = filterScrypt + filterEnding
    filterValuesNoLimit = filterValues.copy()

  if groupByCollumns:
    filterScrypt += " GROUP BY " + groupByCollumns

  if orderByCollumns:
    filterScrypt += " ORDER BY " + orderByCollumns
  
  if limitValue != None:
    filterScrypt += " LIMIT %s "
    filterValues.append(limitValue)
  
  if offsetValue != None:
    filterScrypt += " OFFSET %s "
    filterValues.append(offsetValue)
  
  filterScrypt += filterEnding

  if getFilterWithoutLimits:
    return filterScrypt, filterScryptNoLimit, filterValues, filterValuesNoLimit

  return filterScrypt, filterValues

def getSqlScrypt(name):

  textFile = open("./sql/" + name + ".sql", "r", encoding="utf-8")
  strFile = textFile.read()
  textFile.close()

  return strFile

def dbCreate():

  dbObject = dbStartTransactionObj(False)

  # creates schema and tables
  sqlScrypt = getSqlScrypt("sisges_create")
  for createTable in sqlScrypt.split(";"):
    dbObject.dbCursor.execute(createTable)

  # insert default values
  sqlScrypt = getSqlScrypt("sisges_insert_default")
  for insertTable in sqlScrypt.split(";"):
    dbObject.dbCursor.execute(insertTable)

  dbCommit(dbObject)

class dbObject():
  def __init__(self, dbConnection, dbCursor, dbTransactionDone):
    self.dbConnection = dbConnection
    self.dbCursor = dbCursor
    self.dbTransactionDone = dbTransactionDone
import logging
import mysql.connector
import os

logging = logging.getLogger(__name__)

def db_check_create():

    db_connection = mysql.connector.connect(
        host = os.getenv("SQL_HOST"),
        port = os.getenv("SQL_PORT"),
        user = os.getenv("SQL_USER"),
        passwd = os.getenv("SQL_PASSWORD"),
        auth_plugin="mysql_native_password"
    )

    db_cursor = db_connection.cursor(buffered=True, dictionary=True)

    if db_connection:
        logging.info("Connection to database successfull from mysql.connector")
    else:
        logging.warn("Connection to database failed from mysql.connector")
        return

    db_cursor.execute("show databases")

    schema_found = False
    for db in db_cursor:
        if os.getenv("SQL_SCHEMA") == db["Database"]:
            schema_found = True
            break

    if not schema_found:
        logging.info("Schema " + str(os.getenv("SQL_SCHEMA")) + " not found! creating schema and tables")
        create_database(db_cursor)
        logging.info("Schema " + str(os.getenv("SQL_SCHEMA")) + " and tables created")
    else:
        logging.info("Schema " + str(os.getenv("SQL_SCHEMA")) + " is in database")
  
    db_connection.commit()
    db_cursor.close()
    db_connection.close()

def create_database(db_cursor):

    # creates schema and tables
    sql_scrypt = get_sql_scrypt("sisflow_create")
    for create_table in sql_scrypt.split(";"):
        db_cursor.execute(create_table)

    # insert default values
    sql_scrypt = get_sql_scrypt("sisflow_insert_default")
    for insert_table in sql_scrypt.split(";"):
        db_cursor.execute(insert_table)

def get_sql_scrypt(name):

    txt_file = open("./sql/" + name + ".sql", "r", encoding="utf-8")
    str_file = txt_file.read()
    txt_file.close()

    return str_file
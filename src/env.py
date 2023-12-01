#import logging
from dotenv import load_dotenv, find_dotenv
import os

def get_missing_env():
    """ Returns a list of missing environment vars """

    return list(filter(lambda env: (os.getenv(env) == None), [
        "APP_HOST", "APP_PORT", 
        "FRONT_URL", 
        "SMTP_LOGIN", "SMTP_HOST", "SMTP_PASSWORD", "SMTP_PORT", 
        "SQL_HOST", "SQL_PASSWORD", "SQL_PORT", "SQL_SCHEMA", "SQL_USER", 
        "SYS_DEBUG"
    ]))

if get_missing_env():

    print("# Loading and checking environment from .env")
    load_dotenv(find_dotenv())

    missing_env = get_missing_env()
    if missing_env:
        print(f"# Error - Missing {str(missing_env)} environment variable{'s' if len(missing_env) > 1 else ''}")
        exit()

# system envs
DEBUG = os.getenv("SYS_DEBUG").lower() == "true"
HOST = os.getenv("APP_HOST")
PORT = int(os.getenv("APP_PORT"))

# mysql envs
MYSQL = {
    "user": os.getenv("SQL_USER"),
    "password": os.getenv("SQL_PASSWORD"),
    "host": os.getenv("SQL_HOST"),
    "port": os.getenv("SQL_PORT"),
    "schema": os.getenv("SQL_SCHEMA"),
}
DB_URI = "mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)s/%(schema)s" % MYSQL

# smtp envs
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_PORT = os.getenv("SMTP_PORT")

# deactivate flask sqlalchemy events that runs on top of sqlalchemy events to save system resources
SQLALCHEMY_TRACK_MODIFICATIONS = False
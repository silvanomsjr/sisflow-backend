from flask import Flask, abort
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import sys

from utils.dbUtils import dbStart
from utils.smtpMails import smtpStart
from services.authentication import Login, SignWithCode

import config

app = Flask(__name__)
CORS(
  app, 
  origins='*',
  headers=['Content-Type', 'Authorization'],
  expose_headers='Authorization')

api = Api(app)
api.add_resource(Login, '/login')
api.add_resource(SignWithCode, '/sign')

if __name__ == '__main__':

  if config.SYS_CMDLINE_ARGS:
    dbStart(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    smtpStart(sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
  
  else:
    dbStart(config.SQL_HOST, config.SQL_PORT, config.SQL_SCHEMA, config.SQL_USER, config.SQL_PASSWORD)
    smtpStart(config.SMTP_HOST, config.SMTP_PORT, config.SMTP_LOGIN, config.SMTP_PASSWORD)

  exit()

  
  app.run(debug=True)
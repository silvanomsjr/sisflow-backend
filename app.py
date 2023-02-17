from flask import Flask, abort
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import os
from dotenv import load_dotenv, find_dotenv

from utils.dbUtils import dbStart
from utils.smtpMails import smtpStart
from services.authentication import Login, Sign
from services.receiveFiles import ReceiveFile

app = Flask(__name__)
CORS(
  app,
  origins='*',
  headers=['Content-Type', 'Authorization'],
  expose_headers='Authorization')

api = Api(app)
api.add_resource(Login, '/login')
api.add_resource(Sign, '/sign')
api.add_resource(ReceiveFile, '/file')

# For production ambients like render.com the environment variables are already loaded
if not os.getenv('SQL_HOST'):
  print('# Loading environment from file')
  load_dotenv(find_dotenv())
  
# Start MySQL
dbStart()

# Start SMTP Server
smtpStart()
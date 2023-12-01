"""
Defines the blueprint for sending mail messages
"""
from flask import Blueprint
from flask_restful import Api

from resources import SendMailResource

SEND_MAIL_BLUEPRINT = Blueprint("sendmail", __name__)
Api(SEND_MAIL_BLUEPRINT).add_resource(
    SendMailResource, "/sendmail"
)
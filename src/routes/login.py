"""
Defines the blueprint for user login authentication
"""
from flask import Blueprint
from flask_restful import Api

from resources import LoginResource

LOGIN_BLUEPRINT = Blueprint("login", __name__)
Api(LOGIN_BLUEPRINT).add_resource(
    LoginResource, "/login"
)
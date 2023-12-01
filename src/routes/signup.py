"""
Defines the blueprint for user signup
"""
from flask import Blueprint
from flask_restful import Api

from resources import SignupResource

SIGNUP_BLUEPRINT = Blueprint("signup", __name__)
Api(SIGNUP_BLUEPRINT).add_resource(
    SignupResource, "/signup"
)
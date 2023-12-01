"""
Defines the blueprint for reasons and its classes
"""
from flask import Blueprint
from flask_restful import Api

from resources import ReasonsResource

REASONS_BLUEPRINT = Blueprint("reasons", __name__)
Api(REASONS_BLUEPRINT).add_resource(
    ReasonsResource, "/reasons"
)
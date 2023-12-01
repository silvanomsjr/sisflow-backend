"""
Defines the blueprint for single user solicitations
"""
from flask import Blueprint
from flask_restful import Api

from resources import SolicitationResource

SOLICITATION_BLUEPRINT = Blueprint("solicitation", __name__)
Api(SOLICITATION_BLUEPRINT).add_resource(
    SolicitationResource, "/solicitation"
)
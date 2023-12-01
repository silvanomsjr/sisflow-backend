"""
Defines the blueprint for advisors
"""
from flask import Blueprint
from flask_restful import Api

from resources import AdvisorsResource

ADVISORS_BLUEPRINT = Blueprint("advisors", __name__)
Api(ADVISORS_BLUEPRINT).add_resource(
    AdvisorsResource, "/advisors"
)
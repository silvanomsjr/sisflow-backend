"""
Defines the blueprint for solicitation advisors
"""
from flask import Blueprint
from flask_restful import Api

from resources import SolicitationAdvisorResource

SOLICITATION_ADVISOR_BLUEPRINT = Blueprint("solicitation_advisor", __name__)
Api(SOLICITATION_ADVISOR_BLUEPRINT).add_resource(
    SolicitationAdvisorResource, "/solicitation/advisor"
)
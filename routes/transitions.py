"""
Defines the blueprint for solicitation transitions
"""
from flask import Blueprint
from flask_restful import Api

from resources import SolicitationStateTransitionsResource

SOLICITATION_STATE_TRANSITIONS_BLUEPRINT = Blueprint("solicitation_state_transitions", __name__)
Api(SOLICITATION_STATE_TRANSITIONS_BLUEPRINT).add_resource(
    SolicitationStateTransitionsResource, "/solicitation/transitions"
)
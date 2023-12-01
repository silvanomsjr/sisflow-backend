"""
Defines the blueprints for solicitations of coordinators, advisors and students
"""
from flask import Blueprint
from flask_restful import Api

from resources import SolicitationsCoordinatorResource, SolicitationsAdvisorResource, SolicitationsStudentResource

SOLICITATIONS_COORDINATOR_BLUEPRINT = Blueprint("solicitations_coordinator", __name__)
Api(SOLICITATIONS_COORDINATOR_BLUEPRINT).add_resource(
    SolicitationsCoordinatorResource, "/solicitations/coordinator"
)

SOLICITATIONS_ADVISOR_BLUEPRINT = Blueprint("solicitations_advisor", __name__)
Api(SOLICITATIONS_ADVISOR_BLUEPRINT).add_resource(
    SolicitationsAdvisorResource, "/solicitations/advisor"
)

SOLICITATIONS_STUDENT_BLUEPRINT = Blueprint("solicitations_student", __name__)
Api(SOLICITATIONS_STUDENT_BLUEPRINT).add_resource(
    SolicitationsStudentResource, "/solicitations/student"
)
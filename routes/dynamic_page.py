"""
Defines the blueprint for dynamic page
"""
from flask import Blueprint
from flask_restful import Api

from resources import DynamicPageResource

DYNAMIC_PAGE_BLUEPRINT = Blueprint("dynamic_page", __name__)
Api(DYNAMIC_PAGE_BLUEPRINT).add_resource(
    DynamicPageResource, "/dynamic_page"
)
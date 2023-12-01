"""
Defines the blueprints for configurations
"""
from flask import Blueprint
from flask_restful import Api

from resources import ConfigResource, ConfigsResource

CONFIG_BLUEPRINT = Blueprint("config", __name__)
Api(CONFIG_BLUEPRINT).add_resource(
    ConfigResource, "/config/<string:config_name>"
)

CONFIGS_BLUEPRINT = Blueprint("configs", __name__)
Api(CONFIGS_BLUEPRINT).add_resource(
    ConfigsResource, "/configs"
)
"""
Define the REST HTTP verbs relative to the system configurations table
"""

from flask.json import jsonify
from flask_restful import Resource
from flask_restful.reqparse import Argument

from repositories import ConfigRepository, ConfigsRepository
from util import parse_params

class ConfigResource(Resource):
    """ HTTP methods relative to the config """

    @staticmethod
    def get(config_name):
        """ Return an config key information based on its config_name """
        config = ConfigRepository.read_config(config_name=config_name)
        return jsonify({"config": config.json})

class ConfigsResource(Resource):
    """ HTTP methods relative to all configs """

    @staticmethod
    def get():
        """ Return all configurations """
        configs = ConfigsRepository.read_configs()
        return jsonify({"configs": [config.json for config in configs]})
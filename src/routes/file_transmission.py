"""
Defines the blueprint for file upload and download
"""
from flask import Blueprint
from flask_restful import Api

from resources import FileTransmitionResource

FILE_TRANSMITION_BLUEPRINT = Blueprint("file", __name__)
Api(FILE_TRANSMITION_BLUEPRINT).add_resource(
    FileTransmitionResource, "/file"
)
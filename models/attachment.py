"""
The Attachment model
"""
from . import db
from .base import BaseModel, MetaBaseModel

class Attachment(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "attachment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash_name = db.Column(db.String(150), unique=True, nullable=False)

    user_has_attachment = db.Relationship("UserHasAttachment", backref="attachment") # 1-N

    """ Create a new Attachment """
    def __init__(self, hash_name):
        self.hash_name = hash_name
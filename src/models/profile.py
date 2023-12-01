"""
The Profile model
"""
from . import db
from .base import BaseModel, MetaBaseModel

class Profile(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_name = db.Column(db.String(50), unique=True)
    profile_acronym = db.Column(db.String(3), unique=True)
    profile_dynamic_fields_metadata = db.Column(db.JSON)

    user_has_profile = db.Relationship("UserHasProfile", backref="profile") # 1-N
    solicitation_state_profile_editors = db.Relationship("SolicitationStateProfileEditors", backref="profile") # 1-N

    """ Create a new Profile """
    def __init__(self, profile_name, profile_acronym, profile_dynamic_fields_metadata):
        self.profile_name = profile_name
        self.profile_acronym = profile_acronym
        self.profile_dynamic_fields_metadata = profile_dynamic_fields_metadata
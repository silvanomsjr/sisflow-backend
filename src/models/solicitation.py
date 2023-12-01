"""
The Solicitation category models
"""
from . import db
from .base import BaseModel, MetaBaseModel

class Solicitation(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    solicitation_name = db.Column(db.String(256))

    solicitation_start_mail = db.Relationship("SolicitationStartMail", backref="solicitation")  # 1-N
    solicitation_state = db.Relationship("SolicitationState", backref="solicitation")           # 1-N
    user_has_solicitation = db.Relationship("UserHasSolicitation", backref="solicitation")      # 1-N

    """ Create a new Solicitation """
    def __init__(self, solicitation_name):
        self.solicitation_name = solicitation_name

class SolicitationStartMail(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_start_mail"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    solicitation_id = db.Column(db.Integer, db.ForeignKey("solicitation.id"), nullable=False)
    dynamic_mail_id = db.Column(db.Integer, db.ForeignKey("dynamic_mail.id"), nullable=False)

    """ Create a new SolicitationStartMail """
    def __init__(self, solicitation_id, dynamic_mail_id):
        self.solicitation_id = solicitation_id
        self.dynamic_mail_id = dynamic_mail_id

class SolicitationState(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_state"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    solicitation_id = db.Column(db.Integer, db.ForeignKey("solicitation.id"), nullable=False)
    state_description = db.Column(db.String(256))
    state_max_duration_days = db.Column(db.Integer)
    state_dynamic_page_id = db.Column(db.Integer, db.ForeignKey("dynamic_page.id"))
    state_static_page_name = db.Column(db.String(100))
    is_initial_state = db.Column(db.Boolean, nullable=False)

    #solicitation_state_transition = db.Relationship("SolicitationStateTransition", backref="solicitation_state")         # 1-N
    user_has_solicitation = db.Relationship("UserHasSolicitation", backref="solicitation_state")                          # 1-N
    user_has_solicitation_state = db.Relationship("UserHasSolicitationState", backref="solicitation_state")               # 1-N
    solicitation_state_profile_editors = db.Relationship("SolicitationStateProfileEditors", backref="solicitation_state") # 1-N

    """ Create a new SolicitationState """
    def __init__(self, solicitation_id, is_initial_state, state_description=None, state_max_duration_days=None, 
        state_dynamic_page_id=None, state_static_page_name=None):
        self.solicitation_id = solicitation_id
        self.state_description = state_description
        self.state_max_duration_days = state_max_duration_days
        self.state_dynamic_page_id = state_dynamic_page_id
        self.state_static_page_name = state_static_page_name
        self.is_initial_state = is_initial_state

class SolicitationStateProfileEditors(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_state_profile_editors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    solicitation_state_id = db.Column(db.Integer, db.ForeignKey("solicitation_state.id"), nullable=False)
    state_profile_editor = db.Column(db.Integer, db.ForeignKey("profile.id"), nullable=False)

    """ Create a new SolicitationStateProfileEditors """
    def __init__(self, solicitation_state_id, state_profile_editor):
        self.solicitation_state_id = solicitation_state_id
        self.state_profile_editor = state_profile_editor
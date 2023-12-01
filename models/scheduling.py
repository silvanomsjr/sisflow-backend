"""
The Scheduling category models
"""
from . import db
from .base import BaseModel, MetaBaseModel

class Scheduling(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "scheduling"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scheduled_action = db.Column(db.Enum("Send Mail", "Solicitation State Transition"), nullable=False)
    scheduled_datetime = db.Column(db.DateTime,  nullable=False)
    scheduled_status = db.Column(db.Enum("Pending", "Sended", "Canceled"), nullable=False)

    scheduling_state_transition = db.Relationship("SchedulingStateTransition", backref="scheduling", uselist=False) # 1-1

    """ Create a new Scheduling """
    def __init__(self, scheduled_action, scheduled_datetime, scheduled_status="Pending"):
        self.scheduled_action = scheduled_action
        self.scheduled_datetime = scheduled_datetime
        self.scheduled_status = scheduled_status

class SchedulingStateTransition(db.Model, BaseModel, metaclass=MetaBaseModel):

    __tablename__ = "scheduling_state_transition"

    scheduling_id = db.Column(db.Integer, db.ForeignKey("scheduling.id"), primary_key=True)
    state_transition_scheduled_id = db.Column(db.Integer, 
        db.ForeignKey("solicitation_state_transition_scheduled.solicitation_state_transition_id"), nullable=False)
    user_has_solicitation_state_id = db.Column(db.Integer, db.ForeignKey("user_has_solicitation_state.id"), nullable=False)

    """ Create a new SchedulingStateTransition """
    def __init__(self, scheduling_id, state_transition_scheduled_id, user_has_solicitation_state_id):
        self.scheduling_id = scheduling_id
        self.state_transition_scheduled_id = state_transition_scheduled_id
        self.user_has_solicitation_state_id = user_has_solicitation_state_id
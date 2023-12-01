"""
The Dynamic Mail model
"""
from . import db
from .base import BaseModel, MetaBaseModel

class DynamicMail(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_mail"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mail_subject = db.Column(db.String(100), nullable=False)
    mail_body_html = db.Column(db.String(100), nullable=False)
    is_sent_to_student = db.Column(db.Boolean, nullable=False)
    is_sent_to_advisor = db.Column(db.Boolean, nullable=False)
    is_sent_to_coordinator = db.Column(db.Boolean, nullable=False)

    solicitation_start_mail = db.Relationship("SolicitationStartMail", backref="dynamic_mail")                      # 1-N
    solicitation_state_transition_mail = db.Relationship("SolicitationStateTransitionMail", backref="dynamic_mail") # 1-N

    """ Create a new DynamicMail """
    def __init__(self, mail_subject, mail_body_html, is_sent_to_student=False, is_sent_to_advisor=False, is_sent_to_coordinator=False):
        self.mail_subject = mail_subject
        self.mail_body_html = mail_body_html
        self.is_sent_to_student = is_sent_to_student
        self.is_sent_to_advisor = is_sent_to_advisor
        self.is_sent_to_coordinator = is_sent_to_coordinator
"""
The Transition category models
"""
from . import db
from .base import BaseModel, MetaBaseModel

class SolicitationStateTransition(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_state_transition"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transition_name = db.Column(db.String(100), nullable=False)

    # needs refs to avoid errors in SQLAlchemy, allows solicitation access by transitions fields from and to
    solicitation_state_id_from = db.Column(db.Integer, db.ForeignKey("solicitation_state.id"), nullable=False)
    solicitation_state_id_to = db.Column(db.Integer,  db.ForeignKey("solicitation_state.id"))

    solicitation_state_id_from_ref = db.relationship("SolicitationState", uselist=False, foreign_keys=[solicitation_state_id_from])
    solicitation_state_id_to_ref = db.relationship("SolicitationState", uselist=False, foreign_keys=[solicitation_state_id_to])

    # relation with the transition types
    solicitation_state_transition_manual = db.Relationship("SolicitationStateTransitionManual", 
        backref="solicitation_state_transition", uselist=False) # 1-1
    solicitation_state_transition_from_dynamic_page = db.Relationship("SolicitationStateTransitionFromDynamicPage", 
        backref="solicitation_state_transition", uselist=False) # 1-1
    solicitation_state_transition_scheduled = db.Relationship("SolicitationStateTransitionScheduled", 
        backref="solicitation_state_transition", uselist=False) # 1-1
    solicitation_state_transition_mail = db.Relationship("SolicitationStateTransitionMail", 
        backref="solicitation_state_transition") # 1-N
        
    """ Create a new SolicitationStateTransition """
    def __init__(self, solicitation_state_id_from, transition_name, solicitation_state_id_to=None):
        self.solicitation_state_id_from = solicitation_state_id_from
        self.solicitation_state_id_to = solicitation_state_id_to
        self.transition_name = transition_name

class SolicitationStateTransitionManual(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_state_transition_manual"

    solicitation_state_transition_id = db.Column(db.Integer, db.ForeignKey("solicitation_state_transition.id"), primary_key=True)
    transition_decision = db.Column(db.Enum("Em analise", "Solicitado", "Enviado", "Deferido", "Indeferido", 
        "Cancelado pelo aluno", "Cancelado pelo orientador", "Cancelado pela coordenação", "Expirado"), nullable=False)
    transition_reason = db.Column(db.String(100), nullable=False)

    """ Create a new SolicitationStateTransitionManual """
    def __init__(self, solicitation_state_transition_id, transition_reason, transition_decision="Em analise"):
        self.solicitation_state_transition_id = solicitation_state_transition_id
        self.transition_decision = transition_decision
        self.transition_reason = transition_reason

class SolicitationStateTransitionFromDynamicPage(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_state_transition_from_dynamic_page"

    solicitation_state_transition_id = db.Column(db.Integer, db.ForeignKey("solicitation_state_transition.id"), primary_key=True)
    dynamic_page_component = db.Column(db.Enum("Button-Request", "Button-Cancel", "Button-Send", 
        "Button-Send and Defer", "Button-Defer", "Button-Reject", "Table-Cancel"), nullable=False)
    transition_decision = db.Column(db.Enum("Em analise", "Solicitado", "Enviado", "Deferido", "Indeferido", 
        "Cancelado pelo aluno", "Cancelado pelo orientador", "Cancelado pela coordenação", "Expirado"), nullable=False)
    transition_reason = db.Column(db.String(100), nullable=False)

    """ Create a new SolicitationStateTransitionFromDynamicPage """
    def __init__(self, solicitation_state_transition_id, dynamic_page_component, transition_reason, 
        transition_decision="Em analise"):
        self.solicitation_state_transition_id = solicitation_state_transition_id
        self.dynamic_page_component = dynamic_page_component
        self.transition_decision = transition_decision
        self.transition_reason = transition_reason

class SolicitationStateTransitionScheduled(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_state_transition_scheduled"

    solicitation_state_transition_id = db.Column(db.Integer, db.ForeignKey("solicitation_state_transition.id"), primary_key=True)
    transition_decision = db.Column(db.Enum("Em analise", "Solicitado", "Enviado", "Deferido", "Indeferido", 
        "Cancelado pelo aluno", "Cancelado pelo orientador", "Cancelado pela coordenação", "Expirado"), nullable=False)
    transition_reason = db.Column(db.String(100), nullable=False)
    transition_delay_seconds = db.Column(db.Integer, nullable=False)

    scheduling_state_transition = db.Relationship("SchedulingStateTransition", backref="solicitation_state_transition_scheduled") # 1-N

    """ Create a new SolicitationStateTransitionScheduled """
    def __init__(self, solicitation_state_transition_id, transition_reason, transition_delay_seconds,
        transition_decision="Em analise"):
        self.solicitation_state_transition_id = solicitation_state_transition_id
        self.transition_decision = transition_decision
        self.transition_reason = transition_reason
        self.transition_delay_seconds = transition_delay_seconds

class SolicitationStateTransitionMail(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "solicitation_state_transition_mail"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    solicitation_state_transition_id = db.Column(db.Integer, db.ForeignKey("solicitation_state_transition.id"), nullable=False)
    dynamic_mail_id = db.Column(db.Integer, db.ForeignKey("dynamic_mail.id"), nullable=False)

    """ Create a new SolicitationStateTransitionMail """
    def __init__(self, solicitation_state_transition_id, dynamic_mail_id):
        self.solicitation_state_transition_id = solicitation_state_transition_id
        self.dynamic_mail_id = dynamic_mail_id
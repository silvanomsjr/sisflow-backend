"""
The User Data category models
"""
from . import db
from .base import BaseModel, MetaBaseModel

class User(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    institutional_email = db.Column(db.String(256), unique=True, nullable=False)
    secondary_email = db.Column(db.String(256))
    user_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('M', 'F'), nullable=False)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(65))
    password_salt = db.Column(db.String(16))
    creation_datetime = db.Column(db.DateTime)

    user_has_profile = db.Relationship("UserHasProfile", backref="user")                # 1-N
    user_has_attachment = db.Relationship("UserHasAttachment", backref="user")          # 1-N
    user_has_solicitation = db.Relationship("UserHasSolicitation", backref="user")      # 1-N
    mail_validation = db.Relationship("MailValidation", backref="user", uselist=False)  # 1-1

    """ Create a new User """
    def __init__(self, institutional_email, secondary_email, user_name, gender, phone, password_hash, password_salt, creation_datetime):
        self.institutional_email = institutional_email
        self.secondary_email = secondary_email
        self.user_name = user_name
        self.gender = gender
        self.phone = phone
        self.password_hash = password_hash
        self.password_salt = password_salt
        self.creation_datetime = creation_datetime

class UserHasProfile(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_has_profile"
    __table_args__ = (db.UniqueConstraint("user_id", "profile_id"),) # defines the unique constraint

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"), nullable=False)
    user_dinamyc_profile_fields_data = db.Column(db.JSON)
    start_datetime = db.Column(db.Date, nullable=False)
    end_datetime = db.Column(db.Date)

    user_has_profile_coordinator_data = db.Relationship("UserHasProfileCoordinatorData", backref="user_has_profile", uselist=False) # 1-1
    user_has_profile_advisor_data = db.Relationship("UserHasProfileAdvisorData", backref="user_has_profile", uselist=False)         # 1-1
    user_has_profile_student_data = db.Relationship("UserHasProfileStudentData", backref="user_has_profile", uselist=False)         # 1-1

    """ Create a new UserHasProfile """
    def __init__(self, user_id, profile_id, user_dinamyc_profile_fields_data, start_datetime, end_datetime):
        self.user_id = user_id
        self.profile_id = profile_id
        self.user_dinamyc_profile_fields_data = user_dinamyc_profile_fields_data
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

class UserHasProfileCoordinatorData(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_has_profile_coordinator_data"

    user_has_profile_id = db.Column(db.Integer, db.ForeignKey("user_has_profile.id"), primary_key=True)
    siape = db.Column(db.String(15), unique=True, nullable=False)

    """ Create a new UserHasProfileCoordinatorData """
    def __init__(self, user_has_profile_id, siape):
        self.user_has_profile_id = user_has_profile_id
        self.siape = siape

class UserHasProfileAdvisorData(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_has_profile_advisor_data"

    user_has_profile_id = db.Column(db.Integer, db.ForeignKey("user_has_profile.id"), primary_key=True)
    siape = db.Column(db.String(15), unique=True, nullable=False)

    user_has_solicitation = db.Relationship("UserHasSolicitation", backref="user_has_profile_advisor_data") # 1-N

    """ Create a new UserHasProfileAdvisorData """
    def __init__(self, user_has_profile_id, siape):
        self.user_has_profile_id = user_has_profile_id
        self.siape = siape

class UserHasProfileStudentData(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_has_profile_student_data"

    user_has_profile_id = db.Column(db.Integer, db.ForeignKey("user_has_profile.id"), primary_key=True)
    matricula = db.Column(db.String(15), unique=True, nullable=False)
    course = db.Column(db.Enum("BCC", "BSI"), nullable=False)

    """ Create a new UserHasProfileStudentData """
    def __init__(self, user_has_profile_id, matricula, course):
        self.user_has_profile_id = user_has_profile_id
        self.matricula = matricula
        self.course = course

class UserHasAttachment(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_has_attachment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False)
    attachment_id = db.Column(db.Integer, db.ForeignKey("attachment.id"), nullable=False)

    """ Create a new UserHasAttachment """
    def __init__(self, user_id, attachment_id):
        self.user_id = user_id
        self.attachment_id = attachment_id

class UserHasSolicitation(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_has_solicitation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False)
    advisor_siape = db.Column(db.String(15), db.ForeignKey("user_has_profile_advisor_data.siape"))
    is_accepted_by_advisor = db.Column(db.Boolean, nullable=False)
    solicitation_id = db.Column(db.Integer, db.ForeignKey("solicitation.id"), nullable=False)
    actual_solicitation_state_id = db.Column(db.Integer, db.ForeignKey("solicitation_state.id"), nullable=False)
    solicitation_user_data = db.Column(db.JSON)

    user_has_solicitation_state = db.Relationship("UserHasSolicitationState", order_by="UserHasSolicitationState.id.desc()", 
        backref="user_has_solicitation") # 1-N

    """ Create a new UserHasSolicitation """
    def __init__(self, user_id, advisor_siape, solicitation_id, actual_solicitation_state_id, is_accepted_by_advisor=None,
        solicitation_user_data=None):
        self.user_id = user_id
        self.advisor_siape = advisor_siape
        self.is_accepted_by_advisor = is_accepted_by_advisor
        self.solicitation_id = solicitation_id
        self.actual_solicitation_state_id = actual_solicitation_state_id
        self.solicitation_user_data = solicitation_user_data

class UserHasSolicitationState(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "user_has_solicitation_state"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_has_solicitation_id = db.Column(db.Integer, db.ForeignKey("user_has_solicitation.id"), nullable=False)
    solicitation_state_id = db.Column(db.Integer, db.ForeignKey("solicitation_state.id"), nullable=False)
    decision = db.Column(db.Enum("Em analise", "Solicitado", "Enviado", "Deferido", "Indeferido", "Cancelado pelo aluno", 
        "Cancelado pelo orientador", "Cancelado pela coordenação", "Expirado"), nullable=False)
    reason = db.Column(db.String(100))
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime)

    scheduling_state_transition = db.Relationship("SchedulingStateTransition", backref="user_has_solicitation_state") # 1-N

    """ Create a new UserHasSolicitationState """
    def __init__(self, user_has_solicitation_id, solicitation_state_id, decision, start_datetime, reason=None, end_datetime=None):
        self.user_has_solicitation_id = user_has_solicitation_id
        self.solicitation_state_id = solicitation_state_id
        self.decision = decision
        self.reason = reason
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
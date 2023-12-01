"""
The Configuration category models
"""
from . import db
from .base import BaseModel, MetaBaseModel

class Config(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "config"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_name = db.Column(db.String(50))

    config_system_path = db.Relationship("ConfigSystemPath", backref="config", uselist=False)   # 1-1
    config_mail = db.Relationship("ConfigMail", backref="config", uselist=False)                # 1-1
    config_year = db.Relationship("ConfigYear", backref="config", uselist=False)                # 1-1
    config_reason_class = db.Relationship("ConfigReasonClass", backref="config", uselist=False) # 1-1

    """ Create a new Config """
    def __init__(self, config_name):
        self.config_name = config_name

class ConfigSystemPath(db.Model, BaseModel, metaclass=MetaBaseModel):

    __tablename__ = "config_system_path"

    config_id = db.Column(db.Integer, db.ForeignKey("config.id"), primary_key=True)
    system_path= db.Column(db.String(256))

    """ Create a new ConfigSystemPath """
    def __init__(self, config_id, system_path):
        self.config_id = config_id
        self.system_path = system_path

class ConfigMail(db.Model, BaseModel, metaclass=MetaBaseModel):

    __tablename__ = "config_mail"

    config_id = db.Column(db.Integer, db.ForeignKey("config.id"), primary_key=True)
    mail = db.Column(db.String(256), unique=True)
    mail_name = db.Column(db.String(100))

    """ Create a new ConfigMail """
    def __init__(self, config_id, mail, mail_name):
        self.config_id = config_id
        self.mail = mail
        self.mail_name = mail_name

class ConfigYear(db.Model, BaseModel, metaclass=MetaBaseModel):

    __tablename__ = "config_year"

    config_id = db.Column(db.Integer, db.ForeignKey("config.id"), primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
    config_year_holiday = db.Relationship("ConfigYearHoliday", backref="config_year") # 1-N

    """ Create a new ConfigYear """
    def __init__(self, config_id, year):
        self.config_id = config_id
        self.year = year

class ConfigYearHoliday(db.Model, BaseModel, metaclass=MetaBaseModel):

    __tablename__ = "config_year_holiday"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, db.ForeignKey("config_year.year"))
    get_by = db.Column(db.Enum("API", "Personalized"))
    holiday_name = db.Column(db.String(50), unique=True, nullable=False)
    holiday_date = db.Column(db.Date, unique=True, nullable=False)

    """ Create a new ConfigYearHoliday """
    def __init__(self, year, get_by, holiday_name, holiday_date):
        self.year = year
        self.get_by = get_by
        self.holiday_name = holiday_name
        self.holiday_date = holiday_date

class ConfigReasonClass(db.Model, BaseModel, metaclass=MetaBaseModel):

    __tablename__ = "config_reason_class"

    config_id = db.Column(db.Integer, db.ForeignKey("config.id"), primary_key=True)
    class_name = db.Column(db.String(50), unique=True, nullable=False)
    config_reason = db.Relationship("ConfigReason", backref="config_reason_class") # 1-N

    """ Create a new ConfigReasonClass """
    def __init__(self, config_id, class_name):
        self.config_id = config_id
        self.class_name = class_name

class ConfigReason(db.Model, BaseModel, metaclass=MetaBaseModel):

    __tablename__ = "config_reason"

    id = db.Column(db.Integer, primary_key=True)
    reason_class_id = db.Column(db.Integer, db.ForeignKey("config_reason_class.config_id"), nullable=False)
    inner_html = db.Column(db.String(2000), nullable=False)

    """ Create a new ConfigReason """
    def __init__(self, id, reason_class_id, inner_html):
        self.id = id
        self.reason_class_id = reason_class_id
        self.inner_html = inner_html
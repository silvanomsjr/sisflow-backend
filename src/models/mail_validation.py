"""
The Mail Validation model
"""
from . import db
from .base import BaseModel, MetaBaseModel
    
class MailValidation(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "mail_validation"

    institutional_email = db.Column(db.String(256), db.ForeignKey("user_account.institutional_email"), primary_key=True)
    validation_code = db.Column(db.String(10))
    validation_code_expires_in = db.Column(db.TIMESTAMP)

    """ Create a new MailValidation """
    def __init__(self, institutional_email, validation_code, validation_code_expires_in=None):
        self.institutional_email = institutional_email
        self.validation_code = validation_code
        self.validation_code_expires_in = validation_code_expires_in
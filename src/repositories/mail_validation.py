""" Defines the MailValidation repository """

from models import MailValidation

class MailValidationRepository:
    """ The repository for mail_validations """

    @staticmethod
    def create_mail_validation(institutional_email, validation_code):
        """ Create a mail_validation """
        mail_validation = MailValidation(institutional_email, validation_code)
        return mail_validation.save()

    @staticmethod
    def read_mail_validation(institutional_email=None, validation_code=None):
        """ Query a mail_validation by institutional_email or/and by validation_code"""
        
        mail_validation = None
        
        # query by institutional_email and validation_code
        if institutional_email and validation_code:
            mail_validation_query = MailValidation.query.filter_by(institutional_email=institutional_email, validation_code=validation_code)
            if mail_validation_query.count() == 1:
                mail_validation = mail_validation_query.one()
        
        # query by institutional_email only
        elif institutional_email:
            mail_validation_query = MailValidation.query.filter_by(institutional_email=institutional_email)
            if mail_validation_query.count() == 1:
                mail_validation = mail_validation_query.one()
        
        return mail_validation
    
    @staticmethod
    def update_mail_validation(institutional_email, validation_code):
        """ Update a mail_validation's validation_code """
        
        mail_validation = MailValidationRepository.read_mail_validation(institutional_email=institutional_email)

        if not mail_validation:
            return None
            
        mail_validation.validation_code = validation_code
        return mail_validation.save()
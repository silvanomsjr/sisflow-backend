""" Defines the User repository """

from models import User, UserHasAttachment, UserHasProfileAdvisorData

class UserRepository:
    """ The repository for one user """

    @staticmethod
    def create_user_has_attachment(user_id, attachment_id):
        """ Creates a user has attachment """
        user_has_attachment = UserHasAttachment(user_id, attachment_id)
        return user_has_attachment.save()

    @staticmethod
    def read_user(id=None, institutional_email=None):
        """ Query a user by id or by institutional_email"""
        user = None

        if id:
            user_query = User.query.filter_by(id=id)
            if user_query.count() == 1:
                user = user_query.one()

        elif institutional_email:
            user_query = User.query.filter_by(institutional_email=institutional_email)
            if user_query.count() == 1:
                user = user_query.one()

        return user
    
    @staticmethod
    def read_advisor_profile_user(siape):
        """ Query a advisor user by siape """

        uhpd_query = UserHasProfileAdvisorData.query.filter_by(siape=siape)
        if uhpd_query.count() != 1:
            return None
        
        user_has_profile_advisor_data = uhpd_query.one()
        user_has_profile = user_has_profile_advisor_data.user_has_profile
        user = user_has_profile.user

        return user

    @staticmethod
    def update_user(id=None, institutional_email=None, secondary_email=None, user_name=None, 
        gender=None, phone=None, password_hash=None, password_salt=None, creation_datetime=None):
        """ Update a user """
        
        user = UserRepository.read_user(id, institutional_email)

        if not user:
            return None
        
        if secondary_email:
            user.secondary_email = secondary_email
        if user_name:
            user.user_name = user_name
        if gender:
            user.gender = gender
        if phone:
            user.phone = phone
        if password_hash:
            user.password_hash = password_hash
        if password_salt:
            user.password_salt = password_salt
        if creation_datetime:
            user.creation_datetime = creation_datetime

        return user.save()

class UsersRepository:
    """ The repository for all users """

    @staticmethod
    def read_users():
        """ Query all configs """
        return User.query.all()
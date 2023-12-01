""" Defines the Solicitations repository """

from models import User, UserHasSolicitation

class SolicitationsRepository:
    """ The repository for multiple solicitations """

    @staticmethod
    def read_user_solicitations(student_id=None, advisor_id=None):
        """ Query solicitations by student, advisor id or all """

        if student_id:
            return UserHasSolicitation.query.filter_by(user_id=student_id).all()
        
        elif advisor_id:
            advisor_solicitations = None

            advisor_query = User.query.filter_by(id=advisor_id)
            if advisor_query.count() == 1:
                advisor_user = advisor_query.one()
                
                for advisor_profile in advisor_user.user_has_profile:
                    if advisor_profile.user_has_profile_advisor_data:
                        advisor_siape = advisor_profile.user_has_profile_advisor_data.siape
                        advisor_solicitations = UserHasSolicitation.query.filter_by(advisor_siape=advisor_siape).all()

            return advisor_solicitations

        return UserHasSolicitation.query.all()
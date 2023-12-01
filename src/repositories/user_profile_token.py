""" Defines the repository to creating profile tokens """

from models import User, UserHasSolicitation

class UserProfileTokenRepository:
    """ The repository for a user profile token """

    @staticmethod
    def read_user_profile_token(user_id):
        """ Query a user by id and makes its profile token """

        user_query = User.query.filter_by(id=user_id)
        if user_query.count() != 1:
            return None
        user = user_query.one()

        # creates response object with user profiles, used in jwt authentication and to parse dynamic strings
        user_token = {
            "user_id": user.id,
            "institutional_email": user.institutional_email,
            "secondary_email": user.secondary_email,
            "user_name": user.user_name,
            "gender": user.gender,
            "phone": user.phone,
            "creation_datetime": user.creation_datetime.strftime("%Y-%m-%d %H:%M:%S") if user.creation_datetime else "",
            "profiles": [],
            "profile_acronyms": []
        }

        # creates user fields based on its profiles
        for user_has_profile in user.user_has_profile:
            profile = user_has_profile.profile

            # basic columns
            formated_profile = {
                "profile_name": profile.profile_name,
                "profile_acronym": profile.profile_acronym,
                "profile_dynamic_fields_metadata": profile.profile_dynamic_fields_metadata,
                "user_dinamyc_profile_fields_data": user_has_profile.user_dinamyc_profile_fields_data,
                "start_datetime": user_has_profile.start_datetime.strftime("%Y-%m-%d %H:%M:%S") if user_has_profile.start_datetime else "",
                "end_datetime": user_has_profile.end_datetime.strftime("%Y-%m-%d %H:%M:%S") if user_has_profile.end_datetime else ""
            }
            
            # profile specific fields
            # coordinator
            if user_has_profile.user_has_profile_coordinator_data:
                formated_profile["siape"] = user_has_profile.user_has_profile_coordinator_data.siape
                formated_profile["coordinator_students"] = UserHasSolicitation.query\
                    .with_entities(UserHasSolicitation.advisor_siape, UserHasSolicitation.user_id)\
                    .filter_by(advisor_siape=formated_profile["siape"])\
                    .distinct().count()

            # advisor
            elif user_has_profile.user_has_profile_advisor_data:
                formated_profile["siape"] = user_has_profile.user_has_profile_advisor_data.siape
                formated_profile["advisor_students"] = UserHasSolicitation.query\
                    .with_entities(UserHasSolicitation.advisor_siape, UserHasSolicitation.user_id)\
                    .filter_by(advisor_siape=formated_profile["siape"])\
                    .distinct().count()

            # student
            elif user_has_profile.user_has_profile_student_data:
                formated_profile["matricula"] = user_has_profile.user_has_profile_student_data.matricula
                formated_profile["course"] = user_has_profile.user_has_profile_student_data.course

            user_token["profiles"].append(formated_profile)
            user_token["profile_acronyms"].append(formated_profile["profile_acronym"])

        return user_token
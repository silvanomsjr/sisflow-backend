""" Defines the advisor repository """

from models import User, UserHasProfile, UserHasProfileAdvisorData, UserHasSolicitation

class AdvisorsRepository:
    """ The repository for multiple advisors """

    @staticmethod
    def read_advisors(advisor_name=None, limit=None, offset=None, format=True):
        """ Query advisor users by name or applying custom offsets """
        
        # query
        advisors_query = UserHasProfileAdvisorData.query\
            .join(UserHasProfile, UserHasProfileAdvisorData.user_has_profile_id == UserHasProfile.id)\
            .join(User, UserHasProfile.user_id == User.id)\
            .add_columns(User.id.label("user_id"), User.institutional_email, User.secondary_email, User.user_name, User.gender, User.phone)
        
        # filters
        if advisor_name != None:
            advisors_query = advisors_query.filter(User.user_name.like("%{}%".format(advisor_name)))
        count_query = advisors_query

        if limit != None:
            advisors_query = advisors_query.limit(limit)
        if offset != None:
            advisors_query = advisors_query.offset(offset)

        # validation
        count = count_query.count()
        advisors = advisors_query.all()

        if not format or not advisors:
            return advisors

        # format
        formated_advs = {
            "count": count,
            "advisors": []
        }

        for adv in advisors:
            advisor_students = UserHasSolicitation.query\
                .with_entities(UserHasSolicitation.advisor_siape, UserHasSolicitation.user_id)\
                .filter_by(advisor_siape=adv.UserHasProfileAdvisorData.siape)\
                .distinct().count()

            formated_advs["advisors"].append({
                "user_id": adv.user_id,
                "institutional_email": adv.institutional_email,
                "secondary_email": adv.secondary_email,
                "user_name": adv.user_name,
                "gender": adv.gender,
                "phone": adv.phone,
                "siape": adv.UserHasProfileAdvisorData.siape,
                "advisor_students": advisor_students
            })

        return formated_advs
""" Defines the Reason repository """

from models import ConfigReason, ConfigReasonClass

class ReasonsRepository:
    """ The repository for multiple reasons """

    @staticmethod
    def read_reasons(system_configuration, student_token=None, advisor_token=None, class_names=None, reason_id=None, reason_content=None):
        """ Query reasons using user_has_state_id and filters """

        # read and format all reason classes
        reasons_classes = ConfigReasonClass.query.all()
        formatted_reasons_classes = []

        # format response
        for clss in reasons_classes:
            formatted_reasons_classes.append({
                "reason_class_id": clss.config_id,
                "reason_class_name": clss.class_name
            })
        
        # read reasons 
        reasons_query = ConfigReasonClass.query\
            .join(ConfigReason, ConfigReasonClass.config_id == ConfigReason.reason_class_id)\
            .add_columns(ConfigReason.id.label("reason_id"), ConfigReason.inner_html.label("reason_inner_html"))

        # apply filters, if any
        if class_names != None:
            reason_class_list = class_names.split(",")
            reasons_query.filter(ConfigReason.class_name.in_(reason_class_list))
        if reason_id != None:
            reasons_query.filter(ConfigReason.id == reason_id)
        if reason_content != None:
            reasons_query.filter(ConfigReason.inner_html.like("%{}%".format(reason_content)))

        # format response
        reasons = reasons_query.all()
        formatted_reasons = []
        for reason in reasons:
            formatted_reasons.append({
                "reason_id": reason.reason_id,
                "reason_inner_html": system_configuration.sistem_str_parser(reason.reason_inner_html, student_token, advisor_token),
                "reason_class_id": reason.ConfigReasonClass.config_id,
                "reason_class_name": reason.ConfigReasonClass.class_name
            })

        return { "classes": formatted_reasons_classes, "reasons": formatted_reasons }
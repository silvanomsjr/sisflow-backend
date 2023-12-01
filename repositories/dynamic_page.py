""" Defines the Dynamic Page repository """

from models import DynamicPage

def format_dynamic_component(system_configuration, student_token, advisor_token, comp):
    """ Format a component by its type """
    formated_comp = None

    if comp.type == "inner_html":
        formated_comp = format_dc_inner_html(system_configuration, student_token, advisor_token, comp)
    elif comp.type == "input":
        formated_comp = format_dc_input(comp)
    elif comp.type == "upload":
        formated_comp = format_dc_upload(comp)
    elif comp.type == "select":
        formated_comp = format_dc_select(comp)
    elif comp.type == "select_upload":
        formated_comp = format_dc_select_upload(comp)
    elif comp.type == "download":
        formated_comp = format_dc_download(comp)
    elif comp.type == "button":
        formated_comp = format_dc_button(comp)
    elif comp.type == "details":
        formated_comp = format_dc_details(comp)

    formated_comp["component_id"] = comp.id
    formated_comp["component_type"] = comp.type
    
    return formated_comp

def format_dc_inner_html(system_configuration, student_token, advisor_token, comp):
    """ Format a inner_html component """
    return {
        "inner_html": system_configuration.sistem_str_parser(comp.dynamic_component_inner_html.inner_html, student_token, advisor_token)
    }

def format_dc_input(comp):
    """ Format a input component """

    # basic format
    c_input = comp.dynamic_component_input
    formated_comp = {
        "input_name": c_input.input_name,
        "input_type": c_input.input_type,
        "input_required": c_input.input_required,
        "input_missing_message": c_input.input_missing_message
    }

    # date rule formatting
    if c_input.input_type == "date":
        formated_comp["input_date_rules"] = []

        for input_date_rule in c_input.dynamic_component_input_date_rule:
            formated_comp["input_date_rules"].append({
                "rule_type": input_date_rule.rule_type,
                "rule_message_type": input_date_rule.rule_message_type,
                "rule_start_days": input_date_rule.rule_start_days,
                "rule_end_days": input_date_rule.rule_end_days,
                "rule_missing_message": input_date_rule.rule_missing_message
            })
    
    return formated_comp

def format_dc_upload(comp):
    """ Format a upload component """
    c_upload = comp.dynamic_component_upload
    return {
        "upload_label": c_upload.upload_label,
        "upload_name": c_upload.upload_name,
        "upload_required": c_upload.upload_required,
        "upload_missing_message": c_upload.upload_missing_message
    }
    
def format_dc_select(comp):
    """ Format a select component """

    # basic format
    c_select = comp.dynamic_component_select
    formated_comp = {
        "select_name": c_select.select_name,
        "select_label": c_select.select_label,
        "select_initial_text": c_select.select_initial_text,
        "is_select_required": c_select.is_select_required,
        "select_missing_message": c_select.select_missing_message,
        "select_options": []
    }
    
    # option formatting
    for option in c_select.dynamic_component_select_option:
        formated_comp["select_options"].append({
            "label": option.select_option_label,
            "value": option.select_option_value
        })

    return formated_comp

def format_dc_select_upload(comp):
    """ Format a select upload component """

    # basic format
    c_select = comp.dynamic_component_select_upload.dynamic_component_select
    formated_comp = {
        "select_id": c_select.dynamic_component_id,
        "select_upload_name": c_select.select_name,
        "select_upload_label": c_select.select_label,
        "select_upload_initial_text": c_select.select_initial_text,
        "select_upload_required": c_select.is_select_required,
        "select_upload_missing_message": c_select.select_missing_message,
        "select_upload_options": []
    }
    
    # option formatting
    for option in c_select.dynamic_component_select_option:
        formated_comp["select_upload_options"].append({
            "label": option.select_option_label,
            "value": option.select_option_value
        })
    
    return formated_comp

def format_dc_download(comp):
    """ Format a download component """
    c_download = comp.dynamic_component_download
    return {
        "download_label": c_download.download_label,
        "download_from": c_download.download_from,
        "internal_upload_name": c_download.internal_upload_name,
        "internal_select_upload_name": c_download.internal_select_upload_name,
        "external_download_link": c_download.external_download_link
    }
    
def format_dc_button(comp):
    """ Format a button component """
    c_button = comp.dynamic_component_button
    return {
        "button_label": c_button.button_label,
        "button_color": c_button.button_color,
        "button_transation_type": c_button.button_transation_type
    }
    
def format_dc_details(comp):
    """ Format a details component """
    return {
        "details_type": comp.dynamic_component_details.details_type
    }

class DynamicPageRepository:
    """ The repository for a single dynamic page """

    @staticmethod
    def read_dynamic_page(system_configuration, student_token, advisor_token, id, format=True):
        """ Query and format a dynamic page by id """
        dp = None

        # query and validate
        dp_query = DynamicPage.query.filter_by(id=id)
        if dp_query.count() == 1:
            dp = dp_query.one()
        
        # if not format
        if not format or not dp:
            return dp

        # format
        formated_dp = {
            "id": dp.id,
            "title": dp.title,
            "components": []
        }
        for dp_has_comp in dp.dynamic_page_has_component:
            dynamic_component = dp_has_comp.dynamic_component
            formated_comp = format_dynamic_component(system_configuration, student_token, advisor_token, dynamic_component)
            formated_comp["component_order"] = dp_has_comp.dynamic_component_order
            formated_dp["components"].append(formated_comp)
        
        return formated_dp
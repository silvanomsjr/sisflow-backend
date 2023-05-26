from flask import Flask, abort, request
from flask_restful import Resource, Api, reqparse

from utils.dbUtils import *
from utils.cryptoFunctions import isAuthTokenValid
from utils.utils import sistemStrParser

def getDynamicPage(pageId, studentData=None, advisorData=None):

  dpQuery = None
  try:
    dpQuery = dbGetSingle(
      " SELECT * FROM dynamic_page dp "
      "   WHERE dp.id = %s; ",
      (pageId,))
  except Exception as e:
    print("# Database reading error:")
    print(str(e))
    return "Erro na base de dados", 409

  if not dpQuery:
    return "Pagina não encontrada", 404
  
  dpQuery['components'] = loadPageComponents(pageId, studentData, advisorData)
  
  return dpQuery

def loadPageComponents(pageId, studentData=None, advisorData=None):

  useParser = studentData!=None

  pageComponentsQuery = dbGetAll(
    " SELECT dphc.dynamic_component_order AS component_order, "
    " dc.id AS component_id, dc.type AS component_type, "
    " dc_inner_html.inner_html, "
    " dc_input.input_name, dc_input.input_type, dc_input.input_required, dc_input.input_missing_message, "
    " dc_upload.upload_label, dc_upload.upload_name, dc_upload.upload_required, dc_upload.upload_missing_message, "
    " dc_select.select_name, dc_select.select_label, dc_select.select_initial_text, dc_select.is_select_required, dc_select.select_missing_message, "
    " dcsupload_select.dynamic_component_id AS select_upload_select_id, dcsupload_select.select_name AS select_upload_select_name, "
    " dcsupload_select.select_label AS select_upload_select_label, dcsupload_select.select_initial_text AS select_upload_select_initial_text, "
    " dcsupload_select.is_select_required AS select_upload_is_select_required, dcsupload_select.select_missing_message AS select_upload_select_missing_message, "
    " dc_download.download_label, dc_download.download_from, dc_download.internal_upload_name, dc_download.internal_select_upload_name, dc_download.external_download_link, "
    " dc_button.button_label, dc_button.button_color, dc_button.button_transation_type, "
    " dc_details.details_type "
    "   FROM dynamic_page AS dp "
    "     JOIN dynamic_page_has_component AS dphc ON dp.id = dphc.dynamic_page_id "
    "     JOIN dynamic_component AS dc ON dphc.dynamic_component_id = dc.id "
    "     LEFT JOIN dynamic_component_inner_html AS dc_inner_html ON dc.id = dc_inner_html.dynamic_component_id "
    "     LEFT JOIN dynamic_component_input AS dc_input ON dc.id = dc_input.dynamic_component_id "
    "     LEFT JOIN dynamic_component_upload AS dc_upload ON dc.id = dc_upload.dynamic_component_id "
    "     LEFT JOIN dynamic_component_select AS dc_select ON dc.id = dc_select.dynamic_component_id "
    "     LEFT JOIN dynamic_component_select_upload AS dc_select_upload ON dc.id = dc_select_upload.dynamic_component_id "
    "     LEFT JOIN dynamic_component_select AS dcsupload_select ON dc_select_upload.dynamic_component_select_name = dcsupload_select.select_name "
    "     LEFT JOIN dynamic_component_download AS dc_download ON dc.id = dc_download.dynamic_component_id "
    "     LEFT JOIN dynamic_component_button AS dc_button ON dc.id = dc_button.dynamic_component_id "
    "     LEFT JOIN dynamic_component_details AS dc_details ON dc.id = dc_details.dynamic_component_id "
    "   WHERE dp.id = %s "
    "   ORDER BY dphc.dynamic_component_order; ",
    (pageId,))
  
  if not pageComponentsQuery:
    raise Exception("No return for dynamic_page in get single solicitation ")
  
  # copy from query result to avoid empty fields
  pageComponents = []
  for componentQ in pageComponentsQuery:

    component = {}
    component["component_order"] = componentQ["component_order"]
    component["component_id"] = componentQ["component_id"]
    component["component_type"] = componentQ["component_type"]

    if component["component_type"] == "inner_html":
      component["inner_html"] = sistemStrParser(componentQ["inner_html"], studentData) if useParser else componentQ["inner_html"]

    if component["component_type"] == "input":
      component["input_name"] = componentQ["input_name"]
      component["input_type"] = componentQ["input_type"]
      component["input_required"] = componentQ["input_required"]
      component["input_missing_message"] = componentQ["input_missing_message"]

      if component["input_type"] == "date":

        rawInputDateRules = dbGetAll(
          " SELECT rule_type, rule_message_type, rule_start_days, rule_end_days, rule_missing_message "
          "   FROM dynamic_component_input AS dc_input "
          "     JOIN dynamic_component_input_date_rule AS dc_input_date_rules ON dc_input.dynamic_component_id = dc_input_date_rules.dynamic_component_input_id "
          "   WHERE dc_input.dynamic_component_id = %s; ",
          [(component["component_id"])])

        if rawInputDateRules:
          component["input_date_rules"] = rawInputDateRules

    if component["component_type"] == "upload":
      component["upload_label"] = componentQ["upload_label"]
      component["upload_name"] = componentQ["upload_name"]
      component["upload_required"] = componentQ["upload_required"]
      component["upload_missing_message"] = componentQ["upload_missing_message"]
    
    if component["component_type"] == "select":
      component["select_name"] = componentQ["select_name"]
      component["select_label"] = componentQ["select_label"]
      component["select_initial_text"] = componentQ["select_initial_text"]
      component["is_select_required"] = componentQ["is_select_required"]
      component["select_missing_message"] = componentQ["select_missing_message"]

      rawSelectOpts = dbGetAll(
        " SELECT select_option_label AS option_label, select_option_value AS option_value "
        "   FROM dynamic_component_select AS dc_select "
        "     JOIN dynamic_component_select_option AS dc_select_option ON dc_select.dynamic_component_id = dc_select_option.dynamic_component_select_id "
        "   WHERE dc_select.dynamic_component_id = %s; ",
        [(component["component_id"])])

      component["select_options"] = rawSelectOpts

    if component["component_type"] == "select_upload":
      component["select_id"] = componentQ["select_upload_select_id"]
      component["select_upload_name"] = componentQ["select_upload_select_name"]
      component["select_upload_label"] = componentQ["select_upload_select_label"]
      component["select_upload_initial_text"] = componentQ["select_upload_select_initial_text"]
      component["select_upload_required"] = componentQ["select_upload_is_select_required"]
      component["select_upload_missing_message"] = componentQ["select_upload_select_missing_message"]

      rawSelectUploadOptions = dbGetAll(
        " SELECT select_option_label AS label, select_option_value AS value "
        "   FROM dynamic_component_select AS dc_select "
        "     JOIN dynamic_component_select_option AS dc_select_option ON dc_select.dynamic_component_id = dc_select_option.dynamic_component_select_id "
        "   WHERE dc_select.dynamic_component_id = %s; ",
        [(component["select_id"])])

      component['select_upload_options'] = rawSelectUploadOptions

    if component["component_type"] == "download":
      component["download_label"] = componentQ["download_label"]
      component["download_from"] = componentQ["download_from"]
      component["internal_upload_name"] = componentQ["internal_upload_name"]
      component["internal_select_upload_name"] = componentQ["internal_select_upload_name"]
      component["external_download_link"] = componentQ["external_download_link"]
      
    if component["component_type"] == "button":
      component["button_label"] = componentQ["button_label"]
      component["button_color"] = componentQ["button_color"]
      component["button_transation_type"] = componentQ["button_transation_type"]
    
    if component["component_type"] == "details":
      component["details_type"] = componentQ["details_type"]
    
    # index by component order
    pageComponents.append(component)
  
  return pageComponents

# Data from dynamic pages
class DynamicPage(Resource):

  # get dynamic page data
  def get(self):

    args = reqparse.RequestParser()
    args.add_argument("Authorization", location="headers", type=str, help="Bearer with jwt given by server in user autentication, required", required=True)
    args.add_argument("advisor_data", location="args", type=object)
    args.add_argument("student_data", location="args", type=object)
    args.add_argument("page_id", location="args", type=int, required=True)
    args = args.parse_args()

    # verify jwt and its signature correctness
    isTokenValid, errorMsg, tokenData = isAuthTokenValid(args)
    if not isTokenValid:
      abort(401, errorMsg)

    print("\n# Starting get dynamic page\n# Reading data from DB")
    dpData = getDynamicPage(args["page_id"], args["student_data"], args["advisor_data"])
    print("# Operation Done!")
    
    return dpData, 200
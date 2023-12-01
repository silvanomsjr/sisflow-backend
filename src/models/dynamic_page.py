"""
The Dynamic Page category models
"""
from . import db
from .base import BaseModel, MetaBaseModel

class DynamicPage(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_page"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)

    dynamic_page_has_component = db.Relationship("DynamicPageHasComponent", 
        order_by="DynamicPageHasComponent.dynamic_component_order.asc()", backref="dynamic_page") # 1-N

    """ Create a new DynamicPage """
    def __init__(self, title):
        self.title = title

class DynamicComponent(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component"
    __table_args__ = (db.UniqueConstraint("id", "type"),) # unique used for foreign key

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)

    # relations with the components
    dynamic_component_inner_html = db.Relationship("DynamicComponentInnerHtml", backref="dynamic_component", uselist=False)       # 1-1
    dynamic_component_input = db.Relationship("DynamicComponentInput", backref="dynamic_component", uselist=False)                # 1-1
    dynamic_component_upload = db.Relationship("DynamicComponentUpload", backref="dynamic_component", uselist=False)              # 1-1
    dynamic_component_select = db.Relationship("DynamicComponentSelect", backref="dynamic_component", uselist=False)              # 1-1
    dynamic_component_select_upload = db.Relationship("DynamicComponentSelectUpload", backref="dynamic_component", uselist=False) # 1-1
    dynamic_component_download = db.Relationship("DynamicComponentDownload", backref="dynamic_component", uselist=False)          # 1-1
    dynamic_component_button = db.Relationship("DynamicComponentButton", backref="dynamic_component", uselist=False)              # 1-1
    dynamic_component_details = db.Relationship("DynamicComponentDetails", backref="dynamic_component", uselist=False)            # 1-1

    # relation with page has components    
    dynamic_page_has_component = db.Relationship("DynamicPageHasComponent", backref="dynamic_component", uselist=False) # 1-1

    """ Create a new DynamicComponent """
    def __init__(self, type):
        self.type = type

class DynamicPageHasComponent(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_page_has_component"
    __table_args__ = (
        db.UniqueConstraint("id", "dynamic_component_id"), # unique used for foreign key
        db.UniqueConstraint("dynamic_page_id", "dynamic_component_id"),
        db.UniqueConstraint("dynamic_page_id", "dynamic_component_order"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dynamic_page_id = db.Column(db.Integer,  db.ForeignKey("dynamic_page.id"), nullable=False)
    dynamic_component_id = db.Column(db.Integer, db.ForeignKey("dynamic_component.id"), nullable=False)
    dynamic_component_order = db.Column(db.Integer, nullable=False)

    """ Create a new dynamicPageHasComponent """
    def __init__(self, dynamic_page_id, dynamic_component_id, dynamic_component_order):
        self.dynamic_page_id = dynamic_page_id
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_order = dynamic_component_order

class DynamicComponentInnerHtml(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_inner_html"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"], 
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.CheckConstraint("dynamic_component_type = 'inner_html'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    inner_html = db.Column(db.String(2000), nullable=False)

    """ Create a new DynamicComponentInnerHtml """
    def __init__(self, dynamic_component_id, inner_html, dynamic_component_type="inner_html"):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.inner_html = inner_html

class DynamicComponentInput(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_input"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"], 
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.UniqueConstraint("dynamic_component_id", "input_type"), # unique used for foreign key
        db.CheckConstraint("dynamic_component_type = 'input'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    input_name = db.Column(db.String(100), unique=True, nullable=False)
    input_type = db.Column(db.Enum("text", "date"), nullable=False)
    input_required = db.Column(db.Boolean, nullable=False)
    input_missing_message = db.Column(db.String(200), nullable=False)

    # relation with date rules
    dynamic_component_input_date_rule = db.Relationship("DynamicComponentInputDateRule", backref="dynamic_component_input") # 1-N

    """ Create a new DynamicComponentInput """
    def __init__(self, dynamic_component_id, input_name, input_type, input_missing_message, 
        dynamic_component_type="input", input_required=True):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.input_name = input_name
        self.input_type = input_type
        self.input_required = input_required
        self.input_missing_message = input_missing_message

class DynamicComponentInputDateRule(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_input_date_rule"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_input_id", "dynamic_component_input_type"], 
            ["dynamic_component_input.dynamic_component_id", "dynamic_component_input.input_type"]
        ),
        db.CheckConstraint("dynamic_component_input_type = 'date'")
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dynamic_component_input_id = db.Column(db.Integer, nullable=False)
    dynamic_component_input_type = db.Column(db.Enum("text", "date"), nullable=False)
    rule_type = db.Column(db.Enum("must-be-from-today", "must-not-be-from-today"), nullable=False)
    rule_message_type = db.Column(db.Enum("warn", "error"), nullable=False)
    rule_start_days = db.Column(db.Integer)
    rule_end_days = db.Column(db.Integer)
    rule_missing_message = db.Column(db.String(200))

    """ Create a new DynamicComponentInputDateRule """
    def __init__(self, dynamic_component_input_id, rule_type, rule_message_type, 
        dynamic_component_input_type="date", rule_start_days=None, rule_end_days=None, rule_missing_message=None):
        self.dynamic_component_input_id = dynamic_component_input_id
        self.dynamic_component_input_type = dynamic_component_input_type
        self.rule_type = rule_type
        self.rule_message_type = rule_message_type
        self.rule_start_days = rule_start_days
        self.rule_end_days = rule_end_days
        self.rule_missing_message = rule_missing_message

class DynamicComponentUpload(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_upload"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"], 
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.CheckConstraint("dynamic_component_type = 'upload'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    upload_label = db.Column(db.String(100), nullable=False)
    upload_name = db.Column(db.String(30), unique=True, nullable=False)
    upload_required = db.Column(db.Boolean, nullable=False)
    upload_missing_message = db.Column(db.String(200), nullable=False)

    # relation with its download
    dynamic_component_download = db.Relationship("DynamicComponentDownload", 
        backref="dynamic_component_upload", uselist=False) # 1-1

    """ Create a new DynamicComponentUpload """
    def __init__(self, dynamic_component_id, upload_label, upload_name, upload_missing_message, 
        dynamic_component_type="upload", upload_required=True):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.upload_label = upload_label
        self.upload_name = upload_name
        self.upload_required = upload_required
        self.upload_missing_message = upload_missing_message

class DynamicComponentSelect(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_select"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"], 
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.CheckConstraint("dynamic_component_type = 'select'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    select_name = db.Column(db.String(30), unique=True, nullable=False)
    select_label = db.Column(db.String(100), nullable=False)
    select_initial_text = db.Column(db.String(30), nullable=False)
    select_missing_message = db.Column(db.String(200), nullable=False)
    is_select_required = db.Column(db.Boolean, nullable=False)

    # relation with its possible options or upload
    dynamic_component_select_option = db.Relationship("DynamicComponentSelectOption", 
        backref="dynamic_component_select")                 # 1-N
    dynamic_component_select_upload = db.Relationship("DynamicComponentSelectUpload", 
        backref="dynamic_component_select", uselist=False)  # 1-1

    """ Create a new DynamicComponentSelect """
    def __init__(self, dynamic_component_id, select_name, select_label, select_missing_message, 
        dynamic_component_type="select", is_select_required=True, select_initial_text="Selecione: "):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.select_name = select_name
        self.select_label = select_label
        self.select_initial_text = select_initial_text
        self.select_missing_message = select_missing_message
        self.is_select_required = is_select_required

class DynamicComponentSelectOption(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_select_option"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dynamic_component_select_id = db.Column(db.Integer, 
        db.ForeignKey("dynamic_component_select.dynamic_component_id"), nullable=False)
    select_option_label = db.Column(db.String(30), nullable=False)
    select_option_value = db.Column(db.String(30))

    """ Create a new DynamicComponentSelectOption """
    def __init__(self, dynamic_component_select_id, select_option_label="Selecione: ", select_option_value=None):
        self.dynamic_component_select_id = dynamic_component_select_id
        self.select_option_label = select_option_label
        self.select_option_value = select_option_value

class DynamicComponentSelectUpload(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_select_upload"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"], 
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.CheckConstraint("dynamic_component_type = 'select_upload'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    dynamic_component_select_name = db.Column(db.String(30), 
        db.ForeignKey("dynamic_component_select.select_name"), unique=True, nullable=False)

    # relation with its download
    dynamic_component_download = db.Relationship("DynamicComponentDownload", 
        backref="dynamic_component_select_upload", uselist=False) # 1-1

    """ Create a new DynamicComponentSelectUpload """
    def __init__(self, dynamic_component_id, dynamic_component_select_name, dynamic_component_type="select_upload"):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.dynamic_component_select_name = dynamic_component_select_name

class DynamicComponentDownload(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_download"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"],
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.CheckConstraint("\
            (download_from = 'internal_from_upload' AND internal_upload_name IS NOT NULL AND \
                internal_select_upload_name IS NULL AND external_download_link IS NULL) \
            OR (download_from = 'internal_from_select_upload' AND internal_upload_name IS NULL AND \
                internal_select_upload_name IS NOT NULL AND external_download_link IS NULL) \
            OR (download_from = 'external_from_link' AND internal_upload_name IS NULL AND \
                internal_select_upload_name IS NULL AND external_download_link IS NOT NULL) \
        "),
        db.CheckConstraint("dynamic_component_type = 'download'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    download_label = db.Column(db.String(100))
    download_from = db.Column(db.Enum("internal_from_upload", "internal_from_select_upload", 
        "external_from_link"), nullable=False)
    internal_upload_name = db.Column(db.String(30), db.ForeignKey("dynamic_component_upload.upload_name"))
    internal_select_upload_name = db.Column(db.String(30), 
        db.ForeignKey("dynamic_component_select_upload.dynamic_component_select_name"))
    external_download_link = db.Column(db.String(500))

    """ Create a new DynamicComponentDownload """
    def __init__(self, dynamic_component_id, download_from, dynamic_component_type="download", 
        download_label=None, internal_upload_name=None, internal_select_upload_name=None, external_download_link=None):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.download_label = download_label
        self.download_from = download_from
        self.internal_upload_name = internal_upload_name
        self.internal_select_upload_name = internal_select_upload_name
        self.external_download_link = external_download_link

class DynamicComponentButton(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_button"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"], 
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.CheckConstraint("dynamic_component_type = 'button'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    button_label = db.Column(db.String(100), nullable=False)
    button_color = db.Column(db.Enum("darkblue", "red", "black"), nullable=False)
    button_transation_type = db.Column(db.Enum("Request", "Cancel", "Send", "Send and Defer", 
        "Defer", "Reject"), nullable=False)

    """ Create a new DynamicComponentButton """
    def __init__(self, dynamic_component_id, button_label, button_color, button_transation_type, dynamic_component_type="button"):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.button_label = button_label
        self.button_color = button_color
        self.button_transation_type = button_transation_type

class DynamicComponentDetails(db.Model, BaseModel, metaclass=MetaBaseModel):
    
    __tablename__ = "dynamic_component_details"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["dynamic_component_id", "dynamic_component_type"], 
            ["dynamic_component.id", "dynamic_component.type"]
        ),
        db.CheckConstraint("dynamic_component_type = 'details'")
    )

    dynamic_component_id = db.Column(db.Integer, primary_key=True)
    dynamic_component_type = db.Column(db.Enum("inner_html", "input", "upload", "download",
        "select", "select_upload", "button", "details"), nullable=False)
    details_type = db.Column(db.Enum("student", "advisor"), nullable=False)

    """ Create a new DynamicComponentDetails """
    def __init__(self, dynamic_component_id, details_type, dynamic_component_type="details"):
        self.dynamic_component_id = dynamic_component_id
        self.dynamic_component_type = dynamic_component_type
        self.details_type = details_type
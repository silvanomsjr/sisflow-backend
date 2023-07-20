CREATE SCHEMA IF NOT EXISTS sisgesteste;
USE sisgesteste;

/* Sistem configurations */
CREATE TABLE config(
	id INT NOT NULL AUTO_INCREMENT,
    config_name VARCHAR(50),
    PRIMARY KEY (id)
);
CREATE TABLE config_system_path(
	config_id INT NOT NULL,
	system_path VARCHAR(256),
    PRIMARY KEY (config_id),
    FOREIGN KEY (config_id) REFERENCES config(id)
);
CREATE TABLE config_mail(
    config_id INT NOT NULL,
    mail VARCHAR(256) NOT NULL UNIQUE,
    mail_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (config_id),
    FOREIGN KEY (config_id) REFERENCES config(id)
);
CREATE TABLE config_year(
    config_id INT NOT NULL,
    year INT NOT NULL UNIQUE,
    PRIMARY KEY (config_id),
    FOREIGN KEY (config_id) REFERENCES config(id)
);
CREATE TABLE config_year_holiday(
    id INT NOT NULL AUTO_INCREMENT,
    year INT NOT NULL,
    get_by ENUM('API', 'Personalized'),
    holiday_name VARCHAR(50) NOT NULL UNIQUE,
    holiday_date DATE NOT NULL UNIQUE,
    PRIMARY KEY (id),
    FOREIGN KEY (year) REFERENCES config_year(year)
);
CREATE TABLE config_reason_class(
	config_id INT NOT NULL,
    class_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (config_id),
    FOREIGN KEY (config_id) REFERENCES config(id)
);
CREATE TABLE config_reason(
	id INT NOT NULL AUTO_INCREMENT,
	reason_class_id INT NOT NULL,
    inner_html VARCHAR(2000) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (reason_class_id) REFERENCES config_reason_class(config_id)
);

/* User data and Profiles */
CREATE TABLE user_account(
	id INT NOT NULL AUTO_INCREMENT,
    institutional_email VARCHAR(256) NOT NULL UNIQUE,
    secondary_email VARCHAR(256),
    user_name VARCHAR(100) NOT NULL,
    gender ENUM('M', 'F') NOT NULL,
    phone VARCHAR(15),
    password_hash CHAR(65),
    password_salt CHAR(16),
    creation_datetime DATETIME,
    PRIMARY KEY (id)
);
CREATE TABLE profile(
	id INT NOT NULL AUTO_INCREMENT,
    profile_name VARCHAR(50) UNIQUE,
    profile_acronym CHAR(3) UNIQUE,
    profile_dynamic_fields_metadata JSON,
    PRIMARY KEY (id)
);
CREATE TABLE user_has_profile(
	id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    profile_id INT NOT NULL,
    user_dinamyc_profile_fields_data JSON,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME,
	PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user_account(id),
    FOREIGN KEY (profile_id) REFERENCES profile(id),
    UNIQUE (user_id, profile_id)
);
CREATE TABLE user_has_profile_coordinator_data(
	user_has_profile_id INT NOT NULL,
    siape VARCHAR(15) NOT NULL UNIQUE,
    PRIMARY KEY (user_has_profile_id),
    FOREIGN KEY (user_has_profile_id) REFERENCES user_has_profile(id)
);
CREATE TABLE user_has_profile_advisor_data(
	user_has_profile_id INT NOT NULL,
    siape VARCHAR(15) NOT NULL UNIQUE,
	PRIMARY KEY (user_has_profile_id),
    FOREIGN KEY (user_has_profile_id) REFERENCES user_has_profile(id)
);
CREATE TABLE user_has_profile_student_data(
	user_has_profile_id INT NOT NULL,
    matricula VARCHAR(15) NOT NULL UNIQUE,
    course ENUM('BCC', 'BSI') NOT NULL,
    PRIMARY KEY (user_has_profile_id),
    FOREIGN KEY (user_has_profile_id) REFERENCES user_has_profile(id)
);

/* Attachments */
CREATE TABLE attachment(
	id INT NOT NULL AUTO_INCREMENT,
	hash_name VARCHAR(150) NOT NULL UNIQUE,
    PRIMARY KEY (id)
);
CREATE TABLE user_has_attachment(
	id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    attachment_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user_account(id),
    FOREIGN KEY (attachment_id) REFERENCES attachment(id)
);

/* Security sigin code */
CREATE TABLE mail_validation(
	institutional_email VARCHAR(256) NOT NULL,
    validation_code CHAR(10),
    validation_code_expires_in TIMESTAMP,
    PRIMARY KEY (institutional_email),
    FOREIGN KEY (institutional_email) REFERENCES user_account(institutional_email)
);
CREATE TRIGGER set_mail_validation_code_expires_in BEFORE INSERT ON mail_validation 
    FOR EACH ROW 
    SET NEW.validation_code_expires_in = NOW() + INTERVAL 8 HOUR;
CREATE EVENT mail_validation_code_expiration
	ON SCHEDULE EVERY 1 HOUR
	COMMENT 'Remove mail validation codes after it expires'
	DO DELETE FROM mail_validation WHERE validation_code_expires_in < NOW();

/* Dynamic page and its associated data  */
CREATE TABLE dynamic_page(
	id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(256) NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE dynamic_component(
    id INT NOT NULL AUTO_INCREMENT,
    type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (id, type)
);
CREATE TABLE dynamic_page_has_component(
	id INT NOT NULL AUTO_INCREMENT,
    dynamic_page_id INT NOT NULL,
    dynamic_component_id INT NOT NULL,
    dynamic_component_order INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (dynamic_page_id) REFERENCES dynamic_page(id),
    FOREIGN KEY (dynamic_component_id) REFERENCES dynamic_component(id),
    UNIQUE (id, dynamic_component_id),
    UNIQUE (dynamic_page_id, dynamic_component_id),
    UNIQUE (dynamic_page_id, dynamic_component_order)
);
CREATE TABLE dynamic_component_inner_html(
	dynamic_component_id INT NOT NULL,
    dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    inner_html VARCHAR(2000) NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'inner_html')
);
CREATE TABLE dynamic_component_input(
    dynamic_component_id INT NOT NULL,
    dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    input_name VARCHAR(100) UNIQUE NOT NULL,
    input_type ENUM('text', 'date') NOT NULL,
    input_required BOOL DEFAULT TRUE NOT NULL,
    input_missing_message VARCHAR(200) NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    UNIQUE (dynamic_component_id, input_type),
    CHECK (dynamic_component_type = 'input')
);
CREATE TABLE dynamic_component_input_date_rule(
    id INT NOT NULL AUTO_INCREMENT,
    dynamic_component_input_id INT NOT NULL,
    dynamic_component_input_type ENUM('text', 'date') NOT NULL,
    rule_type ENUM('must-be-from-today', 'must-not-be-from-today') NOT NULL,
    rule_message_type ENUM('warn', 'error') NOT NULL,
    rule_start_days INT,
    rule_end_days INT,
    rule_missing_message VARCHAR(200),
    PRIMARY KEY (id),
    FOREIGN KEY (dynamic_component_input_id, dynamic_component_input_type) REFERENCES dynamic_component_input(dynamic_component_id, input_type),
    CHECK (dynamic_component_input_type = 'date')
);
CREATE TABLE dynamic_component_upload(
    dynamic_component_id INT NOT NULL,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    upload_label VARCHAR(100) NOT NULL,
    upload_name VARCHAR(30) UNIQUE NOT NULL,
    upload_required BOOL DEFAULT TRUE NOT NULL,
    upload_missing_message VARCHAR(200) NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'upload')
);
CREATE TABLE dynamic_component_select(
    dynamic_component_id INT NOT NULL,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    select_name VARCHAR(30) NOT NULL UNIQUE,
    select_label VARCHAR(100) NOT NULL,
    select_initial_text VARCHAR(30) DEFAULT 'Selecione: ' NOT NULL,
    is_select_required BOOL DEFAULT TRUE NOT NULL,
    select_missing_message VARCHAR(200) NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'select')
);
CREATE TABLE dynamic_component_select_option(
	id INT NOT NULL AUTO_INCREMENT,
    dynamic_component_select_id INT NOT NULL,
    select_option_label VARCHAR(30) DEFAULT 'Selecione: ' NOT NULL,
    select_option_value VARCHAR(30),
    PRIMARY KEY (id),
    FOREIGN KEY (dynamic_component_select_id) REFERENCES dynamic_component_select(dynamic_component_id)
);
CREATE TABLE dynamic_component_select_upload(
    dynamic_component_id INT NOT NULL,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    dynamic_component_select_name VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    FOREIGN KEY (dynamic_component_select_name) REFERENCES dynamic_component_select(select_name),
    CHECK (dynamic_component_type = 'select_upload')
);
CREATE TABLE dynamic_component_download(
    dynamic_component_id INT NOT NULL,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    download_label VARCHAR(100),
    download_from ENUM ('internal_from_upload', 'internal_from_select_upload', 'external_from_link') NOT NULL,
    internal_upload_name VARCHAR(30),
    internal_select_upload_name VARCHAR(30),
    external_download_link VARCHAR(500),
    CHECK (
		(download_from = 'internal_from_upload' AND internal_upload_name IS NOT NULL AND internal_select_upload_name IS NULL AND external_download_link IS NULL)
        OR (download_from = 'internal_from_select_upload' AND internal_upload_name IS NULL AND internal_select_upload_name IS NOT NULL AND external_download_link IS NULL)
        OR (download_from = 'external_from_link' AND internal_upload_name IS NULL AND internal_select_upload_name IS NULL AND external_download_link IS NOT NULL)
	),
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    FOREIGN KEY (internal_upload_name) REFERENCES dynamic_component_upload(upload_name),
    FOREIGN KEY (internal_select_upload_name) REFERENCES dynamic_component_select_upload(dynamic_component_select_name),
    CHECK (dynamic_component_type = 'download')
);
CREATE TABLE dynamic_component_button(
	dynamic_component_id INT NOT NULL,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    button_label VARCHAR(100) NOT NULL,
    button_color ENUM('darkblue', 'red', 'black') NOT NULL,
    button_transation_type ENUM('Request', 'Cancel', 'Send', 'Send and Defer', 'Defer', 'Reject') NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'button')
);
CREATE TABLE dynamic_component_details(
	dynamic_component_id INT NOT NULL,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button', 'details') NOT NULL,
    details_type ENUM('student', 'advisor') NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'details')
);

/* Dynamic mail message */
CREATE TABLE dynamic_mail(
	id INT NOT NULL AUTO_INCREMENT,
    mail_subject VARCHAR(100),
    mail_body_html VARCHAR(2000),
    is_sent_to_student BOOL DEFAULT FALSE,
    is_sent_to_advisor BOOL DEFAULT FALSE,
    is_sent_to_coordinator BOOL DEFAULT FALSE,
    PRIMARY KEY (id)
);

/* Solicitation and its associated data - Solicitation is the state machine */
CREATE TABLE solicitation(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_name VARCHAR(256),
    PRIMARY KEY (id)
);
CREATE TABLE solicitation_start_mail(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_id INT NOT NULL,
    dynamic_mail_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_id) REFERENCES solicitation(id),
    FOREIGN KEY (dynamic_mail_id) REFERENCES dynamic_mail(id)
);
CREATE TABLE solicitation_state(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_id INT NOT NULL,
    state_description VARCHAR(256),
    state_max_duration_days INT,
    state_dynamic_page_id INT,
    state_static_page_name VARCHAR(100),
    is_initial_state BOOL NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_id) REFERENCES solicitation(id),
    FOREIGN KEY (state_dynamic_page_id) REFERENCES dynamic_page(id)
);
CREATE TABLE solicitation_state_profile_editors(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_state_id INT NOT NULL,
    state_profile_editor INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_state_id) REFERENCES solicitation_state(id),
    FOREIGN KEY (state_profile_editor) REFERENCES profile(id)
);
CREATE TABLE solicitation_state_transition(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_state_id_from INT NOT NULL,
    solicitation_state_id_to INT,
    transition_name VARCHAR(30) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_state_id_from) REFERENCES solicitation_state(id),
    FOREIGN KEY (solicitation_state_id_to) REFERENCES solicitation_state(id)
);
CREATE TABLE solicitation_state_transition_manual(
	solicitation_state_transition_id INT NOT NULL,
    transition_decision ENUM('Em analise', 'Solicitado', 'Enviado', 'Deferido', 'Indeferido', 'Cancelado pelo aluno', 'Cancelado pelo orientador', 'Cancelado pela coordenação', 'Expirado') DEFAULT 'Em analise' NOT NULL,
    transition_reason VARCHAR(100) NOT NULL,
    PRIMARY KEY (solicitation_state_transition_id),
    FOREIGN KEY (solicitation_state_transition_id) REFERENCES solicitation_state_transition(id)
);
CREATE TABLE solicitation_state_transition_from_dynamic_page(
	solicitation_state_transition_id INT NOT NULL,
    dynamic_page_component ENUM('Button-Request', 'Button-Cancel', 'Button-Send', 'Button-Send and Defer', 'Button-Defer', 'Button-Reject', 'Table-Cancel') NOT NULL,
	transition_decision ENUM('Em analise', 'Solicitado', 'Enviado', 'Deferido', 'Indeferido', 'Cancelado pelo aluno', 'Cancelado pelo orientador', 'Cancelado pela coordenação', 'Expirado') DEFAULT 'Em analise' NOT NULL,
    transition_reason VARCHAR(100) NOT NULL,
    PRIMARY KEY (solicitation_state_transition_id),
    FOREIGN KEY (solicitation_state_transition_id) REFERENCES solicitation_state_transition(id)
);
CREATE TABLE solicitation_state_transition_scheduled(
	solicitation_state_transition_id INT NOT NULL,
    transition_decision ENUM('Em analise', 'Solicitado', 'Enviado', 'Deferido', 'Indeferido', 'Cancelado pelo aluno', 'Cancelado pelo orientador', 'Cancelado pela coordenação', 'Expirado') DEFAULT 'Em analise' NOT NULL,
    transition_reason VARCHAR(100) NOT NULL,
    transition_delay_seconds INT NOT NULL,
    PRIMARY KEY (solicitation_state_transition_id),
    FOREIGN KEY (solicitation_state_transition_id) REFERENCES solicitation_state_transition(id)
);
CREATE TABLE solicitation_state_transition_mail(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_state_transition_id INT NOT NULL,
    dynamic_mail_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_state_transition_id) REFERENCES solicitation_state_transition(id),
    FOREIGN KEY (dynamic_mail_id) REFERENCES dynamic_mail(id)
);
CREATE TABLE user_has_solicitation(
	id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    advisor_siape VARCHAR(15),
    is_accepted_by_advisor BOOL DEFAULT FALSE,
    solicitation_id INT NOT NULL,
    actual_solicitation_state_id INT NOT NULL,
    solicitation_user_data JSON,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user_account(id),
    FOREIGN KEY (advisor_siape) REFERENCES user_has_profile_advisor_data(siape),
    FOREIGN KEY (solicitation_id) REFERENCES solicitation(id),
    FOREIGN KEY (actual_solicitation_state_id) REFERENCES solicitation_state(id)
);
CREATE TABLE user_has_solicitation_state(
	id INT NOT NULL AUTO_INCREMENT,
    user_has_solicitation_id INT NOT NULL,
    solicitation_state_id INT NOT NULL,
    decision ENUM('Em analise', 'Solicitado', 'Enviado', 'Deferido', 'Indeferido', 'Cancelado pelo aluno', 'Cancelado pelo orientador', 'Cancelado pela coordenação', 'Expirado') DEFAULT 'Em analise' NOT NULL,
    reason VARCHAR(100),
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (user_has_solicitation_id) REFERENCES user_has_solicitation(id),
    FOREIGN KEY (solicitation_state_id) REFERENCES solicitation_state(id)
);

/* Event Scheduling */
CREATE TABLE scheduling(
	id INT NOT NULL AUTO_INCREMENT,
    scheduled_action ENUM('Send Mail', 'Solicitation State Transition') NOT NULL,
    scheduled_datetime DATETIME NOT NULL,
    scheduled_status ENUM('Pending', 'Sended', 'Canceled') DEFAULT 'Pending' NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE scheduling_state_transition(
	scheduling_id INT NOT NULL,
    state_transition_scheduled_id INT NOT NULL,
    user_has_solicitation_state_id INT NOT NULL,
    PRIMARY KEY (scheduling_id),
    FOREIGN KEY (scheduling_id) REFERENCES scheduling(id),
    FOREIGN KEY (state_transition_scheduled_id) REFERENCES solicitation_state_transition_scheduled(solicitation_state_transition_id),
    FOREIGN KEY (user_has_solicitation_state_id) REFERENCES user_has_solicitation_state(id)
);
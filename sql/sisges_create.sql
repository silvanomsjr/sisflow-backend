CREATE SCHEMA sisgesteste;
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
    holiday_name VARCHAR(30) NOT NULL UNIQUE,
    holiday_date DATE NOT NULL UNIQUE,
    PRIMARY KEY (id),
    FOREIGN KEY (year) REFERENCES config_year(year)
);

INSERT INTO config(config_name) VALUES
	("root path key files"),
    ("root path user files"),
    ("coordinator mail");
    
INSERT INTO config_system_path(config_id, system_path) VALUES
	(1, "/sisges/secrets/"),
	(2, "/sisges/userfiles/");
    
INSERT INTO config_mail(config_id, mail, mail_name) VALUES
	(3, "prof.asoares@ufu.br", "Alexsandro Santos Soares");

/* User data */
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

/* Profiles */
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

CREATE TABLE user_has_profile_professor_data(
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

/* States */
CREATE TABLE state(
	id INT NOT NULL AUTO_INCREMENT,
    state_name VARCHAR(50),
    state_type VARCHAR(50),
    state_description VARCHAR(100),
    PRIMARY KEY (id)
);

CREATE TABLE user_has_state(
	id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    state_id INT NOT NULL,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user_account(id),
    FOREIGN KEY (state_id) REFERENCES state(id)
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

INSERT INTO user_account (institutional_email, secondary_email, user_name, gender, phone, password_hash, password_salt, creation_datetime) VALUES
	("admin@ufu.br", "admin@gmail.com","Admin", 'M', "34111111111","96c287e89a2edf3e807560fd79d8a064b4248846379ab9fe691e2bc158e8293f","btoUCZer0lROFz0e",now()),
    ("prof.asoares@ufu.br","prof.asoares@gmail.com", "Alexsandro Santos Soares", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
	("professor@ufu.br", "professor@gmail.com","Professor Renato", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("aluno@ufu.br", "aluno@gmail.com","Aluno Vitor", 'M', "34222222222","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
	("viniciuscalixto.grad@ufu.br", NULL, "Vinicius Calixto Rocha", 'M', NULL, NULL, NULL, NULL);

INSERT INTO profile (profile_name, profile_acronym, profile_dynamic_fields_metadata) VALUES
	("admin", "ADM", NULL),
    ("coordinator", "COO", NULL),
    ("professor", "PRO", NULL),
    ("student", "STU", NULL);

INSERT INTO user_has_profile (user_id, profile_id, user_dinamyc_profile_fields_data, start_datetime, end_datetime) VALUES 
	(1, 1, NULL, NOW(), NULL),
    (2, 2, NULL, NOW(), NULL),
    (2, 3, NULL, NOW(), NULL),
    (3, 3, NULL, NOW(), NULL),
    (4, 4, NULL, NOW(), NULL),
    (5, 4, NULL, NOW(), NULL);
    
INSERT INTO user_has_profile_coordinator_data (user_has_profile_id, siape)  VALUES
	(2, 'SIAPEALEX');

INSERT INTO user_has_profile_professor_data (user_has_profile_id, siape)  VALUES
	(3, 'SIAPEALEX'),
	(4, 'SIAPERENATO');

INSERT INTO user_has_profile_student_data (user_has_profile_id, matricula, course) VALUES
	(5, '11111BSI111', 'BSI'),
    (6, '11911BCC039', 'BCC');
    
INSERT INTO attachment (hash_name) VALUES 
	("ViniciusCalixtoRocha_HistTextual_9w0ThBLCyT.pdf");
    
INSERT INTO user_has_attachment (user_id, attachment_id) VALUES 
	(1,1),
    (2,1),
    (3,1),
    (4,1),
    (5,1);

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
    type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (id, type)
);
CREATE TABLE dynamic_page_has_component(
	id INT NOT NULL AUTO_INCREMENT,
    dynamic_page_id INT NOT NULL,
    dynamic_component_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (dynamic_page_id) REFERENCES dynamic_page(id),
    FOREIGN KEY (dynamic_component_id) REFERENCES dynamic_component(id),
    UNIQUE (dynamic_page_id, dynamic_component_id)
);
CREATE TABLE dynamic_component_inner_html(
	dynamic_component_id INT NOT NULl,
    dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    inner_html VARCHAR(2000) NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'inner_html')
);
CREATE TABLE dynamic_component_input(
    dynamic_component_id INT NOT NULl,
    dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    input_name VARCHAR(30) UNIQUE NOT NULL,
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
    dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    upload_label VARCHAR(50) NOT NULL,
    upload_name VARCHAR(30) UNIQUE NOT NULL,
    upload_required BOOL DEFAULT TRUE NOT NULL,
    upload_missing_message VARCHAR(200) NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'upload')
);
CREATE TABLE dynamic_component_download(
    dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    download_label VARCHAR(50),
    download_from ENUM ('internal-upload', 'external-link') NOT NULL,
    internal_upload_name VARCHAR(30),
    external_download_link VARCHAR(500),
    CHECK ( (internal_upload_name IS NOT NULL AND external_download_link IS NULL) OR (internal_upload_name IS NULL AND external_download_link IS NOT NULL) ),
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    FOREIGN KEY (internal_upload_name) REFERENCES dynamic_component_upload(upload_name),
    CHECK (dynamic_component_type = 'download')
);
CREATE TABLE dynamic_component_select(
    dynamic_component_id INT NOT NULL,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    select_name VARCHAR(30) NOT NULL UNIQUE,
    select_label VARCHAR(30) NOT NULL,
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
    select_option_label VARCHAR(30) NOT NULL,
    select_opttion_value VARCHAR(30) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (dynamic_component_select_id) REFERENCES dynamic_component_select(dynamic_component_id)
);
CREATE TABLE dynamic_component_select_upload(
    dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    dynamic_component_select_id INT NOT NULL,
    select_upload_name_prefix VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    FOREIGN KEY (dynamic_component_select_id) REFERENCES dynamic_component_select(dynamic_component_id),
    CHECK (dynamic_component_type = 'select_upload')
);
CREATE TABLE dynamic_component_button(
	dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    button_label VARCHAR(30) NOT NULL,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    CHECK (dynamic_component_type = 'button')
);

INSERT INTO dynamic_page (title) VALUES 
	('Solicitação de inicio de estágio obrigatório com vínculo - Avaliação de históricos e comprovante de vínculo empregatício'),
    ('Solicitação de inicio de estágio obrigatório sem vínculo - Avaliação de históricos'),
    ('Solicitação de inicio de estágio não obrigatório externo - Avaliação de históricos'),
    ('Solicitação de inicio de estágio não obrigatório interno - Avaliação de históricos'),
    
    ('Solicitação de inicio de estágio - Verificação de históricos e comprovantes do aluno pela coordenação'),
    ('Solicitação de inicio de estágio - Verificação de históricos do aluno pela coordenação'),
    
    ('Solicitação de inicio de estágio - Assinatura do PA [[[ifMale?pelo aluno:::pela aluna]]]'),
    ('Solicitação de inicio de estágio - Assinatura do PA pelo orientador'),
    ('Solicitação de inicio de estágio - Assinatura do PA pela coordenação de estágios'),
    ('Solicitação de inicio de estágio - Concluída'),
    
    ('Solicitação de inicio de estágio - Assinatura do PA e TCE [[[ifMale?pelo aluno:::pela aluna]]]'),
    ('Solicitação de inicio de estágio - Assinatura do PA e TCE pelo orientador'),
    ('Solicitação de inicio de estágio - Assinatura do PA e TCE pela coordenação de estágios'),
    ('Solicitação de inicio de estágio - Concluída'),
    
    ('Envio de relatório parcial - Assinatura [[[ifMale?do aluno:::da aluna]]]'),
    ('Envio de relatório parcial - Assinatura da coordenação de estágios'),
    ('Envio de relatório parcial - Concluída'),
    
    ('Envio de relatório final - Assinatura [[[ifMale?do aluno:::da aluna]]]'),
    ('Envio de relatório final - Assinatura da coordenação de estágios'),
    ('Envio de relatório final - Concluída');
    
INSERT INTO dynamic_component (type) VALUES 
	('inner_html'),('inner_html'),('inner_html'),('inner_html'),('inner_html'),
    ('inner_html'),('inner_html'),('inner_html'),('inner_html'),('inner_html'),
    ('inner_html'),('inner_html'),('inner_html'),('inner_html'),('inner_html'),
    ('inner_html'),('inner_html');
    
INSERT INTO dynamic_component_inner_html (dynamic_component_id, dynamic_component_type, inner_html) VALUES 
	(
		1, 
        'inner_html', 
		'<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio obrigatório no [[[ifBCC? BCC ::: BSI ]]]:</p>'
            '[[[ifBCC? 
				<p><b>Duração</b>: 10 a 20 semanas, <b>Carga horária mínima</b>: 210 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ::: 
				<p><b>Duração</b>: 16 a 32 semanas, <b>Carga horária mínima</b>: 440 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ]]]'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCC?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>'
	),(
		2, 
        'inner_html', 
		'<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio não obrigatório no [[[ifBCC? BCC ::: BSI ]]]:</p>'
            '<p><b>Duração</b>: 8 a 24 semanas, <b>Carga horária mínima</b>: 220 horas, <b>Aprovação</b>: 1 e 2 períodos completos</p>'
			'<p>Com carga horária de disciplinas acima de 1200 é possível estagiar de 30 horas semanais e, caso contrário, 20 horas</p>'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCC?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>'
	),(
		3, 
        'inner_html', 
		'<p>Olá coordenador [[[coordinatorName]]]. Segue abaixo históricos e comprovante empregatício do aluno para download caso necessário:</p>'
	),(
		4, 
        'inner_html', 
        '<p>Olá coordenador [[[coordinatorName]]]. Segue abaixo históricos do aluno para download caso necessário:</p>'
	),(
		5,
        'inner_html', 
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o Plano de Atividades(PA) contendo a sua assinatura e aguarda a assinatura dos professores</p>'
	),(
		6,
        'inner_html',
        '<p>Olá orientador. Segue abaixo o Plano de Atividades(PA) enviado pelo aluno para a sua assinatura:</p>'
	),(
		7, 
        'inner_html', 
		'<p>Olá coordenador. Segue abaixo o Plano de Atividades(PA) enviado pelo aluno e orientador para a sua assinatura:</p>'
	),(
		8,
        'inner_html',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o Termo de Compromisso de Estágio(TCE) e o Plano de Atividades(PA)'
			' contendo a sua assinatura e aguarda a assinatura dos professores</p>'
	),(
		9,
        'inner_html',
        '<p>Olá orientador. Segue abaixo o o Termo de Compromisso de Estágio(TCE) e o Plano de Atividades(PA) enviado pelo aluno'
			' para a sua assinatura:</p>'
	),(
		10,
		'inner_html',
        '<p>Olá coordenador. Segue abaixo o Termo de Compromisso de Estágio(TCE) e o Plano de Atividades(PA) enviado pelo aluno'
			' e orientador para a sua assinatura:</p>'
	),(
		11,
		'inner_html',
        '<p>Com todas as assinaturas a solicitação está concluída você já pode iniciar o estágio em sua data de início</p>'
			'<p>Realize o download abaixo da documentação assinada</p>'
	),(
		12,
        'inner_html',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia os documentos relacionados ao relatório parcial contendo'
			' a sua assinatura e aguarda os docentes assinarem</p>'
	),(
		13,
        'inner_html',
        '<p>Olá coordenador. Segue abaixo o relatório parcial enviado pelo aluno para a sua validação e assinatura:</p>'
	),(
		14,
        'inner_html',
        '<p>Com todas as assinaturas a solicitação está concluída</p>'
			'<p>Realize o download abaixo da documentação assinada</p>'
	),(
		15,
        'inner_html',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia os documentos relacionados ao relatório final contendo'
			' a sua assinatura e aguarda os docentes assinarem</p>'
	),(
		16,
        'inner_html',
        '<p>Olá coordenador. Segue abaixo o relatório final enviado pelo aluno para a sua validação e assinatura:</p>'
	),(
		17,
        'inner_html',
        '<p>Com todas as assinaturas a solicitação a solicitação está concluída e o estágio pode ser finalizado!</p>'
			'<p>Realize o download abaixo da documentação assinada</p>'
	);

/*
'
 '[{ "file_content_id" : "PAALUNO", "label_txt" : "Download do PA" }]',
        '[{ "file_content_id" : "PAPROFESSOR", "label_txt" : "Envie o PA com sua assinatura", "required": true, "missing_msg": "O envio do PA é obrigatório!" }]',
		
*/

INSERT INTO dynamic_component_input (dynamic_component_id, dynamic_component_type, input_name, input_type, input_required, input_missing_message) VALUES 
	(18, 'input', 'startInternship', 'date', TRUE, 'A data de início é obrigatória!');

INSERT INTO dynamic_component_input_date_rule (dynamic_component_input_id, dynamic_component_input_type, rule_type, rule_message_type, rule_start_days, rule_end_days, rule_missing_message) VALUES
	(18, 'date', 'must-not-be-from-today', 'warn', 5, 10, 'Atenção o prazo recomendável para verificar a documentação e assinar pelo grupo docente e SESTA é de 10 dias, clique em ok se deseja continuar mesmo assim'),
    (18, 'date', 'must-not-be-from-today', 'error', 0, 5, 'Atenção o prazo mínimo para verificar a documentação e assinar pelo SESTA é de 5 dias úteis');

INSERT INTO dynamic_component_upload (dynamic_component_id, dynamic_component_type, upload_label, upload_name, upload_required, upload_missing_message) VALUES
	(19, 'upload', 'Envie seu histórico textual', 'HistTextual', TRUE, 'O envio do histórico textual é obrigatório!'),
    (20, 'upload', 'Envie seu histórico visual', 'HistVisual', TRUE, 'O envio do histórico visual é obrigatório!'),
    (21, 'upload', 'Envie o PA com sua assinatura', 'PAAluno', TRUE, 'O envio do PA é obrigatório!'),
    (22, 'upload', 'Envie o PA com sua assinatura', 'PAOrientador', TRUE, 'O envio do PA é obrigatório!'),
    (23, 'upload', 'Envie o PA com sua assinatura', 'PACoordenador', TRUE, 'O envio do PA é obrigatório!'),
    (24, 'upload', 'Envie o TCE com sua assinatura', 'TCEAluno', TRUE, 'O envio do TCE é obrigatório!'),
    (25, 'upload', 'Envie o TCE com sua assinatura', 'TCEOrientador', TRUE, 'O envio do TCE é obrigatório!'),
    (26, 'upload', 'Envie o TCE com sua assinatura', 'TCECoordenador', TRUE, 'O envio do TCE é obrigatório!'),
    (27, 'upload', 'Envie o Relatório Parcial com sua assinatura', 'RelParcialAluno', TRUE, 'O envio do Relatório Parcial é obrigatório!'),
    (28, 'upload', 'Envie o Relatório Parcial com sua assinatura', 'RelParcialCoordenador', TRUE, 'O envio do Relatório Parcial é obrigatório!'),
	(29, 'upload', 'Envie o Relatório Final com sua assinatura', 'RelFinalAluno', TRUE, 'O envio do Relatório Final é obrigatório!'),
    (30, 'upload', 'Envie o Relatório Final com sua assinatura', 'RelFinalCoordenador', TRUE, 'O envio do Relatório Final é obrigatório!');
    
INSERT INTO dynamic_component_download (dynamic_component_id, dynamic_component_type, download_label, download_from, internal_upload_name, external_download_link) VALUES
	(31, 'download', 'Faça o download do histórico textual', 'internal-upload', 'HistTextual', NULL),
	(32, 'download', 'Faça o download do histórico visual', 'internal-upload', 'HistVisual', NULL),
	(33, 'download', 'Faça o download do PA assinado pelo aluno', 'internal-upload', 'PAAluno', NULL),
	(34, 'download', 'Faça o download do PA assinado pelo aluno e orientador', 'internal-upload', 'PAOrientador', NULL),
	(35, 'download', 'Faça o download do PA completamente assinado', 'internal-upload', 'PACoordenador', NULL),
	(36, 'download', 'Faça o download do TCE assinado pelo aluno', 'internal-upload', 'TCEAluno', NULL),
	(37, 'download', 'Faça o download do TCE assinado pelo aluno e orientador', 'internal-upload', 'TCEOrientador', NULL),
	(38, 'download', 'Faça o download do  TCE completamente assinado', 'internal-upload', 'TCECoordenador', NULL),
	(39, 'download', 'Faça o download do ', 'internal-upload', 'RelParcialAluno', NULL),
	(40, 'download', 'Faça o download do ', 'internal-upload', 'RelParcialCoordenador', NULL),
	(41, 'download', 'Faça o download do ', 'internal-upload', 'RelFinalAluno', NULL),
	(42, 'download', 'Faça o download do ', 'internal-upload', 'RelFinalCoordenador', NULL);

INSERT INTO dynamic_page_has_component (dynamic_page_id, dynamic_component_id) VALUES 
	(1, 1);
    
INSERT INTO dynamic_page (title, top_inner_html, mid_inner_html, bot_inner_html, inputs, downloads, uploads, select_uploads, is_solicitation_button_active) VALUES 
	(
        'Solicitação de inicio de estágio obrigatório com vínculo - Avaliação de históricos e comprovante de vínculo empregatício',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio obrigatório no [[[ifBCC? BCC ::: BSI ]]]:</p>'
            '[[[ifBCC? 
				<p><b>Duração</b>: 10 a 20 semanas, <b>Carga horária mínima</b>: 210 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ::: 
				<p><b>Duração</b>: 16 a 32 semanas, <b>Carga horária mínima</b>: 440 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ]]]'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCC?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>',
		'',
        '',
        NULL,
        NULL,
        '[
			{ "file_content_id" : "HistTextual", "label_txt" : "Envie seu histórico textual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{ "file_content_id" : "HistVisual", "label_txt" : "Envie seu histórico visual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
		]',
		'[{
			"label_txt" : "Escolha o tipo de vínculo",
            "select_opts" : [
				{ "label" : "Escolha uma opção ..." },
                { "label" : "Carteira Digital de Trabalho", "value": "VinculoCTPS" },
                { "label" : "Contrato de pessoa jurídica", "value": "VinculoPJ" },
                { "label" : "Declaração do Empregador", "value": "VinculoDeclaracao" },
                { "label" : "Outros", "value": "VinculoOutros" }
			],
            "required": true,
            "missing_msg": "O envio do comprovante de vínculo empregatício é obrigatório!"
		}]',
		TRUE
	),
    (
        'Solicitação de inicio de estágio obrigatório sem vínculo - Avaliação de históricos',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio obrigatório do curso [[[ifBCC? BCC ::: BSI ]]]:</p>'
            '[[[ifBCC? 
				<p><b>Duração</b>: 10 a 20 semanas, <b>Carga horária mínima</b>: 210 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ::: 
				<p><b>Duração</b>: 16 a 32 semanas, <b>Carga horária mínima</b>: 440 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ]]]'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCC?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>',
		'',
        '',
        NULL,
        NULL,
        '[
			{ "file_content_id" : "HistTextual", "label_txt" : "Envie seu histórico textual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{ "file_content_id" : "HistVisual", "label_txt" : "Envie seu histórico visual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio não obrigatório externo - Avaliação de históricos',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio não obrigatório no [[[ifBCC? BCC ::: BSI ]]]:</p>'
            '<p><b>Duração</b>: 8 a 24 semanas, <b>Carga horária mínima</b>: 220 horas, <b>Aprovação</b>: 1 e 2 períodos completos</p>'
			'<p>Com carga horária de disciplinas acima de 1200 é possível estagiar de 30 horas semanais e, caso contrário, 20 horas</p>'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCC?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>',
		'',
        '',
        NULL,
        NULL,
        '[
			{ "file_content_id" : "HistTextual", "label_txt" : "Envie seu histórico textual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{ "file_content_id" : "HistVisual", "label_txt" : "Envie seu histórico visual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio não obrigatório interno - Avaliação de históricos',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio não obrigatório no [[[ifBCC? BCC ::: BSI ]]]:</p>'
            '<p><b>Duração</b>: 8 a 24 semanas, <b>Carga horária mínima</b>: 220 horas, <b>Aprovação</b>: 1 e 2 períodos completos</p>'
			'<p>Com carga horária de disciplinas acima de 1200 é possível estagiar de 30 horas semanais e, caso contrário, 20 horas</p>'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCC?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>',
		'',
        '',
        NULL,
        NULL,
        '[
			{ "file_content_id" : "HistTextual", "label_txt" : "Envie seu histórico textual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{ "file_content_id" : "HistVisual", "label_txt" : "Envie seu histórico visual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!" }
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Verificação de documentos pela coordenação',
        '<p>Olá coordenador [[[coordinatorName]]]. Segue abaixo a documentação do aluno para download caso necessário:</p>',
		'',
        '',
        NULL,
        '[
			{ "file_content_id" : "HistTextual", "label_txt" : "Download do histórico textual" },
			{ "file_content_id" : "HistVisual", "label_txt" : "Download do histórico visual" }
		]',
        NULL,
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o PA contendo a sua assinatura e aguarda a assinatura dos professores</p>',
		'',
        '',
        '[{
			"label_txt" : "Data de início do estágio", 
            "input_type" : "date", 
            "required": true, 
            "missing_msg": "A data de início é obrigatória!",
            "input_date_rules": [
				{"rule_type":"warn", "min_days_plus_today": 6, "max_days_plus_today": 10, "msg":"Atenção o prazo recomendável para verificar a documentação e assinar pelo grupo docente e SESTA é de 10 dias"},
                {"rule_type":"error", "min_days_plus_today": 0, "max_days_plus_today": 5, "msg":"Atenção o prazo mínimo para verificar a documentação e assinar pelo SESTA é de 5 dias"}
            ]
		}]',
        NULL,
        '[{ "file_content_id" : "PAALUNO", "label_txt" : "Envie o plano de atividades com sua assinatura", "required": true, "missing_msg": "O envio do plano de atividades é obrigatório!" }]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura do professor orientador',
        '<p>Olá orientador. Segue abaixo o plano de atividades enviado pelo aluno para a sua assinatura:</p>',
		'',
        '',
        NULL,
        '[{ "file_content_id" : "PAALUNO", "label_txt" : "Download do PA" }]',
        '[{ "file_content_id" : "PAPROFESSOR", "label_txt" : "Envie o PA com sua assinatura", "required": true, "missing_msg": "O envio do PA é obrigatório!" }]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura do coordenador',
        '<p>Olá coordenador. Segue abaixo o PA enviado pelo professor orientador e aluno para a sua assinatura:</p>',
		'',
        '',
        NULL,
        '[
			{ "file_content_id" : "PAALUNO", "label_txt" : "Download do PA Aluno" },
            { "file_content_id" : "PAPROFESSOR", "label_txt" : "Download do PA Professor" }
		]',
        '[{ "file_content_id" : "PACOORDENADOR", "label_txt" : "Envie o PA com sua assinatura", "required": true, "missing_msg": "O envio do PA é obrigatório!" }]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Concluída',
        '<p>Com todas as assinaturas a solicitação está concluída você já pode iniciar o estágio</p>'
        '<p>Realize o download abaixo da documentação assinada</p>',
		'',
        '',
        NULL,
        '[{ "file_content_id" : "PACOORDENADOR", "label_txt" : "Download do plano de atividades assinado" }]',
        NULL,
        NULL,
		FALSE
	),
    (
        'Solicitação de inicio de estágio - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o TCE e o PA contendo a sua assinatura e aguarda a assinatura dos professores</p>',
		'',
        '',
        '[{
			"label_txt" : "Data de início do estágio", 
            "input_type" : "date", 
            "required": true, 
            "missing_msg": "A data de início é obrigatória!",
            "input_date_rules": [
				{"rule_type":"warn", "min_days_plus_today": 6, "max_days_plus_today": 10, "msg":"Atenção o prazo recomendável para verificar a documentação e assinar pelo grupo docente e SESTA é de 10 dias"},
                {"rule_type":"error", "min_days_plus_today": null, "max_days_plus_today": 5, "msg":"Atenção o prazo mínimo para verificar a documentação e assinar pelo SESTA é de 5 dias"}
            ]
		}]',
        NULL,
        '[
			{ "file_content_id" : "TCEALUNO", "label_txt" : "Envie o Termo de Compromisso de Estágio(TCE) com sua assinatura", "required": true, "missing_msg": "O envio do TCE é obrigatório!" },
			{ "file_content_id" : "PAALUNO", "label_txt" : "Envie o Plano de atividades(PA) com sua assinatura", "required": false, "missing_msg": "O envio do PA é opcional desde que suas informações estejam no TCE" }
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura do professor orientador',
        '<p>Olá orientador. Segue abaixo o plano de atividades enviado pelo aluno para a sua assinatura:</p>',
		'',
        '',
        NULL,
        '[
			{ "file_content_id" : "PAALUNO", "label_txt" : "Download do plano de atividades(PA) do aluno" },
            { "file_content_id" : "TCEALUNO", "label_txt" : "Download do Termo de Compromisso de Estágio(TCE) do aluno" }
		]',
        '[
			{ "file_content_id" : "PAPROFESSOR", "label_txt" : "Envie o plano de atividades(PA) com sua assinatura", "required": true, "missing_msg": "O envio do PA é obrigatório!" },
            { "file_content_id" : "TCEPROFESSOR", "label_txt" : "Envie o Termo de Compromisso de Estágio(TCE) com sua assinatura", "required": true, "missing_msg": "O envio do TCE é obrigatório!" }
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura do coordenador',
        '<p>Olá coordenador. Segue abaixo o PA enviado pelo professor orientador e aluno para a sua assinatura:</p>',
		'',
        '',
        NULL,
        '[
			{ "file_content_id" : "PAALUNO", "label_txt" : "Download do PA Aluno" },
            { "file_content_id" : "PAPROFESSOR", "label_txt" : "Download do PA Professor" },
            { "file_content_id" : "TCEALUNO", "label_txt" : "Download do TCE Aluno" },
            { "file_content_id" : "TCEPROFESSOR", "label_txt" : "Download do TCE Professor" }
		]',
        '[
			{ "file_content_id" : "PACOORDENADOR", "label_txt" : "Envie o Plano de Atividades(PA) com sua assinatura", "required": true, "missing_msg": "O envio do PA é obrigatório!" },
            { "file_content_id" : "TCECOORDENADOR", "label_txt" : "Envie o Termo de Compromisso de Estágio(TCE) com sua assinatura", "required": true, "missing_msg": "O envio do TCE é obrigatório!" }
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Concluída',
        '<p>Com todas as assinaturas a solicitação está concluída você já pode iniciar o estágio</p>'
        '<p>Realize o download abaixo da documentação assinada</p>',
		'',
        '',
        NULL,
        '[
			{ "file_content_id" : "PACOORDENADOR", "label_txt" : "Download do plano de atividades assinado" },
            { "file_content_id" : "TCECOORDENADOR", "label_txt" : "Download do Termo de Compromisso de Estágio assinado" }
		]',
        NULL,
        NULL,
		FALSE
	),
    (
        'Envio de relatório parcial - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia os documentos relacionados ao relatório parcial contendo'
        ' a sua assinatura e aguarda os docentes assinarem</p>',
		'',
        '',
        NULL,
        NULL,
        '[{ "file_content_id" : "RelParcial", "label_txt" : "Envie o relatório parcial com sua assinatura", "required": true, "missing_msg": "O envio do relatório parcial é obrigatório!" }]',
        NULL,
		TRUE
	),
	(
        'Envio de relatório parcial - Concluído',
        '<p>Com todas as assinaturas a solicitação está concluída</p>'
        '<p>Realize o download abaixo da documentação assinada</p>',
		'',
        '',
        NULL,
        NULL,
        '[{ "file_content_id" : "RelParcial", "label_txt" : "Relatório parcial completo", "required": true, "missing_msg": "O download do relatório parcial é obrigatório!" }]',
        NULL,
		FALSE
	),
    (
        'Envio de relatório final - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia os documentos relacionados ao relatório final contendo '
        'a sua assinatura e aguarda os docentes assinarem</p>',
		'',
        '',
        NULL,
        NULL,
        '[{ "file_content_id" : "RelFinal", "label_txt" : "Envie o relatório final com sua assinatura", "required": true, "missing_msg": "O envio do relatório final é obrigatório!" }]',
        NULL,
		TRUE
	),
    (
        'Envio de relatório final - Concluído',
        '<p>Com todas as assinaturas a solicitação está concluída</p>'
        '<p>Realize o download abaixo da documentação assinada</p>',
		'',
        '',
        NULL,
        NULL,
        '[{ "file_content_id" : "RelFinal", "label_txt" : "Relatório final completo", "required": true, "missing_msg": "O download do relatório final é obrigatório!" }]',
        NULL,
		FALSE
	);

/* Dynamic mail message */
CREATE TABLE dynamic_mail(
	id INT NOT NULL AUTO_INCREMENT,
    mail_subject VARCHAR(100),
    mail_body_html VARCHAR(2000),
    is_sent_to_student BOOL DEFAULT FALSE,
    is_sent_to_professor BOOL DEFAULT FALSE,
    is_sent_to_coordinator BOOL DEFAULT FALSE,
    PRIMARY KEY (id)
);

INSERT INTO dynamic_mail (mail_subject, mail_body_html, is_sent_to_student, is_sent_to_professor, is_sent_to_coordinator) VALUES 
	(
		'Sistema de estágios - Solicitação de avaliação dos históricos',
        '<p>Olá [[[ifMale?aluno:::aluna]]] [[[ifBCC?do BCC:::do BSI]]] [[[userName]]]</p>'
		'<p>Você solicitou ao coordenador de estágios a avaliação dos seus históricos.</p>'
			'<p>O coordenador de estágios possui até 4 dias úteis para realizar a avaliação retornando se a solicitação foi deferida ou indeferida.</p>'
			'<br>'
			'<p>Não esqueça de verificar sua caixa de mensagens e a plataforma de estágios para novidades neste período.</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de avaliação dos históricos completa',
        '<p>Olá [[[ifMale?aluno:::aluna]]] [[[ifBCC?do BCC:::do BSI]]] [[[userName]]]</p>'
			'<p>O coordenador avaliou seus documentos enviados.</p>'
			'<p>Verifique o status da avaliação no sistema de estágios.</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de assinaturas para início de estágio',
        '<p>Olá [[[ifMale?aluno:::aluna]]] [[[ifBCC?do BCC:::do BSI]]] [[[userName]]]</p>'
			'<p>Você solicitou o complemento de assinaturas para dar inicio ao estágio.</p>'
			'<p>O professor orientador, coordenador e o setor de estágios SESTA podem demorar até 10 dias úteis no processo.</p>'
			'<br>'
			'<p>Não esqueça de verificar sua caixa de mensagens e a plataforma de estágios para novidades neste período.</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de assinaturas completa',
        '<p>Olá [[[ifMale?aluno:::aluna]]] [[[ifBCC?do BCC:::do BSI]]] [[[userName]]]</p>'
			'<p>Os documentos para início de estágio foram assinados.</p>'
			'<p>Com estes documentos é possível dar início ao estágio, não se esqueça de produzir relatórios parciais '
            'durante o período em estágio e o relatório final na conclusão.</p>',
        TRUE, FALSE, FALSE
    );

/* Solicitation and its associated data - Solicitation is the state machine */
CREATE TABLE solicitation(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_name VARCHAR(256),
    PRIMARY KEY (id)
);

CREATE TABLE solicitation_state(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_id INT NOT NULL,
    state_profile_editor INT,
    state_description VARCHAR(256),
    state_max_duration_days INT,
    state_dynamic_page_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_id) REFERENCES solicitation(id),
    FOREIGN KEY (step_profile_editor) REFERENCES profile(id),
    FOREIGN KEY (state_dynamic_page_id) REFERENCES dynamic_page(id)
);

CREATE TABLE solicitation_state_dynamic_mail(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_state_id INT NOT NULL,
    dynamic_mail_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_state_id) REFERENCES solicitation_state(id),
    FOREIGN KEY (dynamic_mail_id) REFERENCES dynamic_mail(id)
);

CREATE TABLE user_has_solicitation(
	id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    professor_siape VARCHAR(15),
    solicitation_id INT NOT NULL,
    actual_solicitation_state INT NOT NULL,
    solicitation_user_data JSON,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user_account(id),
    FOREIGN KEY (professor_siape) REFERENCES user_has_profile_professor_data(siape),
    FOREIGN KEY (solicitation_id) REFERENCES solicitation(id)
);

CREATE TABLE user_has_solicitation_state(
	id INT NOT NULL AUTO_INCREMENT,
    user_has_solicitation_id INT NOT NULL,
    solicitation_state_id INT NOT NULL,
    decision ENUM('Em analise', 'Deferido', 'Indeferido') NOT NULL,
    reason VARCHAR(100),
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (user_has_solicitation_id) REFERENCES user_has_solicitation(id),
    FOREIGN KEY (solicitation_state_id) REFERENCES solicitation_state(id)
);

INSERT INTO solicitation (solicitation_name) VALUES 
	('Inicio de estágio obrigatório externo com vinculo empregatício'),
    ('Inicio de estágio obrigatório externo sem vinculo empregatício'),
    ('Inicio de estágio não obrigatório externo'),
    ('Inicio de estágio não obrigatório interno'),
    ('Envio de relatório parcial'),
    ('Envio de relatório final');

INSERT INTO solicitation_step (solicitation_id, step_profile_editor, step_order_in_solicitation, step_description, step_max_duration_days) VALUES 
	(1, 4, 1, 'Solicitação de avaliação dos históricos e complementos pelo aluno', 4),
    (1, 2, 2, 'Avaliação dos históricos e complementos pelo coordenador', 4),
    (1, 4, 3, 'Requerimento de assinaturas de documentos ao aluno', 4),
    (1, 3, 4, 'Requerimento de assinaturas de documentos ao professor', 4),
    (1, 2, 5, 'Requerimento de assinaturas de documentos ao coordenador', 4),
    (1, NULL, 6, 'Estágio iniciado', NULL),
    
    (2, 4, 1, 'Solicitação de avaliação dos históricos pelo aluno', 4),
    (2, 2, 2, 'Avaliação dos históricos pelo coordenador', 4),
    (2, 4, 3, 'Requerimento de assinaturas de documentos ao aluno', 4),
    (2, 3, 4, 'Requerimento de assinaturas de documentos ao professor', 4),
    (2, 2, 5, 'Requerimento de assinaturas de documentos ao coordenador', 4),
    (2, NULL, 6, 'Estágio iniciado', NULL),
    
    (3, 4, 1, 'Solicitação de avaliação dos históricos pelo aluno', 4),
    (3, 2, 2, 'Avaliação dos históricos pelo coordenador', 4),
    (3, 4, 3, 'Requerimento de assinaturas de documentos ao aluno', 4),
    (3, 3, 4, 'Requerimento de assinaturas de documentos ao professor', 4),
    (3, 2, 5, 'Requerimento de assinaturas de documentos ao coordenador', 4),
    (3, NULL, 6, 'Estágio iniciado', NULL),
    
    (4, 4, 1, 'Solicitação de avaliação dos históricos pelo aluno', 4),
    (4, 2, 2, 'Avaliação dos históricos pelo coordenador', 4),
    (4, 4, 3, 'Requerimento de assinaturas de documentos ao aluno', 4),
    (4, 3, 4, 'Requerimento de assinaturas de documentos ao professor', 4),
    (4, 2, 5, 'Requerimento de assinaturas de documentos ao coordenador', 4),
    (4, NULL, 6, 'Estágio iniciado', NULL),
    
    (5, 4, 1, 'Requerimento de avaliação e complemento de assinaturas do relatório parcial pelo aluno', 4),
    (5, NULL, 2, 'Relatório parcial completo', NULL),
    
    (6, 4, 1, 'Requerimento de avaliação e complemento de assinaturas do relatório final pelo aluno', 4),
    (6, NULL, 2, 'Relatório final completo', NULL);

INSERT INTO solicitation_step_dynamic_mail (solicitation_step_id, dynamic_mail_id) VALUES
	(1, 1),
    (2, 2),
    (3, 3),
    (5, 4),
    
    (7, 1),
    (8, 2),
    (9, 3),
    (11, 4),
    
    (13, 1),
    (14, 2),
    (15, 3),
    (17, 4),
    
    (19, 1),
    (20, 2),
    (21, 3),
    (23, 4);

INSERT INTO solicitation_step_page (solicitation_step_id, use_dynamic_page, dynamic_page_id, static_page_name) VALUES
	(1, TRUE, 1, NULL),
    (2, TRUE, 5, NULL),
    (3, TRUE, 6, NULL),
    (4, TRUE, 7, NULL),
    (5, TRUE, 8, NULL),
    (6, TRUE, 9, NULL),
    
    (7, TRUE, 2, NULL),
    (8, TRUE, 5, NULL),
    (9, TRUE, 10, NULL),
    (10, TRUE, 11, NULL),
    (11, TRUE, 12, NULL),
    (12, TRUE, 13, NULL),
    
    (13, TRUE, 3, NULL),
    (14, TRUE, 5, NULL),
    (15, TRUE, 10, NULL),
    (16, TRUE, 11, NULL),
    (17, TRUE, 12, NULL),
    (18, TRUE, 13, NULL),
    
    (19, TRUE, 4, NULL),
    (20, TRUE, 5, NULL),
    (21, TRUE, 10, NULL),
    (22, TRUE, 11, NULL),
    (23, TRUE, 12, NULL),
    (24, TRUE, 13, NULL),
    
    (25, TRUE, 14, NULL),
    (26, TRUE, 15, NULL),
    
    (27, TRUE, 16, NULL),
    (28, TRUE, 17, NULL);
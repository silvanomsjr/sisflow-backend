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
    holiday_name VARCHAR(50) NOT NULL UNIQUE,
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
INSERT INTO user_account (institutional_email, secondary_email, user_name, gender, phone, password_hash, password_salt, creation_datetime) VALUES
	("admin@ufu.br", "admin@gmail.com","Admin", 'M', "34111111111","96c287e89a2edf3e807560fd79d8a064b4248846379ab9fe691e2bc158e8293f","btoUCZer0lROFz0e",now()),
    ("prof.asoares@ufu.br","prof.asoares@gmail.com", "Alexsandro Santos Soares", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
	("abdala@ufu.br", NULL, "Daniel Duarte Abdala", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("gina@ufu.br", NULL, "Gina Maira Barbosa de Oliveira", 'F', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("luiz@ufu.br", NULL, "Luiz Gustavo Almeida Martins", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("maia@ufu.br", NULL, "Marcelo de Almeida Maia", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("stephane@ufu.br", NULL,"Stéphane Julia", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("aluno@ufu.br", "aluno@gmail.com","Aluno Vitor", 'M', "34222222222","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
	("viniciuscalixto.grad@ufu.br", NULL, "Vinicius Calixto Rocha", 'M', NULL, NULL, NULL, NULL);
INSERT INTO profile (profile_name, profile_acronym, profile_dynamic_fields_metadata) VALUES
	("admin", "ADM", NULL),
    ("coordinator", "COO", NULL),
    ("advisor", "ADV", NULL),
    ("student", "STU", NULL);
INSERT INTO user_has_profile (user_id, profile_id, user_dinamyc_profile_fields_data, start_datetime, end_datetime) VALUES 
	(1, 1, NULL, NOW(), NULL),
    (2, 2, NULL, NOW(), NULL),
    (2, 3, NULL, NOW(), NULL),
    (3, 3, NULL, NOW(), NULL),
    (4, 3, NULL, NOW(), NULL),
    (5, 3, NULL, NOW(), NULL),
    (6, 3, NULL, NOW(), NULL),
    (7, 3, NULL, NOW(), NULL),
    (8, 4, NULL, NOW(), NULL),
    (9, 4, NULL, NOW(), NULL);
INSERT INTO user_has_profile_coordinator_data (user_has_profile_id, siape) VALUES
	(2, 'SIAPE-ALEX');
INSERT INTO user_has_profile_advisor_data (user_has_profile_id, siape)  VALUES
	(3, 'SIAPE-ALEX'),
	(4, 'SIAPE-ABDALA'),
    (5, 'SIAPE-GINA'),
    (6, 'SIAPE-LUIZ'),
    (7, 'SIAPE-MAIA'),
    (8, 'SIAPE-STEPHANE');
INSERT INTO user_has_profile_student_data (user_has_profile_id, matricula, course) VALUES
	(9, '11111BSI111', 'BSI'),
    (10, '11911BCC039', 'BCC');

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
    type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
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
    dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
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
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
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
    dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    dynamic_component_select_name VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (dynamic_component_id),
    FOREIGN KEY (dynamic_component_id, dynamic_component_type) REFERENCES dynamic_component(id, type),
    FOREIGN KEY (dynamic_component_select_name) REFERENCES dynamic_component_select(select_name),
    CHECK (dynamic_component_type = 'select_upload')
);
CREATE TABLE dynamic_component_download(
    dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
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
	dynamic_component_id INT NOT NULl,
	dynamic_component_type ENUM('inner_html', 'input', 'upload', 'download', 'select', 'select_upload', 'button') NOT NULL,
    button_label VARCHAR(100) NOT NULL,
    button_color ENUM('darkblue', 'red', 'black') NOT NULL,
    button_transation_type ENUM('Request', 'Cancel', 'Send', 'Send and Defer', 'Defer', 'Reject') NOT NULL,
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
    ('inner_html'),('inner_html'),
    ('input'),
    ('upload'),('upload'),('upload'),('upload'),('upload'),('upload'),
    ('upload'),('upload'),('upload'),('upload'),('upload'),('upload'),
    ('select'),
    ('select_upload'),
    ('download'),('download'),('download'),('download'),('download'),('download'),
    ('download'),('download'),('download'),('download'),('download'),('download'),('download'),
    ('button'),('button'),('button'),('button'),('button'),('button');
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
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o Plano de Atividades(PA) contendo a sua assinatura e aguarda a assinatura dos docentes</p>'
			'<p>A data planejada para o início do estágio serve para verificação de prazos para as assinaturas</p>'
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
			' contendo a sua assinatura e aguarda a assinatura dos docentes</p>'
            '<p>A data planejada para o início do estágio serve para verificação de prazos para as assinaturas</p>'
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
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o relatório parcial contendo a sua assinatura e aguarda os docentes assinarem</p>'
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
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o relatório final contendo a sua assinatura e aguarda os docentes assinarem</p>'
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
INSERT INTO dynamic_component_input (dynamic_component_id, dynamic_component_type, input_name, input_type, input_required, input_missing_message) VALUES 
	(18, 'input', 'startInternship', 'date', TRUE, 'A data de início é obrigatória!');
INSERT INTO dynamic_component_input_date_rule (dynamic_component_input_id, dynamic_component_input_type, rule_type, rule_message_type, rule_start_days, rule_end_days, rule_missing_message) VALUES
	(18, 'date', 'must-not-be-from-today', 'warn', 4, 10, 'Atenção o prazo recomendável para verificar a documentação e assinar pelo grupo docente e SESTA é de 10 dias, clique em ok se deseja continuar mesmo assim'),
    (18, 'date', 'must-not-be-from-today', 'error', NULL, 4, 'Atenção o prazo mínimo para verificar a documentação e assinar pelo SESTA é de 5 dias úteis');
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
INSERT INTO dynamic_component_select (dynamic_component_id, dynamic_component_type, select_name, select_label, select_initial_text, is_select_required, select_missing_message) VALUES 
	(31, 'select', 'Vinculo', 'Escolha o tipo de vínculo', DEFAULT, TRUE, 'O envio do vínculo empregatício é obrigatório');
INSERT INTO dynamic_component_select_option (dynamic_component_select_id, select_option_label, select_option_value) VALUES 
	(31, DEFAULT, NULL),
    (31, 'Carteira Digital de Trabalho', 'CTPS'),
    (31, 'Contrato de pessoa jurídica', 'PJ'),
    (31, 'Declaração do Empregador', 'Declaracao'),
    (31, 'Outros', 'Outros');
INSERT INTO dynamic_component_select_upload (dynamic_component_id, dynamic_component_type, dynamic_component_select_name) VALUES 
	(32, 'select_upload', 'Vinculo');
INSERT INTO dynamic_component_download (dynamic_component_id, dynamic_component_type, download_label, download_from, internal_upload_name, internal_select_upload_name, external_download_link) VALUES
	(33, 'download', 'Faça o download do histórico textual', 'internal_from_upload', 'HistTextual', NULL, NULL),
	(34, 'download', 'Faça o download do histórico visual', 'internal_from_upload', 'HistVisual', NULL, NULL),
    (35, 'download', 'Faça o download do comprovante de vínculo empregatício', 'internal_from_select_upload', NULL, 'Vinculo', NULL),
	(36, 'download', 'Faça o download do PA assinado pelo aluno', 'internal_from_upload', 'PAAluno', NULL, NULL),
	(37, 'download', 'Faça o download do PA assinado pelo aluno e orientador', 'internal_from_upload', 'PAOrientador', NULL, NULL),
	(38, 'download', 'Faça o download do PA completamente assinado', 'internal_from_upload', 'PACoordenador', NULL, NULL),
	(39, 'download', 'Faça o download do TCE assinado pelo aluno', 'internal_from_upload', 'TCEAluno', NULL, NULL),
	(40, 'download', 'Faça o download do TCE assinado pelo aluno e orientador', 'internal_from_upload', 'TCEOrientador', NULL, NULL),
	(41, 'download', 'Faça o download do TCE completamente assinado', 'internal_from_upload', 'TCECoordenador', NULL, NULL),
	(42, 'download', 'Faça o download do relatório parcial assinado pelo aluno', 'internal_from_upload', 'RelParcialAluno', NULL, NULL),
	(43, 'download', 'Faça o download do relatório parcial assinado pelo aluno e coordenador', 'internal_from_upload', 'RelParcialCoordenador', NULL, NULL),
	(44, 'download', 'Faça o download do relatório final assinado pelo aluno', 'internal_from_upload', 'RelFinalAluno', NULL, NULL),
	(45, 'download', 'Faça o download do relatório parcial assinado pelo aluno e coordenador', 'internal_from_upload', 'RelFinalCoordenador', NULL, NULL);
INSERT INTO dynamic_component_button (dynamic_component_id, dynamic_component_type, button_label, button_color, button_transation_type) VALUES 
	(46, 'button', 'Solicitar', 'darkblue', 'Request'),
    (47, 'button', 'Cancelar', 'black', 'Cancel'),
    (48, 'button', 'Enviar', 'darkblue', 'Send'),
    (49, 'button', 'Enviar e deferir', 'darkblue', 'Send and Defer'),
    (50, 'button', 'Deferir', 'darkblue', 'Defer'),
    (51, 'button', 'Indeferir', 'red', 'Reject');
INSERT INTO dynamic_page_has_component (dynamic_page_id, dynamic_component_id, dynamic_component_order) VALUES 
	(1,1,1), (1,19,2), (1,20,3), (1,32,4), (1,46,5), (1,47,6),
    (2,1,1), (2,19,2), (2,20,3), (2,46,4), (2,47,5),
    (3,2,1), (3,19,2), (3,20,3), (3,46,4), (3,47,5),
    (4,2,1), (4,19,2), (4,20,3), (4,46,4), (4,47,5),
    
    (5,3,1), (5,33,2), (5,34,3), (5,35,4), (5,50,5), (5,51,6), (5,47,7),
    (6,4,1), (6,33,2), (6,34,3), (6,50,4), (6,51,5), (6,47,6),
    
    (7,5,1), (7,18,2), (7,21,3), (7,46,4), (7,47,5),
    (8,6,1), (8,36,2), (8,22,3), (8,48,4), (8,47,5),
    (9,7,1), (9,36,2), (9,37,3), (9,23,4), (9,49,5), (9,51,6), (9,47,7),
    (10,11,1), (10,38,2),
    
    (11,8,1), (11,18,2), (11,24,3), (11,21,4), (11,46,5), (11,47,6),
    (12,9,1), (12,39,2), (12,36,3), (12,25,4), (12,22,5), (12,48,6), (12,47,7),
    (13,10,1), (13,39,2), (13,34,3), (13,40,4), (13,37,5), (13,26,6), (13,23,7), (13,49,8), (13,51,9), (13,47,10),
    (14,11,1), (14,41,2), (14,38,3),
    
    (15,12,1), (15,27,2), (15,46,3), (15,47,4),
    (16,13,1), (16,42,2), (16,28,3), (16,49,4), (16,51,5), (16,47,6),
    (17,14,1), (17,43,2),
    
    (18,15,1), (18,29,2), (18,46,3), (18,47,4),
    (19,16,1), (19,44,2), (19,32,3), (19,49,4), (19,51,5), (19,47,6),
    (20,17,1), (20,45,2);

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
INSERT INTO dynamic_mail (mail_subject, mail_body_html, is_sent_to_student, is_sent_to_advisor, is_sent_to_coordinator) VALUES 
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
			'<p>O orientador, coordenador e o setor de estágios SESTA podem demorar até 10 dias úteis no processo.</p>'
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
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_state_id_from) REFERENCES solicitation_state(id),
    FOREIGN KEY (solicitation_state_id_to) REFERENCES solicitation_state(id)
);
CREATE TABLE solicitation_state_transition_manual(
	solicitation_state_transition_id INT NOT NULL,
    transition_decision ENUM('Em analise', 'Solicitado', 'Enviado', 'Deferido', 'Indeferido', 'Cancelado pelo aluno', 'Cancelado pelo orientador', 'Cancelado pela coordenação') DEFAULT 'Em analise' NOT NULL,
    transition_reason VARCHAR(100) NOT NULL,
    PRIMARY KEY (solicitation_state_transition_id),
    FOREIGN KEY (solicitation_state_transition_id) REFERENCES solicitation_state_transition(id)
);
CREATE TABLE solicitation_state_transition_from_dynamic_page(
	solicitation_state_transition_id INT NOT NULL,
    dynamic_page_component ENUM('Button-Request', 'Button-Cancel', 'Button-Send', 'Button-Send and Defer', 'Button-Defer', 'Button-Reject', 'Table-Cancel') NOT NULL,
	transition_decision ENUM('Em analise', 'Solicitado', 'Enviado', 'Deferido', 'Indeferido', 'Cancelado pelo aluno', 'Cancelado pelo orientador', 'Cancelado pela coordenação') DEFAULT 'Em analise' NOT NULL,
    transition_reason VARCHAR(100) NOT NULL,
    PRIMARY KEY (solicitation_state_transition_id),
    FOREIGN KEY (solicitation_state_transition_id) REFERENCES solicitation_state_transition(id)
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
    decision ENUM('Em analise', 'Solicitado', 'Enviado', 'Deferido', 'Indeferido', 'Cancelado pelo aluno', 'Cancelado pelo orientador', 'Cancelado pela coordenação') DEFAULT 'Em analise' NOT NULL,
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
INSERT INTO solicitation_state (solicitation_id, state_description, state_max_duration_days, state_dynamic_page_id, state_static_page_name, is_initial_state) VALUES
	(1, 'Solicitação de avaliação dos históricos e complementos pelo aluno', 4, 1, NULL, TRUE),
    (1, 'Avaliação dos históricos e complementos pelo coordenador', 4, 5, NULL, FALSE),
    (1, 'Escolha de orientador pelo aluno', 4, NULL, 'interbegin-advisorselection', FALSE),
    (1, 'Aceite de orientado pelo orientador', 4, NULL, 'interbegin-advisoracception', FALSE),
	(1, 'Processo de assinaturas para início de estágio', 15, NULL, 'interbegin-signatures', FALSE),
    (1, 'Estágio iniciado', NULL, 14, NULL, FALSE);
INSERT INTO solicitation_state_profile_editors (solicitation_state_id, state_profile_editor) VALUES 
	(1, 4),
    (2, 2),
    (3, 4),
    (4, 3),
    (5, 2), (5, 3), (5, 4);
INSERT INTO solicitation_state_transition (solicitation_state_id_from, solicitation_state_id_to) VALUES 
	(1, 2), 
    (1, NULL),
    (2, 3),
    (2, NULL),
    (2, NULL),
    (3, 4),
    (3, NULL),
    (4, 5),
    (4, NULL),
    (4, NULL);

INSERT INTO solicitation_state_transition_manual (solicitation_state_transition_id, transition_decision, transition_reason) VALUES
    (6, 'Solicitado', 'O aluno solicitou a orientação ao orientador'), (7, 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
    (8, 'Deferido', 'O orientador aceitou a solicitação'), (9, 'Indeferido', 'O orientador não aceitou a solicitação'), (10, 'Cancelado pelo orientador', 'O orientador cancelou a solicitação');
    
INSERT INTO solicitation_state_transition_from_dynamic_page (solicitation_state_transition_id, dynamic_page_component, transition_decision, transition_reason) VALUES 
	(1, 'Button-Request', 'Solicitado', 'O aluno solicitou avaliação de documentos à coordenação de estágios'), (2, 'Button-Cancel', 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
    (3, 'Button-Defer', 'Deferido', 'A documentação do aluno está aprovada'), (4, 'Button-Reject', 'Indeferido', 'A documentação do aluno está com algum problema'), (5, 'Button-Cancel', 'Cancelado pela coordenação', 'Foi cancelado a solicitação pela coordenação');
/*	
INSERT INTO solicitation_state_dynamic_mail (solicitation_state_id, dynamic_mail_id) VALUES
	(1, 1),
    (2, 2);
INSERT INTO solicitation_state (solicitation_id, state_profile_editor, state_description, state_max_duration_days, state_dynamic_page_id, state_static_page_name, is_initial_state) VALUES
	(1, 4, 'Solicitação de avaliação dos históricos e complementos pelo aluno', 4, 1, NULL, TRUE),
    (1, 2, 'Avaliação dos históricos e complementos pelo coordenador', 4, 5, NULL, False),
    (1, 4, 'Escolha de orientador pelo aluno', 4, NULL, 'interbegin-advisorselection', False),
    (1, 3, 'Aceite de orientado pelo orientador', 4, NULL, 'interbegin-advisoracception', False),
	(1, 4, 'Solicitação de assinaturas do PA pelo aluno', 4, 7, NULL, False),
    (1, 3, 'Requerimento de assinatura do PA ao orientador', 4, 8, NULL, False),
    (1, 2, 'Requerimento de assinatura do PA ao coordenador', 10, 9, NULL, False),
    (1, NULL, 'Estágio iniciado', NULL, 10, NULL, False),
    
    (2, 4, 'Solicitação de avaliação dos históricos pelo aluno', 4, 2, NULL, TRUE),
    (2, 2, 'Avaliação dos históricos pelo coordenador', 4, 6, NULL, False),
	(2, 4, 'Solicitação de assinaturas do TCE e PA pelo aluno', 4, 11, NULL, False),
    (2, 3, 'Requerimento de assinatura do TCE e PA ao orientador', 4, 12, NULL, False),
    (2, 2, 'Requerimento de assinatura do TCE e PA ao coordenador', 10, 13, NULL, False),
    (2, NULL, 'Estágio iniciado', NULL, 14, NULL, False),
    
    (3, 4, 'Solicitação de avaliação dos históricos pelo aluno', 4, 3, NULL, TRUE),
    (3, 2, 'Avaliação dos históricos pelo coordenador', 4, 6, NULL, False),
	(3, 4, 'Solicitação de assinaturas do TCE e PA pelo aluno', 4, 11, NULL, False),
    (3, 3, 'Requerimento de assinatura do TCE e PA ao orientador', 4, 12, NULL, False),
    (3, 2, 'Requerimento de assinatura do TCE e PA ao coordenador', 10, 13, NULL, False),
    (3, NULL, 'Estágio iniciado', NULL, 14, NULL, False),
    
    (4, 4, 'Solicitação de avaliação dos históricos pelo aluno', 4, 4, NULL, TRUE),
    (4, 2, 'Avaliação dos históricos pelo coordenador', 4, 6, NULL, False),
	(4, 4, 'Solicitação de assinaturas do TCE e PA pelo aluno', 4, 11, NULL, False),
    (4, 3, 'Requerimento de assinatura do TCE e PA ao orientador', 4, 12, NULL, False),
    (4, 2, 'Requerimento de assinatura do TCE e PA ao coordenador', 10, 13, NULL, False),
    (4, NULL, 'Estágio iniciado', NULL, 14, NULL, False),
    
    (5, 4, 'Solicitação de avaliação e complemento de assinaturas do relatório parcial pelo aluno', 4, 15, NULL, TRUE),
    (5, 2, 'Avaliação e assinatura do relatório parcial pelo coordenador', 4, 16, NULL, False),
    (5, NULL,  'Relatório parcial completo', NULL, 17, NULL, False),
    
    (6, 4, 'Solicitação de avaliação e complemento de assinaturas do relatório final pelo aluno', 4, 18, NULL, TRUE),
    (6, 2, 'Avaliação e assinatura do relatório final pelo coordenador', 4, 19, NULL, False),
    (6, NULL, 'Relatório final completo', NULL, 20, NULL, False);
*/
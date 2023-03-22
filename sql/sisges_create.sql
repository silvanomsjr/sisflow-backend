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
	("AlunoVitor_HistTextual_1Ok9uqsqIj.pdf");
    
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

/* Solicitation and its associated dynamic data */
CREATE TABLE solicitation(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_name VARCHAR(256),
    PRIMARY KEY (id)
);

CREATE TABLE solicitation_step(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_id INT NOT NULL,
    step_profile_editor INT,
    step_order_in_solicitation INT NOT NULL,
    step_description VARCHAR(256),
    step_max_duration_days INT,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_id) REFERENCES solicitation(id),
    FOREIGN KEY (step_profile_editor) REFERENCES profile(id)
);

CREATE TABLE dynamic_page(
	id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(256) NOT NULL,
    top_inner_html VARCHAR(2000),
    mid_inner_html VARCHAR(2000),
    bot_inner_html VARCHAR(2000),
    inputs JSON,
    downloads JSON,
    uploads JSON,
    select_uploads JSON,
    is_solicitation_button_active BOOL DEFAULT TRUE,
    PRIMARY KEY (id)
);

CREATE TABLE dynamic_mail(
	id INT NOT NULL AUTO_INCREMENT,
    mail_subject VARCHAR(100),
    mail_body_html VARCHAR(2000),
    is_sent_to_student BOOL DEFAULT FALSE,
    is_sent_to_professor BOOL DEFAULT FALSE,
    is_sent_to_coordinator BOOL DEFAULT FALSE,
    PRIMARY KEY (id)
);

CREATE TABLE solicitation_step_page(
	solicitation_step_id INT NOT NULL,
    use_dynamic_page BOOL DEFAULT TRUE,
    dynamic_page_id INT,
    static_page_name VARCHAR(100),
    PRIMARY KEY (solicitation_step_id),
    FOREIGN KEY (solicitation_step_id) REFERENCES solicitation_step(id),
    FOREIGN KEY (dynamic_page_id) REFERENCES dynamic_page(id)
);

CREATE TABLE solicitation_step_dynamic_mail(
	id INT NOT NULL AUTO_INCREMENT,
    solicitation_step_id INT NOT NULL,
    dynamic_mail_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (solicitation_step_id) REFERENCES solicitation_step(id),
    FOREIGN KEY (dynamic_mail_id) REFERENCES dynamic_mail(id)
);

CREATE TABLE user_has_solicitation(
	id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    professor_siape VARCHAR(15),
    solicitation_id INT NOT NULL,
    actual_solicitation_step_order INT NOT NULL,
    
    decision ENUM('Em analise', 'Deferido', 'Indeferido') NOT NULL,
    reason VARCHAR(100),
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME,
    
    solicitation_user_data JSON,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES user_account(id),
    FOREIGN KEY (professor_siape) REFERENCES user_has_profile_professor_data(siape),
    FOREIGN KEY (solicitation_id) REFERENCES solicitation(id)
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

INSERT INTO dynamic_mail (mail_subject, mail_body_html, is_sent_to_student, is_sent_to_professor, is_sent_to_coordinator) VALUES 
	(
		'Sistema de estágios - Solicitação de avaliação dos históricos e complementos',
        '<p>Olá [[[ifMale?aluno:::aluna]]] [[[ifBCC?do BCC:::do BSI]]] [[[userName]]]</p>'
		'<p>Você solicitou ao coordenador de estágios a avaliação dos seus históricos e comprovante de vínculo empregatício.</p>'
			'<p>O coordenador de estágios possui até 4 dias úteis para realizar a avaliação retornando se a solicitação foi deferida ou indeferida.</p>'
			'<br>'
			'<p>Não esqueça de verificar sua caixa de mensagens e a plataforma de estágios para novidades neste período.</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de avaliação dos históricos completa',
        '<p>Olá [[[ifMale?aluno:::aluna]]] [[[ifBCC?do BCC:::do BSI]]] [[[userName]]]</p>'
			'<p>O coordenador avaliou os históricos e comprovante de vínculo empregatício.</p>'
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
    );

INSERT INTO solicitation_step_dynamic_mail (solicitation_step_id, dynamic_mail_id) VALUES
	(1, 1),
    (2, 2),
    (3, 3),
    (7, 1),
    (8, 2),
    (9, 3),
    (13, 1),
    (14, 2),
    (15, 3),
    (19, 1),
    (20, 2),
    (21, 3);
    
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
			{"label_txt" : "Envie seu histórico textual", "file_abs_type" : "HistTextual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{"label_txt" : "Envie seu histórico visual", "file_abs_type" : "HistVisual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
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
        'Solicitação de inicio de estágio obrigatório com vínculo - Verificação de documentos pela coordenação',
        '<p>Olá coordenador [[[coordinatorName]]]. Segue abaixo a documentação do aluno para download caso necessário:</p>',
		'',
        '',
        NULL,
        '[
			{"label_txt" : "Download do histórico textual", "file_abs_type" : "HistTextual" },
			{"label_txt" : "Download do histórico visual", "file_abs_type" : "HistVisual" }
		]',
        NULL,
		NULL,
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
			{"label_txt" : "Envie seu histórico textual", "file_abs_type" : "HistTextual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{"label_txt" : "Envie seu histórico visual", "file_abs_type" : "HistVisual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
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
			{"label_txt" : "Envie seu histórico textual", "file_abs_type" : "HistTextual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{"label_txt" : "Envie seu histórico visual", "file_abs_type" : "HistVisual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
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
			{"label_txt" : "Envie seu histórico textual", "file_abs_type" : "HistTextual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{"label_txt" : "Envie seu histórico visual", "file_abs_type" : "HistVisual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
		]',
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
        '[{"label_txt" : "Envie o PA com sua assinatura", "file_abs_type" : "PA", "required": true, "missing_msg": "O envio do PA é obrigatório!" }]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura do professor orientador',
        '<p>Olá orientador. Segue abaixo o PA enviado pelo aluno para a sua assinatura:</p>',
		'',
        '',
        NULL,
        '[{"label_txt" : "Download do PA", "file_abs_type" : "PA" }]',
        '[{"label_txt" : "Envie o PA com sua assinatura", "file_abs_type" : "PA", "required": true, "missing_msg": "O envio do PA é obrigatório!" }]',
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
			{"label_txt" : "Download do PA Aluno", "file_abs_type" : "PA" },
            {"label_txt" : "Download do PA Professor", "file_abs_type" : "PA" }
		]',
        '[{"label_txt" : "Envie o PA com sua assinatura", "file_abs_type" : "PA", "required": true, "missing_msg": "O envio do PA é obrigatório!" }]',
		NULL,
		TRUE
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
        '[{"label_txt" : "Envie o TCE com sua assinatura", "file_abs_type" : "TCE", "required": true, "missing_msg": "O envio do TCE é obrigatório!" },
			{"label_txt" : "Envie o PA com sua assinatura", "file_abs_type" : "PA", "required": false, "missing_msg": "O envio do PA é opcional desde que suas informações estejam no TCE" }]',
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
        NULL,
        '[{"label_txt" : "Download dos documentos assinados", "file_abs_type" : "TCE", "required": true, "missing_msg": "O envio do TCE é obrigatório!" }]',
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
        '[{"label_txt" : "Envie o relatório parcial com sua assinatura", "file_abs_type" : "RelParcial", "required": true, "missing_msg": "O envio do relatório parcial é obrigatório!"}]',
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
        '[{"label_txt" : "Relatório parcial completo", "file_abs_type" : "RelParcial", "required": true, "missing_msg": "O download do relatório parcial é obrigatório!" }]',
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
        '[{"label_txt" : "Envie o relatório final com sua assinatura", "file_abs_type" : "RelFinal", "required": true, "missing_msg": "O envio do relatório final é obrigatório!" }]',
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
        '[{"label_txt" : "Relatório final completo", "file_abs_type" : "RelFinal", "required": true, "missing_msg": "O download do relatório final é obrigatório!" }]',
        NULL,
		FALSE
	);

INSERT INTO solicitation_step_page (solicitation_step_id, use_dynamic_page, dynamic_page_id, static_page_name) VALUES
	(1, TRUE, 1, NULL),
    (2, TRUE, 2, NULL),
    (3, TRUE, 6, NULL),
    (4, TRUE, 7, NULL),
    (5, TRUE, 8, NULL),
    (6, TRUE, 10, NULL),
    
    (7, TRUE, 3, NULL),
    (8, TRUE, 2, NULL),
    (9, TRUE, 9, NULL),
    (10, TRUE, 7, NULL),
    (11, TRUE, 8, NULL),
    (12, TRUE, 10, NULL),
    
    (13, TRUE, 4, NULL),
    (14, TRUE, 2, NULL),
    (15, TRUE, 9, NULL),
    (16, TRUE, 7, NULL),
    (17, TRUE, 8, NULL),
    (18, TRUE, 10, NULL),
    
    (19, TRUE, 5, NULL),
    (20, TRUE, 2, NULL),
    (21, TRUE, 9, NULL),
    (22, TRUE, 7, NULL),
    (23, TRUE, 8, NULL),
    (24, TRUE, 10, NULL),
    
    (25, TRUE, 11, NULL),
    (26, TRUE, 12, NULL),
    
    (27, TRUE, 13, NULL),
    (28, TRUE, 14, NULL);
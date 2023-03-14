/* Configuracao do sistema */
CREATE TABLE config(
	id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(50),
    PRIMARY KEY (id)
);

CREATE TABLE config_path(
	config_id INT NOT NULL,
	path_str VARCHAR(256),
    PRIMARY KEY (config_id),
    FOREIGN KEY (config_id) REFERENCES config(id)
);

CREATE TABLE config_mail(
	config_id INT NOT NULL,
	mail_str VARCHAR(256),
    PRIMARY KEY (config_id),
    FOREIGN KEY (config_id) REFERENCES config(id)
);

/* Dados usuarios */
CREATE TABLE conta_usuario(
	id INT NOT NULL AUTO_INCREMENT,
    email_ins VARCHAR(256) NOT NULL UNIQUE,
    email_sec VARCHAR(256),
    nome VARCHAR(100) NOT NULL,
    sexo ENUM('M', 'F') NOT NULL,
    curso ENUM('BCC', 'BSI'),
    telefone VARCHAR(15),
    hash_senha CHAR(65),
    salt_senha CHAR(16),
    data_hora_criacao DATETIME,
    PRIMARY KEY (id)
);

CREATE TABLE possui_perfil(
	id INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME,
	PRIMARY KEY (id),
    FOREIGN KEY (id_usuario) REFERENCES conta_usuario(id)
);

CREATE TABLE perfil(
	id INT NOT NULL,
    sigla VARCHAR(2) NOT NULL,
    json_dados JSON,
    PRIMARY KEY (id),
	FOREIGN KEY (id) REFERENCES possui_perfil(id)
);

CREATE TABLE estado(
	id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(50),
    tipo VARCHAR(50),
    descricao VARCHAR(100),
    PRIMARY KEY (id)
);

CREATE TABLE possui_estado(
	id INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_estado INT NOT NULL,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY (id_usuario) REFERENCES conta_usuario(id),
    FOREIGN KEY (id_estado) REFERENCES estado(id)
);

CREATE TABLE anexo(
	hash_anexo VARCHAR(150) NOT NULL,
    id_usuario INT NOT NULL,
    PRIMARY KEY (hash_anexo),
    FOREIGN KEY (id_usuario) REFERENCES conta_usuario(id)
);

/* Codigo de segurança */
CREATE TABLE validacao_email(
	email_ins VARCHAR(256) NOT NULL,
    codigo CHAR(10),
    tempo_expirar TIMESTAMP,
    PRIMARY KEY (email_ins),
    FOREIGN KEY (email_ins) REFERENCES conta_usuario(email_ins)
);

CREATE TRIGGER validacao_email_definir_expirar BEFORE INSERT ON validacao_email 
    FOR EACH ROW 
    SET NEW.tempo_expirar = NOW() + INTERVAL 8 HOUR;

CREATE EVENT IF NOT EXISTS expirar_token_validacao_email 
	ON SCHEDULE EVERY 1 HOUR
	COMMENT 'Remove tokens de cadastro expirados'
	DO DELETE FROM validacao_email WHERE tempo_expirar < NOW();

/* solicitacoes suas etapas e paginas dinamicas relacionadas */
CREATE TABLE solicitacao(
	id INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(256),
    PRIMARY KEY (id)
);

CREATE TABLE etapa_solicitacao(
	id INT NOT NULL AUTO_INCREMENT,
    id_solicitacao INT NOT NULL,
    ordem_etapa_solicitacao INT NOT NULL,
    descricao VARCHAR(256),
    duracao_maxima_dias INT,
    PRIMARY KEY (id),
    FOREIGN KEY (id_solicitacao) REFERENCES solicitacao(id)
);

CREATE TABLE pagina_dinamica(
	id INT NOT NULL AUTO_INCREMENT,
    titulo VARCHAR(256),
    perfis_permitidos VARCHAR(50),
    top_inner_html VARCHAR(2000),
    mid_inner_html VARCHAR(2000),
    bot_inner_html VARCHAR(2000),
    inputs JSON,
    anexos JSON,
    select_anexos JSON,
    botao_solicitar BOOL,
    PRIMARY KEY (id)
);

CREATE TABLE mensagem_dinamica(
	id INT NOT NULL AUTO_INCREMENT,
    msg_assunto VARCHAR(100),
    msg_html VARCHAR(2000),
    enviar_aluno BOOL DEFAULT false,
    enviar_professor BOOL DEFAULT false,
    enviar_coordenador BOOL DEFAULT false,
    PRIMARY KEY (id)
);

CREATE TABLE etapa_solicitacao_pagina(
	id_etapa_solicitacao INT NOT NULL,
    id_pagina_dinamica INT,
    nome_pagina_estatica VARCHAR(100),
    PRIMARY KEY (id_etapa_solicitacao),
    FOREIGN KEY (id_etapa_solicitacao) REFERENCES etapa_solicitacao(id),
    FOREIGN KEY (id_pagina_dinamica) REFERENCES pagina_dinamica(id)
);

CREATE TABLE etapa_solicitacao_mensagem(
	id INT NOT NULL AUTO_INCREMENT,
    id_etapa_solicitacao INT NOT NULL,
    id_mensagem_dinamica INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (id_etapa_solicitacao) REFERENCES etapa_solicitacao(id),
    FOREIGN KEY (id_mensagem_dinamica) REFERENCES mensagem_dinamica(id)
);

CREATE TABLE possui_etapa_solicitacao(
	id INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_etapa_solicitacao INT NOT NULL,
    decisao ENUM('Em analise', 'Deferido', 'Indeferido') NOT NULL,
    motivo VARCHAR(100),
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME,
    json_dados JSON,
    PRIMARY KEY (id),
    FOREIGN KEY (id_usuario) REFERENCES conta_usuario(id),
    FOREIGN KEY (id_etapa_solicitacao) REFERENCES etapa_solicitacao(id)
);

INSERT INTO config(nome) VALUES
	("root path key files"),
    ("root path user files"),
    ("coordinator mail");
    
INSERT INTO config_path(config_id, path_str) VALUES
	(1, "/sisges/secrets/"),
	(2, "/sisges/userfiles/");
    
INSERT INTO config_mail(config_id, mail_str) VALUES
	(3, "prof.asoares@ufu.br");

INSERT INTO conta_usuario (email_ins, email_sec, nome, sexo, curso, telefone, hash_senha, salt_senha, data_hora_criacao) VALUES
	("admin@ufu.br", "admin@gmail.com","Admin", 'M', 'BCC', "34111111111","96c287e89a2edf3e807560fd79d8a064b4248846379ab9fe691e2bc158e8293f","btoUCZer0lROFz0e",now()),
    ("alunobsi@ufu.br", "alunobsisec@gmail.com","Aluno do BSI", 'M', "BSI","34222222222","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
	("alunabcc@ufu.br", "alunabccsec@gmail.com","Aluna do BCC", 'F', "BCC","34111111111","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("viniciuscalixto.grad@ufu.br", "viniciuscalixto.grad@gmail.com","Vinicius Calixto Rocha", 'M', "BCC", NULL, NULL, NULL, NULL),
    ("prof.asoares@ufu.br","prof.asoares@gmail.com", "Alexsandro Santos Soares", 'M', NULL, NULL, NULL, NULL, NULL);

INSERT INTO possui_perfil (id_usuario, data_hora_inicio, data_hora_fim) VALUES 
	(1, NOW(), NULL),
    (2, NOW(), NULL),
    (3, NOW(), NULL),
    (4, NOW(), NULL),
    (5, NOW(), NULL);

INSERT INTO perfil (id, sigla, json_dados) VALUES
	(1, "P", '{"siape":"SIAPE111111"}'),
    (2, "A", '{"matricula":"11111BSI111"}'),
    (3, "A", '{"matricula":"99999BCC999"}'),
    (4, "A", '{"matricula":"11911BCC039"}'),
    (5, "P", '{"siape":"SIAPEalex"}');

INSERT INTO solicitacao (nome) VALUES 
	('Inicio de estágio obrigatório externo com vinculo empregatício'),
    ('Inicio de estágio obrigatório externo sem vinculo empregatício'),
    ('Inicio de estágio não obrigatório externo'),
    ('Inicio de estágio não obrigatório interno'),
    ('Envio de relatório parcial'),
    ('Envio de relatório final');

INSERT INTO etapa_solicitacao (id_solicitacao, ordem_etapa_solicitacao, descricao, duracao_maxima_dias) VALUES 
	(1, 1, 'Solicitação de avaliação dos históricos e complementos', 4),
    (1, 2, 'Requerimento de complemento de assinaturas de documentos', 10),
    (1, 3, 'Estágio iniciado', NULL),
    
    (2, 1, 'Solicitação de avaliação dos históricos', 4),
    (2, 2, 'Requerimento de complemento de assinaturas de documentos', 10),
    (2, 3, 'Estágio iniciado', NULL),
    
    (3, 1, 'Solicitação de avaliação dos históricos', 4),
    (3, 2, 'Requerimento de complemento de assinaturas de documentos', 10),
    (3, 3, 'Estágio iniciado', NULL),
    
    (4, 1, 'Solicitação de avaliação dos históricos', 4),
    (4, 2, 'Requerimento de complemento de assinaturas de documentos', 10),
    (4, 3, 'Estágio iniciado', NULL),
    
    (5, 1, 'Requerimento de avaliação e complemento de assinaturas do relatório parcial', 10),
    (5, 2, 'Relatório parcial completo', NULL),
    
    (6, 1, 'Requerimento de avaliação e complemento de assinaturas do relatório final', 10),
    (6, 2, 'Relatório final e estágio completos', NULL);

INSERT INTO mensagem_dinamica (msg_assunto, msg_html, enviar_aluno, enviar_professor, enviar_coordenador) VALUES 
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
		'Sistema de estágios - Solicitação de assinaturas para início de estágio',
        '<p>Olá [[[ifMale?aluno:::aluna]]] [[[ifBCC?do BCC:::do BSI]]] [[[userName]]]</p>'
		'<p>Você solicitou ao coordenador de estágios o complemento de assinaturas para dar inicio ao estágio.</p>'
			'<p>O coordenador juntamente com o setor de estágios SESTA podem demorar até 10 dias úteis no processo.</p>'
			'<br>'
			'<p>Não esqueça de verificar sua caixa de mensagens e a plataforma de estágios para novidades neste período.</p>',
        TRUE, FALSE, FALSE
    );

INSERT INTO etapa_solicitacao_mensagem (id_etapa_solicitacao, id_mensagem_dinamica) VALUES
	(1, 1),
    (2, 2),
    (4, 1),
    (5, 2),
    (7, 1),
    (8, 2);
    
INSERT INTO pagina_dinamica (titulo, perfis_permitidos, top_inner_html, mid_inner_html, bot_inner_html, inputs, anexos, select_anexos, botao_solicitar) VALUES 
	(
        'Solicitação de inicio de estágio obrigatório com vínculo - Avaliação de históricos e comprovante de vínculo empregatício [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
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
        'Solicitação de inicio de estágio obrigatório sem vínculo - Avaliação de históricos [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
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
        '[
			{"label_txt" : "Envie seu histórico textual", "file_abs_type" : "HistTextual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{"label_txt" : "Envie seu histórico visual", "file_abs_type" : "HistVisual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio não obrigatório externo - Avaliação de históricos [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
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
        '[
			{"label_txt" : "Envie seu histórico textual", "file_abs_type" : "HistTextual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{"label_txt" : "Envie seu histórico visual", "file_abs_type" : "HistVisual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio não obrigatório interno - Avaliação de históricos [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
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
        '[
			{"label_txt" : "Envie seu histórico textual", "file_abs_type" : "HistTextual", "required": true, "missing_msg": "O envio do histórico textual é obrigatório!" },
			{"label_txt" : "Envie seu histórico visual", "file_abs_type" : "HistVisual", "required": true, "missing_msg": "O envio do histórico visual é obrigatório!"}
		]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
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
        '[{"label_txt" : "Envie o PA com sua assinatura", "file_abs_type" : "PA", "required": true, "missing_msg": "O envio do PA é obrigatório!" }]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia o TCE eo PA contendo a sua assinatura e aguarda a assinatura dos professores</p>',
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
        '[{"label_txt" : "Envie o TCE com sua assinatura", "file_abs_type" : "TCE", "required": true, "missing_msg": "O envio do TCE é obrigatório!" },
			{"label_txt" : "Envie o PA com sua assinatura", "file_abs_type" : "PA", "required": false, "missing_msg": "O envio do PA é opcional desde que suas informações estejam no TCE" }]',
		NULL,
		TRUE
	),
    (
        'Solicitação de inicio de estágio - Concluída',
        "['A']",
        '<p>Com todas as assinaturas a solicitação está concluída você já pode iniciar o estágio</p>'
        '<p>Realize o download abaixo da documentação assinada</p>',
		'',
        '',
        NULL,
        '[{"label_txt" : "Download dos documentos assinados", "file_abs_type" : "TCE", "required": true, "missing_msg": "O envio do TCE é obrigatório!" }]',
        NULL,
		FALSE
	),
    (
        'Envio de relatório parcial - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia os documentos relacionados ao relatório parcial contendo'
        ' a sua assinatura e aguarda os docentes assinarem</p>',
		'',
        '',
        NULL,
        '[{"label_txt" : "Envie o relatório parcial com sua assinatura", "file_abs_type" : "RelParcial", "required": true, "missing_msg": "O envio do relatório parcial é obrigatório!"}]',
        NULL,
		TRUE
	),
	(
        'Envio de relatório parcial - Concluído',
        "['A']",
        '<p>Com todas as assinaturas a solicitação está concluída</p>'
        '<p>Realize o download abaixo da documentação assinada</p>',
		'',
        '',
        NULL,
        '[{"label_txt" : "Relatório parcial completo", "file_abs_type" : "RelParcial", "required": true, "missing_msg": "O download do relatório parcial é obrigatório!" }]',
        NULL,
		FALSE
	),
    (
        'Envio de relatório final - Assinatura [[[ifMale?do aluno:::da aluna]]]',
        "['A']",
        '<p>Nesta etapa [[[ifMale?o aluno:::a aluna]]] envia os documentos relacionados ao relatório final contendo '
        'a sua assinatura e aguarda os docentes assinarem</p>',
		'',
        '',
        NULL,
        '[{"label_txt" : "Envie o relatório final com sua assinatura", "file_abs_type" : "RelFinal", "required": true, "missing_msg": "O envio do relatório final é obrigatório!" }]',
        NULL,
		TRUE
	),
    (
        'Envio de relatório final - Concluído',
        "['A']",
        '<p>Com todas as assinaturas a solicitação está concluída</p>'
        '<p>Realize o download abaixo da documentação assinada</p>',
		'',
        '',
        NULL,
        '[{"label_txt" : "Relatório final completo", "file_abs_type" : "RelFinal", "required": true, "missing_msg": "O download do relatório final é obrigatório!" }]',
        NULL,
		FALSE
	);

INSERT INTO etapa_solicitacao_pagina (id_etapa_solicitacao, id_pagina_dinamica, nome_pagina_estatica) VALUES
	(1, 1, NULL),
    (2, 5, NULL),
    (3, 7, NULL),
    (4, 2, NULL),
    (5, 6, NULL),
    (6, 7, NULL),
    (7, 3, NULL),
    (8, 6, NULL),
    (9, 7, NULL),
    (10, 4, NULL),
    (11, 6, NULL),
    (12, 7, NULL),
    (13, 8, NULL),
    (14, 9, NULL),
    (15, 10, NULL),
    (16, 11, NULL);
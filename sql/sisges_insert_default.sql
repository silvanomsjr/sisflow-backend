USE sisgesteste;

/* Sistem configurations */
INSERT INTO config(config_name) VALUES
	("root path key files"),
    ("root path user files"),
    ("coordinator mail"),
    ("reason class: geral student hist validation"),
    ("reason class: bcc student hist validation"),
    ("reason class: bsi student hist validation");
# Path COnfigurations
INSERT INTO config_system_path(config_id, system_path) VALUES
	(1, "../sisgesFiles/secrets/"),
	(2, "../sisgesFiles/userfiles/");
# Email Configurations
INSERT INTO config_mail(config_id, mail, mail_name) VALUES
	(3, "prof.asoares@ufu.br", "Alexsandro Santos Soares");
# Reason class and reasons for reason tables
INSERT INTO config_reason_class(config_id, class_name) VALUES
	(4, "Validação Históricos Geral"),
	(5, "Validação Históricos BCC"),
    (6, "Validação Históricos BSI");
INSERT INTO config_reason(reason_class_id, inner_html) VALUES
	(4, 'O histórico textual [[[ifStudentMale?do aluno:::da aluna]]] está em formato inválido, acesse o mesmo pelo <a href="https://www.portalestudante.ufu.br/">Portal do Estudante UFU</a>'),
    (4, 'O histórico visual [[[ifStudentMale?do aluno:::da aluna]]] está em formato inválido, acesse o mesmo pelo <a href="https://www.portalestudante.ufu.br/">Portal do Estudante UFU</a>'),
    (4, 'O comprovante de vínculo empregatício [[[ifStudentMale?do aluno:::da aluna]]] está em formato inválido'),
	(5, '[[[ifStudentMale?O aluno:::A aluna]]] não possui concluído todas as matérias entre o 1º e o 4º período conforme solicita o Artigo 15 do capítulo III das '
		'<a href="https://facom.ufu.br/system/files/conteudo/sei_23117.080702_2022_71.pdf">Normas de Estagio do BCC</a>.'),
	(6, '[[[ifStudentMale?O aluno:::A aluna]]] não possui concluído com aproveitamento 1.200 horas-aula conforme solicita o Artigo 13 do capítulo IV das '
		'<a href="https://facom.ufu.br/system/files/conteudo/normasestagio_bsi.pdf">Normas de Estagio do BSI</a>.'),
	(6, '[[[ifStudentMale?O aluno:::A aluna]]] não está aprovado em todas as disciplinas do primeiro e segundo períodos conforme solicita o Artigo 14 do capítulo IV das '
		'<a href="https://facom.ufu.br/system/files/conteudo/normasestagio_bsi.pdf">Normas de Estagio do BSI</a>.'),
    (6, '[[[ifStudentMale?O aluno:::A aluna]]] não possui (CRA) mínimo de 60 conforme o Artigo 14 do capítulo IV das '
		'<a href="https://facom.ufu.br/system/files/conteudo/normasestagio_bsi.pdf">Normas de Estagio do BSI</a>.');
/* */
    
/* User data and Profiles */   
INSERT INTO user_account (institutional_email, secondary_email, user_name, gender, phone, password_hash, password_salt, creation_datetime) VALUES
	("admin@ufu.br", "admin@gmail.com","Admin", 'M', "34111111111","96c287e89a2edf3e807560fd79d8a064b4248846379ab9fe691e2bc158e8293f","btoUCZer0lROFz0e",now()),
    ("prof.asoares@ufu.br","prof.asoares@gmail.com", "Alexsandro Santos Soares", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
	("abdala@ufu.br", NULL, "Daniel Duarte Abdala", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("gina@ufu.br", NULL, "Gina Maira Barbosa de Oliveira", 'F', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("luiz@ufu.br", NULL, "Luiz Gustavo Almeida Martins", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("maia@ufu.br", NULL, "Marcelo de Almeida Maia", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("stephane@ufu.br", NULL,"Stéphane Julia", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("adriano@ufu.br", NULL,"Adriano Mendonça Rocha", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("eliana@ufu.br", NULL,"Eliana Pantaleão", 'F', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("ivan@ufu.br", NULL,"Ivan da Silva Sendin", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("leandro@ufu.br", NULL,"Leandro Nogueira Couto", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("mauricio@ufu.br", NULL,"Mauricio Cunha Escarpinati", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("aluno@ufu.br", "aluno@gmail.com","Vitor Borges", 'M', "34222222222","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
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
    (8, 3, NULL, NOW(), NULL),
    (9, 3, NULL, NOW(), NULL),
    (10, 3, NULL, NOW(), NULL),
    (11, 3, NULL, NOW(), NULL),
    (12, 3, NULL, NOW(), NULL),
    (13, 4, NULL, NOW(), NULL),
    (14, 4, NULL, NOW(), NULL);
INSERT INTO user_has_profile_coordinator_data (user_has_profile_id, siape) VALUES
	(2, 'SIAPE-ALEX');
INSERT INTO user_has_profile_advisor_data (user_has_profile_id, siape)  VALUES
	(3, 'SIAPE-ALEX'),
	(4, 'SIAPE-ABDALA'),
    (5, 'SIAPE-GINA'),
    (6, 'SIAPE-LUIZ'),
    (7, 'SIAPE-MAIA'),
    (8, 'SIAPE-STEPHANE'),
    (9, 'SIAPE-ADRIANO'),
    (10, 'SIAPE-ELIANA'),
    (11, 'SIAPE-IVAN'),
    (12, 'SIAPE-LEANDRO'),
    (13, 'SIAPE-MAURICIO');
INSERT INTO user_has_profile_student_data (user_has_profile_id, matricula, course) VALUES
	(14, '11111BSI111', 'BSI'),
    (15, '11911BCC039', 'BCC');

/* Dynamic page */
INSERT INTO dynamic_page (title) VALUES 
	('Solicitação de inicio de estágio obrigatório com vínculo - Envio de históricos e comprovante de vínculo empregatício'),
    ('Solicitação de inicio de estágio obrigatório sem vínculo - Envio de históricos'),
    ('Solicitação de inicio de estágio não obrigatório externo - Envio de históricos'),
    ('Solicitação de inicio de estágio não obrigatório interno - Envio de históricos'),
    
    ('Solicitação de inicio de estágio - Verificação de históricos e comprovantes do aluno pela coordenação'),
    ('Solicitação de inicio de estágio - Verificação de históricos do aluno pela coordenação'),
    
    ('Solicitação de inicio de estágio - Assinatura do PA [[[ifStudentMale?pelo aluno:::pela aluna]]]'),
    ('Solicitação de inicio de estágio - Assinatura do PA pelo orientador'),
    ('Solicitação de inicio de estágio - Assinatura do PA pela coordenação de estágios'),
    ('Solicitação de inicio de estágio - Concluída'),
    
    ('Solicitação de inicio de estágio - Assinatura do PA e TCE [[[ifStudentMale?pelo aluno:::pela aluna]]]'),
    ('Solicitação de inicio de estágio - Assinatura do PA e TCE pelo orientador'),
    ('Solicitação de inicio de estágio - Assinatura do PA e TCE pela coordenação de estágios'),
    ('Solicitação de inicio de estágio - Concluída'),
    
    ('Envio de relatório parcial - Assinatura [[[ifStudentMale?do aluno:::da aluna]]]'),
    ('Envio de relatório parcial - Assinatura da coordenação de estágios'),
    ('Envio de relatório parcial - Concluída'),
    
    ('Envio de relatório final - Assinatura [[[ifStudentMale?do aluno:::da aluna]]]'),
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
    ('button'),('button'),('button'),('button'),('button'),('button'),
    ('details'), ('details');
INSERT INTO dynamic_component_inner_html (dynamic_component_id, dynamic_component_type, inner_html) VALUES 
	(
		1, 
        'inner_html', 
		'<p>Nesta etapa [[[ifStudentMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifStudentMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio obrigatório no [[[ifBCCStudent? BCC ::: BSI ]]]:</p>'
            '[[[ifBCCStudent? 
				<p><b>Duração</b>: 10 a 20 semanas, <b>Carga horária mínima</b>: 210 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ::: 
				<p><b>Duração</b>: 16 a 32 semanas, <b>Carga horária mínima</b>: 440 horas com o máximo de 30 horas semanais, <b>Aprovação</b>: 1 ao 4 períodos completos</p>
            ]]]'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCCStudent?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>'
	),(
		2, 
        'inner_html', 
		'<p>Nesta etapa [[[ifStudentMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifStudentMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio não obrigatório no [[[ifBCCStudent? BCC ::: BSI ]]]:</p>'
            '<p><b>Duração</b>: 8 a 24 semanas, <b>Carga horária mínima</b>: 220 horas, <b>Aprovação</b>: 1 e 2 períodos completos</p>'
			'<p>Com carga horária de disciplinas acima de 1200 é possível estagiar de 30 horas semanais e, caso contrário, 20 horas</p>'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCCStudent?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
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
        '<p>Nesta etapa [[[ifStudentMale?o aluno:::a aluna]]] envia o Plano de Atividades(PA) contendo a sua assinatura e aguarda a assinatura dos docentes</p>'
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
        '<p>Nesta etapa [[[ifStudentMale?o aluno:::a aluna]]] envia o Termo de Compromisso de Estágio(TCE) e o Plano de Atividades(PA)'
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
        '<p>Nesta etapa [[[ifStudentMale?o aluno:::a aluna]]] envia o relatório parcial contendo a sua assinatura e aguarda os docentes assinarem</p>'
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
        '<p>Nesta etapa [[[ifStudentMale?o aluno:::a aluna]]] envia o relatório final contendo a sua assinatura e aguarda os docentes assinarem</p>'
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
INSERT INTO dynamic_component_details (dynamic_component_id, dynamic_component_type, details_type) VALUES
	(52, 'details', 'student'),
    (53, 'details', 'advisor');
INSERT INTO dynamic_page_has_component (dynamic_page_id, dynamic_component_id, dynamic_component_order) VALUES 
	(1,1,1), (1,19,2), (1,20,3), (1,32,4), (1,46,5), (1,47,6),
    (2,1,1), (2,19,2), (2,20,3), (2,46,4), (2,47,5),
    (3,2,1), (3,19,2), (3,20,3), (3,46,4), (3,47,5),
    (4,2,1), (4,19,2), (4,20,3), (4,46,4), (4,47,5),
    
    (5,3,1), (5,52,2), (5,33,3), (5,34,4), (5,35,5), (5,50,6), (5,51,7), (5,47,8),
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
    
/* dynamic mails */
INSERT INTO dynamic_mail (mail_subject, mail_body_html, is_sent_to_student, is_sent_to_advisor, is_sent_to_coordinator) VALUES
	(
		'Sistema de estágios: Inicio de processo de estágio',
        '<p>Olá [[[coordinatorName]]]</p>'
		'<p>Um aluno <b>criou uma solicitação</b> de estágio obrigatório com vínculo empregatício</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>',
        FALSE, FALSE, TRUE
    ),
	(
		'Sistema de estágios: Solicitação de avaliação dos históricos',
        '<p>Olá [[[coordinatorName]]]</p>'
		'<p>Você possui uma <b>solicitação de avaliação de históricos</b></p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>',
        FALSE, FALSE, TRUE
    ),
	(
		'Sistema de estágios: Solicitação de avaliação dos históricos',
        '<p>Olá [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>Você solicitou à coordenação de estágios a avaliação dos seus históricos</p>'
		'<p>A coordenação de estágios possui até 4 dias úteis para realizar a avaliação retornando se a solicitação foi deferida ou indeferida</p>'
		'<br>'
		'<p>Não esqueça de verificar sua caixa de mensagens e a plataforma de estágios para novidades neste período</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios: Cancelamento de inicio de processo de estágio',
        '<p>Olá [[[coordinatorName]]]</p>'
		'<p>Um aluno cancelou uma solicitação de estágio obrigatório com vínculo empregatício antes de solicitar a avaliação de históricos</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>',
        FALSE, FALSE, TRUE
    ),
    (
		'Sistema de estágios - Solicitação de avaliação dos históricos deferida',
        '<p>Olá [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>Sua documentação enviada para a solicitação de início de estágio foi <b>deferida</b></p>'
        '<br>'
		'<p>O próximo passo é a escolha de um orientador para seu estágio na plataforma</p>'
        '<p>O orientador deve concordar em ser seu orientador previamente bem como participar dos processos de assinaturas para a homologação dos documentos</p>'
        '<p>Mantenha seu orientador atualizado com as solicitações e procedimentos realizados na plataforma</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de avaliação dos históricos indeferida',
        '<p>Olá [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>Seus históricos enviados para início de estágio foram <b>indeferidos</b></p>'
        '<br>'
		'<p>Motivo: To be develop</p>'
        '<p>Artigo: To be develop</p>'
        '<p>Qualquer dúvida enviar um email para a coordenação de estágios: </p>'
        '<p>Você também pode solicitar ao colegiado apoio caso necessário</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de orientação',
        '<p>Olá [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]]</p>'
		'<p>[[[ifStudentMale?O aluno:::A aluna]]] [[[studentName]]] solicitou a sua orientação para o processo de estágio</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>'
        '<br>'
        '<p>Acesse a plataforma para aceitar ou recusar a solicitação</p>'
        '<p>Lembre-se de participar do processo de assinaturas no caso do aceite para a homologação dos documentos</p>',
        FALSE, TRUE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de orientação rejeitada',
        '<p>Olá [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>[[[ifAdvisorMale?O orientador:::A orientadora]]] [[[advisorName]]] rejeitou sua solicitação</p>'
        '<br>'
		'<p>Motivo: To be develop</p>'
        '<p>Artigo: To be develop</p>'
        '<p>Qualquer dúvida enviar um email para a coordenação de estágios: </p>'
        '<p>Você também pode solicitar ao colegiado apoio caso necessário</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Solicitação de orientação aceita e início de coleta de assinaturas',
        '<p>Olá [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>[[[ifAdvisorMale?O orientador:::A orientadora]]] [[[advisorName]]] aceitou sua solicitação</p>'
        '<br>'
		'<p>O próximo passo é a assinatura dos documentos para dar início ao estágio</p>'
        '<p>Nesta etapa as pessoas envolvidas no processo de inicio de estágio realizam a assinatura dos documentos Termo de Compromisso de Estágio(TCE) e Plano de Atividades(PA) e as enviam na plataforma para dar inicio ao estágio</p>'
        '<p>Para mais informações sobre estes documentos verifique as [[[ifBCCStudent?'
        '<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">normas de estagio do curso de Ciências da Computação</a>.</p>:::'
		'<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">normas de estagio do curso de Sistemas de Informação</a>.</p>]]]'
        '</p>'
        '<p>Seguir a ordem de assinaturas: Aluno, Supervisor e Orientador</p>'
        '<p>Envie os documentos mais recentes na plataforma para validação da coordenação</p>'
        '<p>Mantenha seu orientador e supervisor atualizados com as solicitações e procedimentos realizados na plataforma</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Início de coleta de assinaturas',
        '<p>Olá [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]]</p>'
		'<p>O processo de coleta de assinaturas para homologação do estágio [[[ifStudentMale?do aluno:::da aluna]]] [[[studentName]]] foi iniciado</p>'
        '<p>Nesta etapa as pessoas envolvidas no processo de inicio de estágio realizam a assinatura dos documentos Termo de Compromisso de Estágio(TCE) e Plano de Atividades(PA) e as enviam na plataforma para dar inicio ao estágio</p>'
		'<p>Para mais informações sobre estes documentos verifique as [[[ifBCCStudent?'
        '<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">normas de estagio do curso de Ciências da Computação</a>.</p>:::'
		'<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">normas de estagio do curso de Sistemas de Informação</a>.</p>]]]'
        '</p>'
        '<p>É importante seguir a ordem de assinaturas: Aluno, Supervisor e Orientador</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>'
        '<br>'
        '<p>Acesse a plataforma para realizar o envio do documento com sua assinatura caso for necessário</p>',
        FALSE, TRUE, FALSE
    ),
    (
		'Sistema de estágios - Início de coleta de assinaturas',
        '<p>Olá [[[coordinatorName]]]</p>'
        '<p>[[[ifAdvisorMale?O orientador:::A orientadora]]] [[[advisorName]]] aceitou a solicitação [[[ifStudentMale?do aluno:::da aluna]]] [[[studentName]]]</p>'
		'<p>Com isso, <b>o processo de coleta de assinaturas iniciou</b></p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        FALSE, FALSE, TRUE
    ),
    
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]]</p>'
        '<br>'
        '<p>[[[ifStudentMale?O aluno:::A aluna]]] [[[studentName]]] realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>Lembre-se de enviar sua assinatura quando necessário</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>',
        FALSE, TRUE, FALSE
    ),
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá [[[coordinatorName]]]</p>'
        '<br>'
        '<p>[[[ifStudentMale?O aluno:::A aluna]]] [[[studentName]]] realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>Lembre-se de enviar sua assinatura quando necessário</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        FALSE, FALSE, TRUE
    ),
    
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<br>'
        '<p>[[[ifAdvisorMale?Seu orientador:::Sua orientadora]]] [[[advisorName]]] realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>Lembre-se de enviar sua assinatura quando necessário</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá [[[coordinatorName]]]</p>'
        '<br>'
        '<p>[[[ifAdvisorMale?O orientador:::A orientadora]]] [[[advisorName]]] [[[ifStudentMale?do aluno:::da aluna]]] [[[studentName]]] realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>Lembre-se de enviar sua assinatura quando necessário</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        FALSE, FALSE, TRUE
    ),
    
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<br>'
        '<p>A coordenação de estágios realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>A próxima etapa é o envio e homologação dos documentos pelo SESTA com o período de espera máximo de 5 dias úteis</p>'
        '<p>Aguarde e caso necessário entre em contato com a coordenação de estágios ou diretamente com o SESTA</p>',
        TRUE, FALSE, FALSE
    ),
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]]</p>'
        '<br>'
        '<p>A coordenação de estágios realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>A próxima etapa é o envio e homologação dos documentos pelo SESTA com o período de espera máximo de 5 dias úteis</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>',
        FALSE, TRUE, FALSE
    ),
    
    (
		'Sistema de estágios - Coleta de assinaturas finalizada e documento homologado',
        '<p>A coordenação de estágios juntamente ao SESTA homologaram os documentos do [[[ifStudentMale?aluno:::aluna]]]: [[[studentName]]]</p>'
		'<p>Com isso o estágio é iniciado</p>'
        '<p>O aluno e orientador devem realizar relatórios parciais e/ou final com detalhamento do ocorrido no estágio</p>'
        '<p>Quando necessário acesse a plataforma para solicitar a avaliação e assinaturas dos relatórios parciais e final</p>'
        '<br>'
		'<p>Agradecemos pela utilização do sistema e um bom processo de estágio para o aluno</p>',
        TRUE, TRUE, FALSE
    ),
    (
		'Sistema de estágios - Coleta de assinaturas finalizada e documento homologado',
        '<p>Olá [[[coordinatorName]]]</p>'
		'<p>Os documentos do [[[ifStudentMale?aluno:::aluna]]]: [[[studentName]]] foram homologaram e a <b>solicitação foi concluída</b></p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<p>Modalidade: Estágio obrigatório com vinculo empregatício</p>'
        '<br>'
        '<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        FALSE, FALSE, TRUE
    );
    
# all solicitations
INSERT INTO solicitation (solicitation_name) VALUES 
	('Inicio de estágio obrigatório externo com vinculo empregatício'),
    ('Inicio de estágio obrigatório externo sem vinculo empregatício'),
    ('Inicio de estágio não obrigatório externo'),
    ('Inicio de estágio não obrigatório interno'),
    ('Envio de relatório parcial'),
    ('Envio de relatório final');
# mail sended when solicitation starts
INSERT INTO solicitation_start_mail(solicitation_id, dynamic_mail_id) VALUES 
	(1, 1);
# states for solicitation 1
INSERT INTO solicitation_state (solicitation_id, state_description, state_max_duration_days, state_dynamic_page_id, state_static_page_name, is_initial_state) VALUES
	(1, 'Solicitação de avaliação dos históricos e complementos pelo aluno', 4, 1, NULL, TRUE),
    (1, 'Avaliação dos históricos e complementos pelo coordenador', 4, NULL, 'interbegin-coordinatoracception', FALSE),
    (1, 'Escolha de orientador pelo aluno', 4, NULL, 'interbegin-advisorselection', FALSE),
    (1, 'Aceite de orientado pelo orientador', 4, NULL, 'interbegin-advisoracception', FALSE),
	(1, 'Processo de assinaturas para início de estágio', 15, NULL, 'interbegin-signatures', FALSE),
    (1, 'Estágio iniciado', NULL, 14, NULL, FALSE);
# editors for states in solicitation 1
INSERT INTO solicitation_state_profile_editors (solicitation_state_id, state_profile_editor) VALUES 
	(1, 4),
    (2, 2),
    (3, 4),
    (4, 3),
    (5, 2), (5, 3), (5, 4);
# transitions for states in solicitation 1
INSERT INTO solicitation_state_transition (solicitation_state_id_from, solicitation_state_id_to, transition_name) VALUES 
	(1, 2, 'STU: send docs'),				#1:s1:  dynamp: state 1 to 2
    (1, NULL, 'STU: cancel'),				#2:s1:  dynamp: state 1 to end
    (1, NULL, 'Expired'),				    #3:s1:  schedu: state 1 to end
    
    (2, 3, 'COO: defer'),					#4:s1:  manual: state 2 to 3
    (2, NULL, 'COO: reject docs'),			#5:s1:  manual: state 2 to end
    (2, NULL, 'COO: cancel'),				#6:s1:  manual: state 2 to end
    (2, NULL, 'Expired'),				    #7:s1:  schedu: state 1 to end

    (3, 4, 'STU: request ADV'),				#8:s1:  manual: state 3 to 4 end
    (3, NULL, 'STU: cancel'),				#9:s1:  manual: state 3 to end
    
    (4, 5, 'ADV: defer ADV'),				#10:s1: manual: state 4 to 5 end
    (4, NULL, 'ADV: reject ADV'),			#11:s1: manual: state 4 to end
    (4, NULL, 'ADV: cancel ADV'),			#12:s1: manual: state 4 to end
    
    (5, 5, 'STU: send docs loopback'),		#13:s1: manual: state 5 to 5
    (5, 5, 'ADV: send docs loopback'),		#14:s1: manual: state 5 to 5
    (5, 5, 'COO: send docs loopback'),		#15:s1: manual: state 5 to 5
    (5, 6, 'SESTA: send docs and defer'),	#16:s1: manual: state 5 to 6
    (5, 6, 'COO: defer'),					#17:s1: manual: state 5 to 6
    (5, NULL, 'COO: reject');				#18:s1: manual: state 5 to end
# email sended when transitions occurs for states in solicitation 1
INSERT INTO solicitation_state_transition_mail(solicitation_state_transition_id, dynamic_mail_id) VALUES
	(1, 2), (1, 3),
    (2, 4),
    (3, 5),
    (5, 6),
    (8, 7),
    (9, 8),
    (10, 9), (10, 10), (10, 11),
    (13, 12), (13, 13),
    (14, 14), (14, 15),
    (15, 16), (15, 17),
	(16, 18), (16, 19),
    (17, 18), (17, 19);
# static pages transitions for states in solicitation 1
INSERT INTO solicitation_state_transition_manual (solicitation_state_transition_id, transition_decision, transition_reason) VALUES
    (4, 'Deferido', 'A documentação do aluno está aprovada'), (5, 'Indeferido', 'A documentação do aluno está com algum problema'), (6, 'Cancelado pela coordenação', 'Foi cancelado a solicitação pela coordenação'),
    (8, 'Solicitado', 'O aluno solicitou a orientação ao orientador'), (9, 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
    (10, 'Deferido', 'O orientador aceitou a solicitação'), (11, 'Indeferido', 'O orientador não aceitou a solicitação'), (12, 'Cancelado pelo orientador', 'O orientador cancelou a solicitação'),
    (13, 'Enviado', 'Atualização de documentos pelo aluno'), (14, 'Enviado', 'Atualização de documentos pelo orientador'), (15, 'Enviado', 'Atualização de documentos pela coordenação'),
    (16, 'Deferido', 'Documentos homologados'), (17, 'Deferido', 'Documentos homologados'), (18, 'Indeferido', 'Processo de assinaturas indeferido pela coordenação');
# dynamic pages transitions for states in solicitation 1
INSERT INTO solicitation_state_transition_from_dynamic_page (solicitation_state_transition_id, dynamic_page_component, transition_decision, transition_reason) VALUES 
	(1, 'Button-Request', 'Solicitado', 'O aluno solicitou avaliação de documentos à coordenação de estágios'), (2, 'Button-Cancel', 'Cancelado pelo aluno', 'O aluno cancelou a solicitação');
# dynamic pages transitions for states in solicitation 1
INSERT INTO solicitation_state_transition_scheduled (solicitation_state_transition_id, transition_decision, transition_reason, transition_delay_seconds) VALUES 
	(3, 'Expirado', 'Foi alcançado o tempo limite de espera para a solicitação', 100),
    (7, 'Expirado', 'Foi alcançado o tempo limite de espera para a solicitação', 100);
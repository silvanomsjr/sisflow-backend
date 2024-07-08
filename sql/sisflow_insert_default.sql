USE sisflow;

/* Sistem configurations */
INSERT INTO config(config_name) VALUES
	("root path key files"),
    ("root path user files"),
    ("coordinator mail"),
    ("reason class: geral student hist validation"),
    ("reason class: bcc student hist validation"),
    ("reason class: bsi student hist validation");
# Path Configurations
INSERT INTO config_system_path(config_id, system_path) VALUES
	(1, "sisflowFiles/secrets/"),
	(2, "sisflowFiles/userfiles/");
# Email Configurations
INSERT INTO config_mail(config_id, mail, mail_name) VALUES
	(3, "coordenador@ufu.br", "Coordenador Curso");
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
	("admin@ufu.br", "admin@gmail.com","Admin", 'M', "34111111111","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("coordenador@ufu.br","coordenador@gmail.com", "Coordenador Curso", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
	("orientador@ufu.br", NULL, "Orientador Curso", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("gina@ufu.br", NULL, "Gina Maira Barbosa de Oliveira", 'F', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("luiz@ufu.br", NULL, "Luiz Gustavo Almeida Martins", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("maia@ufu.br", NULL, "Marcelo de Almeida Maia", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3", now()),
    ("stephane@ufu.br", NULL,"Stéphane Julia", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("adriano@ufu.br", NULL,"Adriano Mendonça Rocha", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("eliana@ufu.br", NULL,"Eliana Pantaleão", 'F', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("ivan@ufu.br", NULL,"Ivan da Silva Sendin", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("leandro@ufu.br", NULL,"Leandro Nogueira Couto", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("mauricio@ufu.br", NULL,"Mauricio Cunha Escarpinati", 'M', "34333333333","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
    ("aluno@ufu.br", "aluno@gmail.com","Aluno BCC", 'M', "34222222222","6507d069ff5e932b093715ab9a9fd415d5666b6f46b4c4943e695eaf72c9b759","GKA43F4CU71p2YF3",now()),
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
	(2, 'SIAPE-COOR');
INSERT INTO user_has_profile_advisor_data (user_has_profile_id, siape)  VALUES
	(3, 'SIAPE-COOR'),
	(4, 'SIAPE-ORIE'),
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
	(14, '11111BSI111', 'BCC'),
    (15, '11911BCC039', 'BCC');

/* Dynamic page */
INSERT INTO dynamic_page (title) VALUES 
	('Solicitação de inicio de estágio obrigatório com vínculo - Envio de históricos e comprovante de vínculo empregatício'),
    ('Solicitação de inicio de estágio obrigatório sem vínculo - Envio de históricos'),
    ('Solicitação de inicio de estágio não obrigatório - Envio de históricos'),
    ('Solicitação de inicio de estágio - Concluída'),
    ('Solicitação de inicio de estágio - Concluída');
INSERT INTO dynamic_component (type) VALUES 
	('inner_html'),('inner_html'),('inner_html'),
    ('upload'),('upload'),('upload'),('upload'),('upload'),
    ('select'),
    ('select_upload'),
    ('download'),('download'),('download'),('download'),('download'),('download'),
    ('button'),('button'),('button'),('button'),('button'),('button'),
    ('details'),('details');
INSERT INTO dynamic_component_inner_html (dynamic_component_id, dynamic_component_type, inner_html) VALUES 
	(
		1, 
        'inner_html', 
		'<p>Nesta etapa [[[ifStudentMale?o aluno:::a aluna]]] solicita uma avaliação de sua documentação ao coordenador de estágios para que este '
			'verifique se [[[ifStudentMale?o aluno:::a aluna]]] atende às normas gerais de estágio, as regras mudam de acordo com cada modalidade de estágio.</p>'
            '<p>Algumas normas para poder efetuar o estágio obrigatório no [[[ifBCCStudent? BCC ::: BSI ]]]:</p>'
            '[[[ifBCCStudent? 
				<ol><li><b>Duração</b>: 10 a 20 semanas</li><li><b>Carga horária mínima</b>: 210 horas com o máximo de 30 horas semanais</li><li><b>Aprovação</b>: 1 ao 4 períodos completos</li></ol>
            ::: 
				<ol><li><b>Duração</b>: 16 a 32 semanas</li><li><b>Carga horária mínima</b>: 440 horas com o máximo de 30 horas semanais</li><li><b>Aprovação</b>: 1 ao 4 períodos completos</li></ol>
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
            '<ol><li><b>Duração</b>: 8 a 24 semanas</li><li><b>Carga horária mínima</b>: 220 horas</li><li><b>Aprovação</b>: 1 e 2 períodos completos</li></ol>'
			'<p>Com carga horária de disciplinas acima de 1200 é possível estagiar de 30 horas semanais e, caso contrário, 20 horas</p>'
			'<p>As normas do seu curso podem ser visualizadas no link: '
			'[[[ifBCCStudent?<a href="https://facom.ufu.br/graduacao/bcc/estagio-supervisionado">Normas de Estagio BCC</a>.</p>:::'
            '<a href="https://facom.ufu.br/legislacoes/normas-de-estagio-curricular-do-bacharelado-em-sistemas-de-informacao">Normas de Estagio BSI</a>.</p>]]]'
			'<p>Para prosseguir anexe os documentos solicitados:</p>'
	),(
		3,
		'inner_html',
        '<p>Com todas as assinaturas a solicitação está concluída você já pode iniciar o estágio em sua data de início</p>'
			'<p>Realize o download abaixo da documentação assinada</p>'
	);
INSERT INTO dynamic_component_upload (dynamic_component_id, dynamic_component_type, upload_label, upload_name, upload_required, upload_missing_message) VALUES
	(4, 'upload', 'Envie seu histórico textual', 'HistTextual', TRUE, 'O envio do histórico textual é obrigatório!'),
    (5, 'upload', 'Envie seu histórico visual', 'HistVisual', TRUE, 'O envio do histórico visual é obrigatório!'),
    (6, 'upload', 'Envie seu TCE com PA assinado', 'TCEPA', TRUE, 'O envio do TCE com PA é obrigatório!'),
    (7, 'upload', 'Envie seu TCE assinado', 'TCE', TRUE, 'O envio do TCE é obrigatório!'),
    (8, 'upload', 'Envie seu PA assinado', 'PA', TRUE, 'O envio do PA é obrigatório!');
INSERT INTO dynamic_component_select (dynamic_component_id, dynamic_component_type, select_name, select_label, select_initial_text, is_select_required, select_missing_message) VALUES 
	(9, 'select', 'Vinculo', 'Escolha o tipo de vínculo', DEFAULT, TRUE, 'O envio do vínculo empregatício é obrigatório');
INSERT INTO dynamic_component_select_option (dynamic_component_select_id, select_option_label, select_option_value) VALUES 
	(9, DEFAULT, NULL),
    (9, 'Carteira Digital de Trabalho', 'CTPS'),
    (9, 'Contrato de pessoa jurídica', 'PJ'),
    (9, 'Declaração do Empregador', 'Declaracao'),
    (9, 'Outros', 'Outros');
INSERT INTO dynamic_component_select_upload (dynamic_component_id, dynamic_component_type, dynamic_component_select_name) VALUES 
	(10, 'select_upload', 'Vinculo');
INSERT INTO dynamic_component_download (dynamic_component_id, dynamic_component_type, download_label, download_from, internal_upload_name, internal_select_upload_name, external_download_link) VALUES
	(11, 'download', 'Faça o download do histórico textual', 'internal_from_upload', 'HistTextual', NULL, NULL),
	(12, 'download', 'Faça o download do histórico visual', 'internal_from_upload', 'HistVisual', NULL, NULL),
    (13, 'download', 'Faça o download do comprovante de vínculo empregatício', 'internal_from_select_upload', NULL, 'Vinculo', NULL),
    
    (14, 'download', 'Faça o download do TCE com PA assinado', 'internal_from_upload', 'TCEPA', NULL, NULL),
    (15, 'download', 'Faça o download do TCE assinado', 'internal_from_upload', 'TCE', NULL, NULL),
    (16, 'download', 'Faça o download do PA assinado', 'internal_from_upload', 'PA', NULL, NULL);
INSERT INTO dynamic_component_button (dynamic_component_id, dynamic_component_type, button_label, button_color, button_transation_type) VALUES 
	(17, 'button', 'Cancelar', 'black', 'Cancel'),
    (18, 'button', 'Solicitar', 'darkblue', 'Request'),
    (19, 'button', 'Enviar', 'darkblue', 'Send'),
    (20, 'button', 'Enviar e deferir', 'darkblue', 'Send and Defer'),
    (21, 'button', 'Deferir', 'darkblue', 'Defer'),
    (22, 'button', 'Indeferir', 'red', 'Reject');
INSERT INTO dynamic_component_details (dynamic_component_id, dynamic_component_type, details_type) VALUES
	(23, 'details', 'student'),
    (24, 'details', 'advisor');
INSERT INTO dynamic_page_has_component (dynamic_page_id, dynamic_component_id, dynamic_component_order) VALUES 
	(1,1,1), (1,4,2), (1,5,3), (1,10,4), (1,17,5), (1,18,6),
    (2,1,1), (2,4,2), (2,5,3), (2,17,4), (2,18,5),
    (3,2,1), (3,4,2), (3,5,3), (3,17,4), (3,18,5),
    (4,3,1), (4,14,2),
    (5,3,1), (5,15,2), (5,16,3);
    
/* dynamic mails */
INSERT INTO dynamic_mail (mail_subject, mail_body_html, is_sent_to_student, is_sent_to_advisor, is_sent_to_coordinator) VALUES
	# 0
	(
		'Sistema de estágios: Inicio de processo de estágio',
        '<p>Olá [[[coordinatorName]]] e [[[studentName]]]</p>'
		'<p>O aluno <b>criou uma solicitação</b> de início de estágio</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    
    # 1
    (
		'Sistema de estágios: Solicitação de avaliação dos históricos',
        '<p>Olá [[[coordinatorName]]] e [[[studentName]]]</p>'
		'<p>O aluno criou uma <b>solicitação de avaliação de históricos</b></p>'
        '<p>A coordenação de estágios possui até 4 dias úteis para realizar a avaliação retornando se a solicitação foi deferida ou indeferida</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    (
		'Sistema de estágios: Cancelamento de inicio de processo de estágio',
        '<p>Olá [[[coordinatorName]]] e [[[studentName]]]</p>'
		'<p>O aluno cancelou a solicitação de estágio antes de solicitar a avaliação de históricos</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    (
		'Sistema de estágios: Sua solicitação de início de estágio expirou',
        '<p>Olá [[[coordinatorName]]] e [[[studentName]]]</p>'
		'<p>Passaram se 14 dias após a solicitação de inicío de processo de estágio e não foi enviado a documentação para avaliação de históricos pelo aluno</p>'
        '<p>Por isso a solicitação foi cancelada.</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    
    # 2
    (
		'Sistema de estágios - Solicitação de avaliação dos históricos deferida',
        '<p>Olá [[[coordinatorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>A documentação enviada para a solicitação de início de estágio foi <b>deferida</b></p>'
        '<br>'
		'<p>O próximo passo é a escolha de um orientador para o estágio na plataforma</p>'
        '<p>O orientador deve concordar em ser o orientador previamente bem como participar dos processos de assinaturas para a homologação dos documentos</p>'
        '<p>Mantenham o orientador atualizado com as solicitações e procedimentos realizados na plataforma</p>',
        TRUE, FALSE, TRUE
    ),
    (
		'Sistema de estágios: A solicitação de início de estágio expirou',
        '<p>Olá [[[coordinatorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[studentName]]]</p>'
		'<p>Passaram se 14 dias após a sua solicitação de avaliação de documentos e a coordenação realizou a avaliação</p>'
        '<p>Por isso sua solicitação foi cancelada. Realize a solicitação novamente</p>'
        '<br>'
        '<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    
    # 3
    (
		'Sistema de estágios - Solicitação de orientação',
        '<p>Olá [[[coordinatorName]]], [[[studentName]]] e [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]]</p>'
		'<p>[[[ifStudentMale?O aluno:::A aluna]]] [[[studentName]]] solicitou a orientação para [[[ifAdvisorMale?o orientador:::a orientadora]]] [[[advisorName]]]</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
        '<p>[[ifAdvisorMale?O orientador:::A orientadora]]] deve acessar a plataforma para aceitar ou recusar a solicitação</p>'
        '<p>Lembre-se de participar do processo de assinaturas no caso do aceite para a homologação dos documentos</p>',
        TRUE, TRUE, TRUE
    ),
    (
		'Sistema de estágios: Cancelamento de inicio de processo de estágio',
        '<p>Olá [[[coordinatorName]]] e [[[studentName]]]</p>'
		'<p>O aluno cancelou a solicitação de estágio antes de solicitar a orientação ao orientador</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    (
		'Sistema de estágios: Foi expirado a solicitação de orientação para início de estágio',
        '<p>Olá [[[coordinatorName]]] e [[[studentName]]]</p>'
		'<p>Passaram se 14 dias após a aprovação da documentação do aluno e o mesmo não solicitou um orientador</p>'
        '<p>Seguem abaixo os dados do aluno</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    
    # 4
    (
		'Sistema de estágios - Solicitação de orientação aceita e início de coleta de assinaturas',
        '<p>Olá coordenador [[[coordinatorName]]], [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>[[[ifAdvisorMale?O orientador:::A orientadora]]] [[[advisorName]]] aceitou a solicitação</p>'
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
        TRUE, TRUE, TRUE
    ),
    (
		'Sistema de estágios - Solicitação de orientação rejeitada',
        '<p>Olá coordenador [[[coordinatorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>[[[ifAdvisorMale?O orientador:::A orientadora]]] [[[advisorName]]] rejeitou a solicitação [[[ifStudentMale?do aluno:::da aluna]]] [[[studentName]]] </p>'
        '<p>Seguem abaixo os dados do aluno</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>',
        TRUE, FALSE, TRUE
    ),
    (
		'Sistema de estágios: Foi expirado a solicitação de orientação para o inicio de estágio',
        '<p>Olá coordenador [[[coordinatorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
		'<p>Passaram se 14 dias após o aluno solicitar orientação [[[ifAdvisorMale?ao orientador:::a orientadora]]] [[[advisorName]]] e por isso foi expirado</p>'
        '<p>Seguem abaixo os dados do aluno e orientador</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        TRUE, FALSE, TRUE
    ),
    
    # 5
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá coordenador [[[coordinatorName]]], [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<br>'
        '<p>[[[ifStudentMale?O aluno:::A aluna]]] [[[studentName]]] realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>Lembre-se de enviar sua assinatura quando necessário</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        TRUE, TRUE, TRUE
    ),
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá coordenador [[[coordinatorName]]], [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<br>'
        '<p>[[[ifAdvisorMale?O orientador:::A orientadora]]] [[[advisorName]]] [[[ifStudentMale?do aluno:::da aluna]]] [[[studentName]]] realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>Lembre-se de enviar sua assinatura quando necessário</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        TRUE, TRUE, TRUE
    ),
    (
		'Sistema de estágios - Atualização de assinaturas',
        '<p>Olá coordenador [[[coordinatorName]]], [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<br>'
        '<p>A coordenação de estágios realizou o envio dos documentos de assinaturas na plataforma de estágios</p>'
		'<p>A próxima etapa é o envio e homologação dos documentos pelo SESTA com o período de espera máximo de 5 dias úteis</p>'
        '<p>Aguarde e caso necessário entre em contato com a coordenação de estágios ou diretamente com o SESTA</p>'
		'<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        TRUE, TRUE, TRUE
    ),
    (
		'Sistema de estágios - Coleta de assinaturas finalizada e documento homologado',
        '<p>Olá coordenador [[[coordinatorName]]], [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<p>A coordenação de estágios juntamente ao SESTA homologaram os documentos do [[[ifStudentMale?aluno:::aluna]]]: [[[studentName]]]</p>'
		'<p>Com isso o estágio é iniciado</p>'
        '<p>O aluno e orientador devem realizar relatórios parciais e/ou final com detalhamento do ocorrido no estágio</p>'
        '<p>Quando necessário acesse a plataforma para solicitar a avaliação e assinaturas dos relatórios parciais e final</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>'
        '<br>'
		'<p>Agradecemos pela utilização do sistema e um bom processo de estágio para o aluno</p>',
        TRUE, TRUE, TRUE
    ),
    (
		'Sistema de estágios - Coleta de assinaturas finalizada e documento homologado',
        '<p>Olá coordenador [[[coordinatorName]]], [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<p>A coordenação de estágios homologou os documentos do [[[ifStudentMale?aluno:::aluna]]]: [[[studentName]]]</p>'
		'<p>Com isso o estágio é iniciado</p>'
        '<p>O aluno e orientador devem realizar relatórios parciais e/ou final com detalhamento do ocorrido no estágio</p>'
        '<p>Quando necessário acesse a plataforma para solicitar a avaliação e assinaturas dos relatórios parciais e final</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>'
        '<br>'
		'<p>Agradecemos pela utilização do sistema e um bom processo de estágio para o aluno</p>',
        TRUE, TRUE, TRUE
    ),(
		'Sistema de estágios - Coleta de assinaturas indeferida',
        '<p>Olá coordenador [[[coordinatorName]]], [[[ifAdvisorMale?orientador:::orientadora]]] [[[advisorName]]] e [[[ifStudentMale?aluno:::aluna]]] [[[ifBCCStudent?do BCC:::do BSI]]] [[[studentName]]]</p>'
        '<p>A coordenação de estágios indeferiu os documentos do [[[ifStudentMale?aluno:::aluna]]]: [[[studentName]]]</p>'
        '<p>Entre em contato com a coordenação para mais informações</p>'
        '<br>'
		'<p>[[[ifStudentMale?Aluno:::Aluna]]]: [[[studentName]]]</p>'
        '<p>Curso: [[[studentCourse]]]</p>'
        '<p>Matricula: [[[studentMatricula]]]</p>'
        '<br>'
		'<p>[[[ifAdvisorMale?Orientador:::Orientadora]]]: [[[advisorName]]]</p>'
        '<p>Siape: [[[advisorSiape]]]</p>',
        TRUE, TRUE, TRUE
    );
    
# all solicitations
INSERT INTO solicitation (solicitation_name) VALUES 
	('Inicio de estágio obrigatório com vinculo empregatício'),
    ('Inicio de estágio obrigatório sem vinculo empregatício'),
    ('Inicio de estágio não obrigatório');
# mail sended when solicitation starts
INSERT INTO solicitation_start_mail(solicitation_id, dynamic_mail_id) VALUES 
	(1, 1),
    (2, 1),
    (3, 1);
INSERT INTO solicitation_state (solicitation_id, state_description, state_max_duration_days, state_dynamic_page_id, state_static_page_name, is_initial_state) VALUES
	# states for solicitation 1
    (1, 'Solicitação de avaliação dos históricos e complementos pelo aluno', 4, 1, NULL, TRUE),
    (1, 'Avaliação dos históricos e complementos pelo coordenador', 4, NULL, 'interbegin-coordinatoracception', FALSE),
    (1, 'Escolha de orientador pelo aluno', 4, NULL, 'interbegin-advisorselection', FALSE),
    (1, 'Aceite de orientado pelo orientador', 4, NULL, 'interbegin-advisoracception', FALSE),
	(1, 'Processo de assinaturas para início de estágio', 15, NULL, 'interbegin-signatures', FALSE),
    (1, 'Estágio iniciado', NULL, 4, NULL, FALSE),
    (1, 'Estágio iniciado', NULL, 5, NULL, FALSE),
    
    # states for solicitation 2
    (2, 'Solicitação de avaliação dos históricos e complementos pelo aluno', 4, 2, NULL, TRUE),
    (2, 'Avaliação dos históricos e complementos pelo coordenador', 4, NULL, 'interbegin-coordinatoracception', FALSE),
    (2, 'Escolha de orientador pelo aluno', 4, NULL, 'interbegin-advisorselection', FALSE),
    (2, 'Aceite de orientado pelo orientador', 4, NULL, 'interbegin-advisoracception', FALSE),
	(2, 'Processo de assinaturas para início de estágio', 15, NULL, 'interbegin-signatures', FALSE),
    (2, 'Estágio iniciado', NULL, 4, NULL, FALSE),
    (2, 'Estágio iniciado', NULL, 5, NULL, FALSE),
    
    # states for solicitation 3
    (3, 'Solicitação de avaliação dos históricos e complementos pelo aluno', 4, 3, NULL, TRUE),
    (3, 'Avaliação dos históricos e complementos pelo coordenador', 4, NULL, 'interbegin-coordinatoracception', FALSE),
    (3, 'Escolha de orientador pelo aluno', 4, NULL, 'interbegin-advisorselection', FALSE),
    (3, 'Aceite de orientado pelo orientador', 4, NULL, 'interbegin-advisoracception', FALSE),
	(3, 'Processo de assinaturas para início de estágio', 15, NULL, 'interbegin-signatures', FALSE),
    (3, 'Estágio iniciado', NULL, 4, NULL, FALSE),
    (3, 'Estágio iniciado', NULL, 5, NULL, FALSE);
    
INSERT INTO solicitation_state_profile_editors (solicitation_state_id, state_profile_editor) VALUES 
	# editors for states in solicitation 1
	(1, 4),
    (2, 2),
    (3, 4),
    (4, 3),
    (5, 2), (5, 3), (5, 4),
    
    # editors for states in solicitation 2
    (8, 4),
    (9, 2),
    (10, 4),
    (11, 3),
    (12, 2), (12, 3), (12, 4),
    
    # editors for states in solicitation 3
    (15, 4),
    (16, 2),
    (17, 4),
    (18, 3),
    (19, 2), (19, 3), (19, 4);
    
INSERT INTO solicitation_state_transition (solicitation_state_id_from, solicitation_state_id_to, transition_name) VALUES 
	# transitions for states in solicitation 1
	(1, 2, 'STU: send docs'),							#1:s1:  dynamp: state 1 to 2
    (1, NULL, 'STU: cancel'),							#2:s1:  dynamp: state 1 to end
    (1, NULL, 'Expired'),				    			#3:s1:  schedu: state 1 to end
    
    (2, 3, 'COO: defer'),								#4:s1:  manual: state 2 to 3
    (2, NULL, 'COO: reject docs'),						#5:s1:  manual: state 2 to end
    (2, NULL, 'Expired'),				   	 			#6:s1:  schedu: state 2 to end

    (3, 4, 'STU: request ADV'),							#7:s1:  manual: state 3 to 4
    (3, NULL, 'STU: cancel'),							#8:s1:  manual: state 3 to end
    (3, NULL, 'Expired'),				    			#9:s1:  schedu: state 3 to end
    
    (4, 5, 'ADV: defer ADV'),							#10:s1: manual: state 4 to 5
    (4, NULL, 'ADV: reject ADV'),						#11:s1: manual: state 4 to end
    (4, NULL, 'Expired'),				    			#12:s1: schedu: state 4 to end
    
    (5, 5, 'STU: send docs loopback'),					#13:s1: manual: state 5 to 5
    (5, 5, 'ADV: send docs loopback'),					#14:s1: manual: state 5 to 5
    (5, 5, 'COO: send docs loopback'),					#15:s1: manual: state 5 to 5
    (5, 6, 'SESTA: send docs and defer TCE com PA'),	#16:s1: manual: state 5 to 6
    (5, 6, 'COO: defer TCE com PA'),					#17:s1: manual: state 5 to 6
    (5, 7, 'SESTA: send docs and defer TCE e PA'),		#18:s1: manual: state 5 to 7
    (5, 7, 'COO: defer TCE e PA'),						#19:s1: manual: state 5 to 7
    (5, NULL, 'COO: reject'),							#20:s1: manual: state 5 to end
    
    # transitions for states in solicitation 2
    (8, 9, 'STU: send docs'),							#21:s2:  dynamp: state 8 to 9
    (8, NULL, 'STU: cancel'),							#22:s2:  dynamp: state 8 to end
    (8, NULL, 'Expired'),				    			#23:s2:  schedu: state 8 to end
    
    (9, 10, 'COO: defer'),								#24:s2:  manual: state 9 to 10
    (9, NULL, 'COO: reject docs'),						#25:s2:  manual: state 9 to end
    (9, NULL, 'Expired'),				   	 			#26:s2:  schedu: state 9 to end

    (10, 11, 'STU: request ADV'),						#27:s2:  manual: state 10 to 11
    (10, NULL, 'STU: cancel'),							#28:s2:  manual: state 10 to end
    (10, NULL, 'Expired'),				    			#29:s2:  schedu: state 10 to end
    
    (11, 12, 'ADV: defer ADV'),							#30:s2: manual: state 11 to 12
    (11, NULL, 'ADV: reject ADV'),						#31:s2: manual: state 11 to end
    (11, NULL, 'Expired'),				    			#32:s2: schedu: state 11 to end
    
    (12, 12, 'STU: send docs loopback'),				#33:s2: manual: state 12 to 12
    (12, 12, 'ADV: send docs loopback'),				#34:s2: manual: state 12 to 12
    (12, 12, 'COO: send docs loopback'),				#35:s2: manual: state 12 to 12
    (12, 13, 'SESTA: send docs and defer TCE com PA'),	#36:s2: manual: state 12 to 13
    (12, 13, 'COO: defer TCE com PA'),					#37:s2: manual: state 12 to 13
    (12, 14, 'SESTA: send docs and defer TCE e PA'),	#38:s2: manual: state 12 to 14
    (12, 14, 'COO: defer TCE e PA'),					#39:s2: manual: state 12 to 14
    (12, NULL, 'COO: reject'),							#40:s2: manual: state 12 to end
    
    # transitions for states in solicitation 3
    (15, 16, 'STU: send docs'),							#41:s3:  dynamp: state 15 to 16
    (15, NULL, 'STU: cancel'),							#42:s3:  dynamp: state 15 to end
    (15, NULL, 'Expired'),				    			#43:s3:  schedu: state 15 to end
    
    (16, 17, 'COO: defer'),								#44:s3:  manual: state 16 to 17
    (16, NULL, 'COO: reject docs'),						#45:s3:  manual: state 16 to end
    (16, NULL, 'Expired'),				   	 			#46:s3:  schedu: state 16 to end

    (17, 18, 'STU: request ADV'),						#47:s3:  manual: state 17 to 18
    (17, NULL, 'STU: cancel'),							#48:s3:  manual: state 17 to end
    (17, NULL, 'Expired'),				    			#49:s3:  schedu: state 17 to end
    
    (18, 19, 'ADV: defer ADV'),							#50:s3: manual: state 18 to 19
    (18, NULL, 'ADV: reject ADV'),						#51:s3: manual: state 18 to end
    (18, NULL, 'Expired'),				    			#52:s3: schedu: state 18 to end
    
    (19, 19, 'STU: send docs loopback'),				#53:s3: manual: state 19 to 19
    (19, 19, 'ADV: send docs loopback'),				#54:s3: manual: state 19 to 19
    (19, 19, 'COO: send docs loopback'),				#55:s3: manual: state 19 to 19
    (19, 20, 'SESTA: send docs and defer TCE com PA'),	#56:s3: manual: state 19 to 20
    (19, 20, 'COO: defer TCE com PA'),					#57:s3: manual: state 19 to 20
    (19, 21, 'SESTA: send docs and defer TCE e PA'),	#58:s3: manual: state 19 to 21
    (19, 21, 'COO: defer TCE e PA'),					#59:s3: manual: state 19 to 21
    (19, NULL, 'COO: reject');							#60:s3: manual: state 19 to end
    
INSERT INTO solicitation_state_transition_mail(solicitation_state_transition_id, dynamic_mail_id) VALUES
	# email sended when transitions occurs for states in solicitation 1
	(1, 2), (2, 3), (3, 4),
    (4, 5), (6, 6),
    (7, 7), (8, 8), (9, 9),
    (10, 10), (11, 11), (12, 12),
    (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 16), (19, 17), (20, 18),
    
    # email sended when transitions occurs for states in solicitation 2
	(21, 2), (22, 3), (23, 4),
    (24, 5), (26, 6),
    (27, 7), (28, 8), (29, 9),
    (30, 10), (31, 11), (32, 12),
    (33, 13), (34, 14), (35, 15), (36, 16), (37, 17), (38, 16), (39, 17), (40, 18),
    
    # email sended when transitions occurs for states in solicitation 3
	(41, 2), (42, 3), (43, 4),
    (44, 5), (46, 6),
    (47, 7), (48, 8), (49, 9),
    (50, 10), (51, 11), (52, 12),
    (53, 13), (54, 14), (55, 15), (56, 16), (57, 17), (58, 16), (59, 17), (60, 18);

INSERT INTO solicitation_state_transition_from_dynamic_page (solicitation_state_transition_id, dynamic_page_component, transition_decision, transition_reason) VALUES 
	# dynamic pages transitions for states in solicitation 1
    (1, 'Button-Request', 'Solicitado', 'O aluno solicitou avaliação de documentos à coordenação de estágios'), (2, 'Button-Cancel', 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
	# dynamic pages transitions for states in solicitation 2
    (21, 'Button-Request', 'Solicitado', 'O aluno solicitou avaliação de documentos à coordenação de estágios'), (22, 'Button-Cancel', 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
	# dynamic pages transitions for states in solicitation 3
    (41, 'Button-Request', 'Solicitado', 'O aluno solicitou avaliação de documentos à coordenação de estágios'), (42, 'Button-Cancel', 'Cancelado pelo aluno', 'O aluno cancelou a solicitação');
	
INSERT INTO solicitation_state_transition_scheduled (solicitation_state_transition_id, transition_decision, transition_reason, transition_delay_seconds) VALUES 
	# dynamic pages transitions for states in solicitation 1
    (3, 'Expirado', 'O aluno não enviou a documentação necessária no intervalo de 14 dias', 1209600),
    (6, 'Expirado', 'A coordenação de estágios não conferiu a documentação no intervalo de 4 dias', 345600),
    (9, 'Expirado', 'O aluno não enviou solicitou orientação no intervalo de 14 dias para o professor orientador', 1209600),	
    (12, 'Expirado', 'O orientador não aceitou a solicitação do discente no período de 14 dias', 1209600),
    # dynamic pages transitions for states in solicitation 2
    (23, 'Expirado', 'O aluno não enviou a documentação necessária no intervalo de 14 dias', 1209600),
    (26, 'Expirado', 'A coordenação de estágios não conferiu a documentação no intervalo de 4 dias', 345600),
    (29, 'Expirado', 'O aluno não enviou solicitou orientação no intervalo de 14 dias para o professor orientador', 1209600),	
    (32, 'Expirado', 'O orientador não aceitou a solicitação do discente no período de 14 dias', 1209600),
    # dynamic pages transitions for states in solicitation 3
    (43, 'Expirado', 'O aluno não enviou a documentação necessária no intervalo de 14 dias', 1209600),
    (46, 'Expirado', 'A coordenação de estágios não conferiu a documentação no intervalo de 4 dias', 345600),
    (49, 'Expirado', 'O aluno não enviou solicitou orientação no intervalo de 14 dias para o professor orientador', 1209600),	
    (52, 'Expirado', 'O orientador não aceitou a solicitação do discente no período de 14 dias', 1209600);

INSERT INTO solicitation_state_transition_manual (solicitation_state_transition_id, transition_decision, transition_reason) VALUES
	# static pages transitions for states in solicitation 1
    (4, 'Deferido', 'A documentação do aluno está aprovada'), (5, 'Indeferido', 'A documentação do aluno está com algum problema'),
    (7, 'Solicitado', 'O aluno solicitou a orientação ao orientador'), (8, 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
    (10, 'Deferido', 'O orientador aceitou a solicitação'), (11, 'Indeferido', 'O orientador não aceitou a solicitação'),
    (13, 'Enviado', 'Atualização de documentos pelo aluno'),
    (14, 'Enviado', 'Atualização de documentos pelo orientador'),
    (15, 'Enviado', 'Atualização de documentos pela coordenação'),
    (16, 'Deferido', 'Documentos homologados'),
    (17, 'Deferido', 'Documentos homologados'),
    (18, 'Deferido', 'Documentos homologados'),
    (19, 'Deferido', 'Documentos homologados'),
    (20, 'Indeferido', 'Processo de assinaturas indeferido pela coordenação'),
    # static pages transitions for states in solicitation 2
    (24, 'Deferido', 'A documentação do aluno está aprovada'), (25, 'Indeferido', 'A documentação do aluno está com algum problema'),
    (27, 'Solicitado', 'O aluno solicitou a orientação ao orientador'), (28, 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
    (30, 'Deferido', 'O orientador aceitou a solicitação'), (31, 'Indeferido', 'O orientador não aceitou a solicitação'),
    (33, 'Enviado', 'Atualização de documentos pelo aluno'),
    (34, 'Enviado', 'Atualização de documentos pelo orientador'),
    (35, 'Enviado', 'Atualização de documentos pela coordenação'),
    (36, 'Deferido', 'Documentos homologados'),
    (37, 'Deferido', 'Documentos homologados'),
    (38, 'Deferido', 'Documentos homologados'),
    (39, 'Deferido', 'Documentos homologados'),
    (40, 'Indeferido', 'Processo de assinaturas indeferido pela coordenação'),
    # static pages transitions for states in solicitation 3
    (44, 'Deferido', 'A documentação do aluno está aprovada'), (45, 'Indeferido', 'A documentação do aluno está com algum problema'),
    (47, 'Solicitado', 'O aluno solicitou a orientação ao orientador'), (48, 'Cancelado pelo aluno', 'O aluno cancelou a solicitação'),
    (50, 'Deferido', 'O orientador aceitou a solicitação'), (51, 'Indeferido', 'O orientador não aceitou a solicitação'),
    (53, 'Enviado', 'Atualização de documentos pelo aluno'),
    (54, 'Enviado', 'Atualização de documentos pelo orientador'),
    (55, 'Enviado', 'Atualização de documentos pela coordenação'),
    (56, 'Deferido', 'Documentos homologados'),
    (57, 'Deferido', 'Documentos homologados'),
    (58, 'Deferido', 'Documentos homologados'),
    (59, 'Deferido', 'Documentos homologados'),
    (60, 'Indeferido', 'Processo de assinaturas indeferido pela coordenação');
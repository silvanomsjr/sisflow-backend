CREATE TABLE config(
	id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(20),
  PRIMARY KEY (id)
);

CREATE TABLE config_path(
	config_id INT NOT NULL,
	path_str VARCHAR(256),
  PRIMARY KEY (config_id),
  FOREIGN KEY (config_id) REFERENCES config(id)
);

INSERT INTO config(nome) VALUES
	("root path key files"),
  ("root path user files");
    
INSERT INTO config_path(config_id, path_str) VALUES
	(1, "/sisges/secrets/"),
	(2, "/sisges/userfiles/");

CREATE TABLE conta_usuario(
	id INT NOT NULL AUTO_INCREMENT,
  email_ins VARCHAR(256) NOT NULL UNIQUE,
  email_sec VARCHAR(256),
  nome VARCHAR(100) NOT NULL,
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
  nome VARCHAR(20),
  tipo VARCHAR(20),
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
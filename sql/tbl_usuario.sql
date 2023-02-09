CREATE TABLE tbl_usuario (
	id_usuario VARCHAR(15) NOT NULL,
  hash_senha CHAR(65) NOT NULL,
	PRIMARY KEY (id_usuario),
  FOREIGN KEY (id_usuario) REFERENCES tbl_pessoa(id_pessoa)
);
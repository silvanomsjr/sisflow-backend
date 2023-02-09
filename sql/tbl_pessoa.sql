CREATE TABLE tbl_pessoa (
	id_pessoa VARCHAR(15) NOT NULL,
  email_ins VARCHAR(50) UNIQUE NOT NULL,
  email_sec VARCHAR(50),
	tipo ENUM ('A', 'P') NOT NULL,
	nome VARCHAR(50),
  telefone VARCHAR(15),
  PRIMARY KEY (id_pessoa)
);
CREATE TABLE tbl_chave_cadastro(
	email_ins VARCHAR(50) NOT NULL,
  chave_cadastro CHAR(9) NOT NULL,
  PRIMARY KEY (email_ins),
  FOREIGN KEY (email_ins) REFERENCES tbl_pessoa(email_ins)
);
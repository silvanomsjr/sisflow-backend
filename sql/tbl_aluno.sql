CREATE TABLE tbl_aluno (
	matricula VARCHAR(15) NOT NULL,
  PRIMARY KEY (matricula),
  FOREIGN KEY (matricula) REFERENCES tbl_pessoa(id_pessoa)
);
CREATE TABLE tbl_professor (
	siape VARCHAR(15) NOT NULL,
  PRIMARY KEY (siape),
  FOREIGN KEY (siape) REFERENCES tbl_pessoa(id_pessoa)
);
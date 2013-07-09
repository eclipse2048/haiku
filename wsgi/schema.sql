CREATE TABLE haiku (
	id INT AUTO_INCREMENT,
	content TEXT,
	seedword TEXT,
	genes TEXT,
	generation INT,
	algorithm TEXT,
	author TEXT,
	comment TEXT,
	posted_on DATETIME;
	primary key (id)
);

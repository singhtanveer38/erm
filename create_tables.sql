create table marks(
	roll_no int,
	name varchar(128),
	class int,
	section char,
	exam_name varchar(16),
	exam_marks int,
	subject varchar(16),
	marks_obtained float
);

create table overall_result(
	roll_no int,
	name varchar(128),
	class int,
	section char,
	exam_name varchar(16),
	exam_total int,
	percentage float,
	category varchar(16)
);

create table subject_result(
	roll_no int,
	name varchar(128),
	class int,
	section char,
	exam_name varchar(16),
	exam_marks int,
	marks_obtained float,
	percentage float,
	category varchar(16)
);

create table loaded_files(
	timestamp timestamp,
	filename varchar(120)
);

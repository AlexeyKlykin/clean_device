CREATE table IF NOT EXISTS device_company(
  company_id integer primary key AUTOINCREMENT,
  company_name text not null unique,
  producer_country text not null unique,
  description_company text
);
CREATE table IF NOT EXISTS device_type(
  type_device_id integer primary key AUTOINCREMENT,
  type_title text not null unique,
  description_type text
);
CREATE table IF NOT EXISTS device(
  device_id integer primary key AUTOINCREMENT,
  device_name text not null unique,
  company_id integer,
  type_device_id integer,
  foreign key(company_id) references device_company(company_id),
  foreign key(type_device_id) references device_type(type_device_id)
);
CREATE table IF NOT EXISTS stock_devices(
  stock_device_id integer primary key,
  at_clean_date text not null,
  device_id integer,    
  foreign key(device_id) references device(device_id)
);


INSERT INTO device_company(company_name, producer_country, description_company)
VALUES ('Clay Paky', 'Itali', 'https://www.claypaky.it/');

INSERT INTO device_type(type_title, description_type)
VALUES ('Beam', 'вращающиеся головы, которые имеют узконаправленный источник света. Угол раскрытия луча у приборов данного вида колеблется от 2 до 10 градусов.');

SELECT company_id from device_company;

INSERT INTO device(device_name, company_id, type_device_id)
VALUES ('k20', 1, 1);

SELECT d.device_name, dc.company_name, dt.type_title from device d
left join device_company dc on dc.company_id = d.company_id
left join device_type dt on dt.type_device_id = d.type_device_id;

/* удалаяет дубликаты */
delete from stock_device where id not in (
	select min(sd.id) from stock_device sd
	left join device d on d.device_id = sd.device_id 
	group by sd.stock_device_id, d.device_id
);

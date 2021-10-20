PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE broker (id INTEGER PRIMARY KEY, name text, "fullName" TEXT);
CREATE TABLE IF NOT EXISTS "instrument_type"  (id INTEGER PRIMARY KEY, type text);
INSERT INTO instrument_type (type) VALUES('ETF');
INSERT INTO instrument_type (type) VALUES('Stock');
INSERT INTO instrument_type (type) VALUES('Funds');
INSERT INTO instrument_type (type) VALUES('Bond');
INSERT INTO instrument_type (type) VALUES('Crypto');
CREATE TABLE IF NOT EXISTS "asset"  (id INTEGER PRIMARY KEY, type text);
INSERT INTO asset (type) VALUES('Stock');
INSERT INTO asset (type) VALUES('Government Bond');
INSERT INTO asset (type) VALUES('Corp Bond');
INSERT INTO asset (type) VALUES('REIT');
INSERT INTO asset (type) VALUES('Gold');
INSERT INTO asset (type) VALUES('Cash');
INSERT INTO asset (type) VALUES('Other');
CREATE TABLE IF NOT EXISTS "asset_allocation"  (instrument int not null,asset int not null,ratio int not null,FOREIGN KEY(instrument) REFERENCES instrument(id),FOREIGN KEY (asset) REFERENCES asset(id));
CREATE TABLE currency (id INTEGER PRIMARY KEY, name text not null);
INSERT INTO currency (name) VALUES('JPY');
INSERT INTO currency (name) VALUES('USD');
INSERT INTO currency (name) VALUES('EUR');
INSERT INTO currency (name) VALUES('CNY');
INSERT INTO currency (name) VALUES('AUD');
INSERT INTO currency (name) VALUES('NZD');
INSERT INTO currency (name) VALUES('HKD');
CREATE TABLE instrument (id INTEGER PRIMARY KEY, name text not null, type int null,  currency int null, "url" TEXT, "expense_ratio" FLOAT, active INTEGER NOT NULL DEFAULT 1, FOREIGN KEY(currency) REFERENCES currency(id),FOREIGN KEY(type) REFERENCES instrument_type(id));
CREATE TABLE fund(instrument int not null , broker int not null, amount int ,price real , value real , profit real , capital real ,date int not null, 
FOREIGN KEY(instrument) REFERENCES "instrument"(id),
FOREIGN KEY(broker) REFERENCES broker(id));
CREATE INDEX fund_date on fund(date);
CREATE TABLE IF NOT EXISTS "transaction" ("instrument" int NOT NULL , "broker"	int NOT NULL, "type" text NOT NULL ,"price" real NOT NULL ,"shares" real   ,"fee" real ,"date" int NOT NULL ,FOREIGN KEY(broker) REFERENCES broker(id));
CREATE TABLE xccy ([from] int not null ,[to] int not null,rate real , date int not null, FOREIGN KEY([from]) REFERENCES currency(id), FOREIGN KEY([to]) REFERENCES currency(id));
CREATE TABLE IF NOT EXISTS "quote" ("instrument" int NOT NULL ,"price" real NOT NULL ,"date" int NOT NULL ,FOREIGN KEY(instrument) REFERENCES instrument(id));
CREATE UNIQUE INDEX "quoteidx" ON "quote" (
	"instrument"	ASC,
	"date"	ASC
);
CREATE TABLE country (id INTEGER PRIMARY KEY, name text);
INSERT INTO country (name) VALUES('US');
INSERT INTO country (name) VALUES('Europe placeholder');
INSERT INTO country (name) VALUES('S.Korea');
INSERT INTO country (name) VALUES('China');
INSERT INTO country (name) VALUES('Japan');
INSERT INTO country (name) VALUES('Asia Other');
INSERT INTO country (name) VALUES('S.America Other');
INSERT INTO country (name) VALUES('Brazil');
INSERT INTO country (name) VALUES('E.Europe Other');
INSERT INTO country (name) VALUES('Australia');
INSERT INTO country (name) VALUES('Taiwan');
INSERT INTO country (name) VALUES('Other');
INSERT INTO country (name) VALUES('Africa Other');
INSERT INTO country (name) VALUES('Middle East Other');
INSERT INTO country (name) VALUES('Singapore');
INSERT INTO country (name) VALUES('Canada');
INSERT INTO country (name) VALUES('UK');
INSERT INTO country (name) VALUES('Germany');
INSERT INTO country (name) VALUES('France');
INSERT INTO country (name) VALUES('NZ');
INSERT INTO country (name) VALUES('Switzerland');
INSERT INTO country (name) VALUES('Hong Kong');
INSERT INTO country (name) VALUES('India');
INSERT INTO country (name) VALUES('W.Europe Other');
CREATE TABLE region(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);
INSERT INTO region (name) VALUES('N.America');
INSERT INTO region (name) VALUES('S.America');
INSERT INTO region (name) VALUES('Asia');
INSERT INTO region (name) VALUES('E.Europe');
INSERT INTO region (name) VALUES('W.Europe');
INSERT INTO region (name) VALUES('Oceania');
INSERT INTO region (name) VALUES('Africa');
INSERT INTO region (name) VALUES('Other');
INSERT INTO region (name) VALUES('Middle East');
INSERT INTO region (name) VALUES('Other');
CREATE TABLE regions (
  region      INT  NOT NULL,
  country     INT  NOT NULL,
  FOREIGN KEY (region) REFERENCES region (id),
  FOREIGN KEY (country) REFERENCES country (id)
);


-- country => region
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'N.America'),
  (SELECT ROWID
   FROM country
   WHERE name = 'US')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'N.America'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Canada')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'S.America'),
  (SELECT ROWID
   FROM country
   WHERE name = 'S.America Other')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Asia'),
  (SELECT ROWID
   FROM country
   WHERE name = 'China')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Asia'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Taiwan')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Asia'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Japan')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Asia'),
  (SELECT ROWID
   FROM country
   WHERE name = 'India')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Asia'),
  (SELECT ROWID
   FROM country
   WHERE name = 'S.Korea')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Asia'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Singapore')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Asia'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Asia Other')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Oceania'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Australia')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'W.Europe'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Europe placeholder')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'W.Europe'),
  (SELECT ROWID
   FROM country
   WHERE name = 'UK')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'W.Europe'),
  (SELECT ROWID
   FROM country
   WHERE name = 'France')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'W.Europe'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Germany')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'E.Europe'),
  (SELECT ROWID
   FROM country
   WHERE name = 'E.Europe Other')
);
INSERT INTO regions (region, country) VALUES (
  (SELECT ROWID
   FROM region
   WHERE name = 'Other'),
  (SELECT ROWID
   FROM country
   WHERE name = 'Other')
);
CREATE TABLE IF NOT EXISTS "country_allocation" ("instrument" int NOT NULL ,"country" int NOT NULL ,"ratio" real NOT NULL  DEFAULT (null),FOREIGN KEY(instrument) REFERENCES instrument(id),FOREIGN KEY (country) REFERENCES country(id) );

CREATE TABLE portfolio(
  id INTEGER PRIMARY KEY,
  name  TEXT NOT NULL
);
CREATE TABLE portfolio_allocation(
  id INTEGER PRIMARY KEY,
  portfolio   INT  NOT NULL,
  instrument  INT  NOT NULL,
  percentage  REAL NOT NULL,
  FOREIGN KEY (portfolio) REFERENCES portfolio(id),
  FOREIGN KEY (instrument) REFERENCES instrument(id)
);

CREATE VIEW portfolio_v as
  SELECT p.name, i.id as instrument_id, i.name as instrument_name, it.type,  a.percentage from portfolio_allocation a, portfolio p, instrument i, instrument_type it
  WHERE p.id = a.portfolio and a.instrument = i.id and i.type = it.id

CREATE TABLE filter(
  id INTEGER PRIMARY KEY,
  name  TEXT NOT NULL,
  extra TEXT
);
CREATE TABLE instrument_filter(
  filter      INT  NOT NULL,
  instrument  INT  NOT NULL,
  FOREIGN KEY (filter) REFERENCES filter(id),
  FOREIGN KEY (instrument) REFERENCES instrument(id)
);
CREATE TABLE cash(
  ccy INT NOT NULL,
  broker INT NOT NULL,
  balance REAL NOT NULL,
  FOREIGN KEY (ccy) REFERENCES currency(id),
  FOREIGN KEY (broker) REFERENCES broker(id)
);
CREATE VIEW xccy_hist as
select c1.id as from_id, c1.name as [From] , c2.id as to_id, c2.name as [To],x.rate,x.date
from xccy x, currency c1, currency c2 where c1.id=x.[from] and c2.id=x.[to] order by x.date;
CREATE VIEW xccy_hist2 as
select from_id,[From],to_id,[To],rate, datetime(date, 'unixepoch') as datestr
from xccy_hist;
CREATE VIEW instrument_xccy as
select
i.id instrument, i.name, i.type instrument_type_id, a.type instrument_type, c.name currency, ifnull(x.rate,1) rate
from instrument i
join instrument_type a on i.type = a.id
join currency c on i.currency = c.id
left join ( select * from xccy_hist2 where datestr = (select max(datestr) from xccy_hist2)) x on c.name = x.[From];
CREATE VIEW stock_trans as 
  select i.name, b.name as broker, t.type,t.price,t.shares,t.fee,t.date,date(t.date, 'unixepoch') as datestr 
  from "transaction" t,instrument i, broker b where t.instrument = i.id and t.broker = b.id;
CREATE VIEW instrument_filters AS
  SELECT
    n.name  as filter_name,
    n.extra as extra,
    i.name  as instrument_name,
    i.id as instrument_id
  FROM filter n
    LEFT JOIN instrument_filter f
      ON n.id = f.filter
    LEFT JOIN instrument i
      ON f.instrument = i.id;
CREATE VIEW cash_balance AS
  SELECT
    ccy.name AS ccy,
    b.name AS broker,
    c.balance
  FROM currency ccy, broker b, cash c
  WHERE c.ccy=ccy.id AND c.broker=b.id;
CREATE VIEW fund_performance AS 
  select p.ROWID as id,b.name as broker ,i.name,i.id as instrument_id, i.url ,i.expense_ratio, t.type,c.name currency,p.amount,p.price,p.value,p.profit,p.capital,
         date(p.date , 'unixepoch') as datestr, p.date from fund p, instrument i, broker b,instrument_type t,currency c 
  where p.instrument = i.id and p.broker = b.id and i.type=t.id and i.currency=c.id;
-- get the most recent performance for each fund
CREATE VIEW fund_performance2 as
select v1.* from fund_performance v1
join
(
select broker,date from fund_performance
join (
 select max(id) as id from fund_performance
 join(
  select broker,max(date) as date from fund_performance group by broker
 ) t1 using (broker, date)
 group by broker
) t2 using (id)
order by broker
) v2 using (broker,date);
COMMIT;

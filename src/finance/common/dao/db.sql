BEGIN TRANSACTION;

-- Tables

CREATE TABLE IF NOT EXISTS asset (
  type TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS broker (
  name     TEXT NOT NULL,
  fullName TEXT
);

CREATE TABLE IF NOT EXISTS currency (
  name TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS country (
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS region (
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instrument (
  name          TEXT NOT NULL,
  type          INT,
  broker        INT,
  currency      INT,
  url           TEXT,
  expense_ratio FLOAT,
  FOREIGN KEY (currency) REFERENCES currency (rowid),
  FOREIGN KEY (type) REFERENCES instrument_type (rowid),
  FOREIGN KEY (broker) REFERENCES broker (rowid)
);

CREATE TABLE IF NOT EXISTS instrument_type (
  type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS performance (
  instrument INT NOT NULL,
  amount     INT,
  price      REAL,
  value      REAL,
  profit     REAL,
  capital    REAL,
  date       INT NOT NULL,
  FOREIGN KEY (instrument) REFERENCES instrument (rowid)
);

CREATE TABLE IF NOT EXISTS asset_allocation (
  instrument INT NOT NULL,
  asset      INT NOT NULL,
  ratio      INT NOT NULL,
  FOREIGN KEY (instrument) REFERENCES instrument (rowid),
  FOREIGN KEY (asset) REFERENCES asset (rowid)
);

CREATE TABLE IF NOT EXISTS quote (
  instrument INT  NOT NULL,
  price      REAL NOT NULL,
  date       INT  NOT NULL,
  FOREIGN KEY (
    instrument
  )
  REFERENCES instrument (rowid)
);

CREATE TABLE IF NOT EXISTS country_allocation (
  instrument INT  NOT NULL,
  country    INT  NOT NULL,
  ratio      REAL NOT NULL,
  FOREIGN KEY (instrument) REFERENCES instrument (rowid),
  FOREIGN KEY (country) REFERENCES country (rowid)
);

CREATE TABLE IF NOT EXISTS regions (
  region  INT NOT NULL,
  country INT NOT NULL,
  FOREIGN KEY (region) REFERENCES region (rowid),
  FOREIGN KEY (country) REFERENCES country (rowid)
);

CREATE TABLE IF NOT EXISTS [transaction] (
  instrument INT  NOT NULL,
  type       TEXT NOT NULL,
  price      REAL NOT NULL,
  shares     REAL,
  fee        REAL,
  date       INT  NOT NULL
);

CREATE TABLE IF NOT EXISTS xccy (
  [from] INT NOT NULL,
  [to]   INT NOT NULL,
  rate   REAL,
  date   INT NOT NULL,
  FOREIGN KEY (
    [from]
  )
  REFERENCES currency (rowid),
  FOREIGN KEY (
    [to]
  )
  REFERENCES currency (rowid)
);

CREATE TABLE IF NOT EXISTS filter (
  name  TEXT NOT NULL,
  extra TEXT
);

CREATE TABLE IF NOT EXISTS instrument_filter (
  filter     INT NOT NULL,
  instrument INT NOT NULL,
  FOREIGN KEY (filter) REFERENCES filter (ROWID),
  FOREIGN KEY (instrument) REFERENCES instrument (ROWID)
);

CREATE TABLE IF NOT EXISTS cash (
  ccy     INT  NOT NULL,
  broker  INT  NOT NULL,
  balance REAL NOT NULL,
  FOREIGN KEY (ccy) REFERENCES currency (ROWID),
  FOREIGN KEY (broker) REFERENCES broker (ROWID)
);

-- Views
CREATE VIEW cash_balance AS
  SELECT
    ccy.name AS ccy,
    b.name   AS broker,
    c.balance
  FROM currency ccy, broker b, cash c
  WHERE c.ccy = ccy.ROWID AND c.broker = b.ROWID;

CREATE VIEW instrument_filters AS
  SELECT
    n.name  AS filter_name,
    n.extra AS extra,
    i.name  AS instrument_name,
    i.ROWID AS instrument_id
  FROM filter n
    LEFT JOIN instrument_filter f
      ON n.ROWID = f.filter
    LEFT JOIN instrument i
      ON f.instrument = i.ROWID;

CREATE VIEW fund_performance AS
SELECT
  p.rowid                   AS rowid,
  b.name                    AS broker,
  i.name,
  i.rowid                   AS instrument_id,
  i.url,
  i.expense_ratio,
  t.type,
  c.name                       currency,
  p.amount,
  p.price,
  p.value,
  p.profit,
  p.capital,
  date(p.date, 'unixepoch') AS datestr,
  p.date
FROM performance p, instrument i, broker b, instrument_type t, currency c
WHERE p.instrument = i.rowid AND i.broker = b.rowid AND i.type = t.rowid AND i.currency = c.rowid;


CREATE VIEW fund_performance2 AS
  SELECT v1.*
  FROM fund_performance v1
    JOIN
    (
      SELECT
        broker,
        date
      FROM fund_performance
        JOIN (
               SELECT max(rowid) AS rowid
               FROM fund_performance
                 JOIN (
                        SELECT
                          broker,
                          max(date) AS date
                        FROM fund_performance
                        GROUP BY broker
                      ) t1 USING (broker, date)
               GROUP BY broker
             ) t2 USING (rowid)
      ORDER BY broker
    ) v2 USING (broker, date);


CREATE VIEW stock_quote AS
  SELECT
    i.name,
    t.price,
    t.date
  FROM quote t,
    instrument i
  WHERE t.instrument = i.rowid;

CREATE VIEW stock_trans AS
  SELECT
    i.name,
    t.type,
    t.price,
    t.shares,
    t.fee,
    t.date,
    date(t.date, 'unixepoch') AS datestr
  FROM [transaction] t,
    instrument i
  WHERE t.instrument = i.rowid;

CREATE VIEW xccy_hist AS
  SELECT
    c1.rowid AS from_id,
    c1.name  AS [From],
    c2.rowid AS to_id,
    c2.name  AS [To],
    x.rate,
    x.date
  FROM xccy x,
    currency c1,
    currency c2
  WHERE c1.rowid = x.[from] AND
        c2.rowid = x.[to]
  ORDER BY x.date;

CREATE VIEW xccy_hist2 AS
  SELECT
    from_id,
    [From],
    to_id,
    [To],
    rate,
    datetime(date, 'unixepoch') AS datestr
  FROM xccy_hist;

CREATE VIEW instrument_xccy AS
  SELECT
    i.rowid           instrument,
    i.name,
    i.type            instrument_type_id,
    a.type            instrument_type,
    c.name            currency,
    ifnull(x.rate, 1) rate
  FROM instrument i
    JOIN
    instrument_type a ON i.type = a.rowid
    JOIN
    currency c ON i.currency = c.rowid
    LEFT JOIN
    (
      SELECT *
      FROM xccy_hist2
      WHERE datestr = (
        SELECT max(datestr)
        FROM xccy_hist2
      )
    )
    x ON c.name = x.[From];

-- Populate meta data -  this is for DEMO site only

-- broker data is purely fake
INSERT INTO broker (name, fullName) VALUES ('ABC', 'ABC Asset Management');
INSERT INTO broker (name, fullName) VALUES ('XYZ', 'XYZ Securities');
INSERT INTO broker (name, fullName) VALUES ('IB', 'IB');

-- asset
INSERT INTO asset (type) VALUES ('Stock');
INSERT INTO asset (type) VALUES ('Government Bond');
INSERT INTO asset (type) VALUES ('Corp Bond');
INSERT INTO asset (type) VALUES ('REIT');
INSERT INTO asset (type) VALUES ('Gold');
INSERT INTO asset (type) VALUES ('Cash');
INSERT INTO asset (type) VALUES ('Other');

-- currency
INSERT INTO currency (name) VALUES ('JPY');
INSERT INTO currency (name) VALUES ('USD');
INSERT INTO currency (name) VALUES ('EUR');
INSERT INTO currency (name) VALUES ('CNY');
INSERT INTO currency (name) VALUES ('AUD');
INSERT INTO currency (name) VALUES ('NZD');

-- instrument type
INSERT INTO instrument_type (type) VALUES ('ETF');
INSERT INTO instrument_type (type) VALUES ('Stock');
INSERT INTO instrument_type (type) VALUES ('Funds');
INSERT INTO instrument_type (type) VALUES ('Bond');
INSERT INTO instrument_type (type) VALUES ('Cash');

-- country
INSERT INTO country (name) VALUES ('US');
INSERT INTO country (name) VALUES ('Canada');
INSERT INTO country (name) VALUES ('S.Korea');
INSERT INTO country (name) VALUES ('China');
INSERT INTO country (name) VALUES ('Singapore');
INSERT INTO country (name) VALUES ('India');
INSERT INTO country (name) VALUES ('Japan');
INSERT INTO country (name) VALUES ('Asia Other');
INSERT INTO country (name) VALUES ('UK');
INSERT INTO country (name) VALUES ('France');
INSERT INTO country (name) VALUES ('Germany');
INSERT INTO country (name) VALUES ('Russia');
INSERT INTO country (name) VALUES ('E.Europe Other');
INSERT INTO country (name) VALUES ('W.Europe Other');
INSERT INTO country (name) VALUES ('S.Africa');
INSERT INTO country (name) VALUES ('Africa Other');
INSERT INTO country (name) VALUES ('Australia');
INSERT INTO country (name) VALUES ('Other');
INSERT INTO country (name) VALUES ('Middle East');
INSERT INTO country (name) VALUES ('S.America');

-- region
INSERT INTO region (name) VALUES ('N.America');
INSERT INTO region (name) VALUES ('S.America');
INSERT INTO region (name) VALUES ('Asia');
INSERT INTO region (name) VALUES ('E.Europe');
INSERT INTO region (name) VALUES ('W.Europe');
INSERT INTO region (name) VALUES ('Oceania');
INSERT INTO region (name) VALUES ('Africa');
INSERT INTO region (name) VALUES ('Other');

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

COMMIT TRANSACTION;


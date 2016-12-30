CREATE TABLE IF NOT EXISTS asset(
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS broker(
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS region(
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instrument (
  name     TEXT NOT NULL ,
  asset    INTEGER DEFAULT NULL,
  broker   INTEGER DEFAULT NULL,
  currency TEXT NOT NULL ,
  FOREIGN KEY (asset) REFERENCES asset(ROWID),
  FOREIGN KEY (broker) REFERENCES broker(ROWID)
);

-- populate meta data


CREATE TABLE entity (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('country', 'region', 'world')),
    region TEXT,
    numeric_code TEXT
) STRICT;

CREATE TABLE observation (
    entity_id TEXT NOT NULL REFERENCES entity(id),
    year INTEGER NOT NULL CHECK (year BETWEEN 2010 AND 2023),
    co2 REAL CHECK (co2 >= 0),
    population INTEGER CHECK (population > 0),
    gdp REAL CHECK (gdp > 0),
    coal REAL CHECK (coal >= 0),
    oil REAL CHECK (oil >= 0),
    gas REAL CHECK (gas >= 0),
    cement REAL CHECK (cement >= 0),
    flaring REAL CHECK (flaring >= 0),
    industry REAL CHECK (industry >= 0),
    PRIMARY KEY (entity_id, year)
) STRICT;

CREATE INDEX observation_year ON observation (year, entity_id);

CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
) STRICT;

CREATE VIEW indicators AS
SELECT o.*, e.name, e.kind, e.region,
       o.co2 * 1000000.0 / o.population AS per_capita,
       o.co2 * 1000000000.0 / o.gdp AS intensity
FROM observation AS o
JOIN entity AS e ON e.id = o.entity_id;

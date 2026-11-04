-- Fase 1: diseño PostgreSQL, pendiente de ejecución y carga en Fase 2.
-- Conserva instantáneas; solo una puede ser la versión activa del dashboard.
BEGIN;

CREATE TABLE ingestion_runs (
    run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_url text NOT NULL,
    source_sha256 char(64) NOT NULL CHECK (source_sha256 ~ '^[0-9a-f]{64}$'),
    codebook_sha256 char(64) NOT NULL CHECK (codebook_sha256 ~ '^[0-9a-f]{64}$'),
    retrieved_at timestamptz NOT NULL,
    rules_version text NOT NULL,
    is_active boolean NOT NULL DEFAULT false,
    UNIQUE (source_sha256, codebook_sha256, rules_version)
);
CREATE UNIQUE INDEX one_active_run ON ingestion_runs ((1)) WHERE is_active;

CREATE TABLE locations (
    entity_code text PRIMARY KEY,
    name text NOT NULL,
    entity_kind text NOT NULL CHECK (entity_kind IN ('country', 'region', 'world')),
    iso3 char(3) UNIQUE,
    CHECK ((entity_kind = 'country' AND iso3 IS NOT NULL AND iso3 ~ '^[A-Z]{3}$')
        OR (entity_kind <> 'country' AND iso3 IS NULL))
);

CREATE TABLE annual_observations (
    run_id bigint NOT NULL REFERENCES ingestion_runs(run_id),
    entity_code text NOT NULL REFERENCES locations(entity_code),
    year smallint NOT NULL CHECK (year BETWEEN 2010 AND 2023),
    co2_mt numeric CHECK (co2_mt >= 0),
    population numeric CHECK (population > 0),
    gdp_ppp_2011 numeric CHECK (gdp_ppp_2011 > 0),
    co2_pc_source numeric CHECK (co2_pc_source >= 0),
    co2_gdp_source numeric CHECK (co2_gdp_source >= 0),
    coal_mt numeric CHECK (coal_mt >= 0),
    oil_mt numeric CHECK (oil_mt >= 0),
    gas_mt numeric CHECK (gas_mt >= 0),
    cement_mt numeric CHECK (cement_mt >= 0),
    flaring_mt numeric CHECK (flaring_mt >= 0),
    other_industry_mt numeric CHECK (other_industry_mt >= 0),
    PRIMARY KEY (run_id, entity_code, year)
);
CREATE INDEX observations_by_year ON annual_observations (year, entity_code);

CREATE TABLE quality_events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id bigint NOT NULL REFERENCES ingestion_runs(run_id),
    entity_name text NOT NULL,
    year smallint,
    field_name text NOT NULL,
    rule_name text NOT NULL,
    original_value text,
    review_status text NOT NULL DEFAULT 'pending'
        CHECK (review_status IN ('pending', 'accepted', 'corrected', 'excluded')),
    review_note text
);

CREATE VIEW active_metrics AS
SELECT o.*, l.name, l.entity_kind, l.iso3,
       o.co2_mt * 1000000 / NULLIF(o.population, 0) AS co2_t_per_person,
       o.co2_mt * 1000000000 / NULLIF(o.gdp_ppp_2011, 0) AS co2_kg_per_dollar,
       o.gdp_ppp_2011 / NULLIF(o.population, 0) AS gdp_per_person
FROM annual_observations o
JOIN ingestion_runs r USING (run_id)
JOIN locations l USING (entity_code)
WHERE r.is_active;

-- Los rankings deben consultar únicamente entity_kind = 'country'.
-- Las series continentales utilizan entity_kind = 'region' y nunca suman World.
-- La activación del lote se realizará al final de una transacción validada.
COMMIT;

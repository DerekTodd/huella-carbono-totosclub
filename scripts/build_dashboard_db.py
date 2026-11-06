"""Construye la base SQLite del dashboard desde la instantánea de la Fase 1."""
import csv
import json
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/processed'
DESTINATION = ROOT / 'public/data/huella.sqlite'
REGIONS = {
    'Africa': ('AF', 'África'), 'Asia': ('AS', 'Asia'), 'Europe': ('EU', 'Europa'),
    'North America': ('NA', 'América del Norte'), 'South America': ('SA', 'América del Sur'),
    'Oceania': ('OC', 'Oceanía'), 'World': ('WORLD', 'Mundo'),
}
FUELS = ('coal_co2', 'oil_co2', 'gas_co2', 'cement_co2', 'flaring_co2', 'other_industry_co2')


def country_region(country):
    region = country.get('region')
    if region == 'Americas':
        region = 'South America' if country.get('subregion') == 'South America' else 'North America'
    return REGIONS.get(region, (None, None))[0]


def read_rows(name):
    with (SOURCE / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def observation(row, entity_id):
    def number(field):
        value = row[field]
        return float(value) if value else None

    population = number('population')
    return (entity_id, int(row['year']), number('co2'), int(population) if population else None,
            number('gdp'), *(number(field) for field in FUELS))


def main():
    catalog = json.loads((ROOT / 'node_modules/world-countries/countries.json').read_text(encoding='utf-8'))
    catalog = {country['cca3']: country for country in catalog}
    countries = read_rows('countries_2010_2023.csv')
    regions = read_rows('regions_2010_2023.csv')
    quality = json.loads((SOURCE / 'quality_report.json').read_text(encoding='utf-8'))
    entities = {}
    observations = []

    for row in countries:
        code = row['iso_code']
        if code not in entities:
            metadata = catalog.get(code, {})
            name = metadata.get('translations', {}).get('spa', {}).get('common') or row['country']
            entities[code] = (code, name, row['country'], 'country', country_region(metadata), metadata.get('ccn3'))
        observations.append(observation(row, code))

    for row in regions:
        source_name = row['country']
        code, name = REGIONS[source_name]
        kind = 'world' if code == 'WORLD' else 'region'
        entities[code] = (code, name, source_name, kind, code, None)
        observations.append(observation(row, code))

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix='.sqlite', dir=DESTINATION.parent, delete=False) as file:
        temporary = Path(file.name)
    try:
        with closing(sqlite3.connect(temporary)) as database:
            database.execute('PRAGMA foreign_keys = ON')
            database.executescript((ROOT / 'db/dashboard.sql').read_text(encoding='utf-8'))
            with database:
                database.executemany('INSERT INTO entity VALUES (?, ?, ?, ?, ?, ?)', entities.values())
                database.executemany('INSERT INTO observation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', observations)
                database.executemany('INSERT INTO metadata VALUES (?, ?)', [
                    ('source_url', quality['source_url']), ('source_sha256', quality['sha256']),
                    ('analysis_date', quality['analysis_date_local']),
                ])
            assert database.execute('PRAGMA integrity_check').fetchone() == ('ok',)
            assert not database.execute('PRAGMA foreign_key_check').fetchall()
        temporary.replace(DESTINATION)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'SQLite: {len(entities)} entidades, {len(observations)} observaciones, {DESTINATION.stat().st_size:,} bytes.')


if __name__ == '__main__':
    main()

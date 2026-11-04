"""Comprobación independiente de integridad y KPIs contra el original local."""
import csv
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    raw_path = ROOT / 'data/raw/owid-co2-data.csv'
    report = json.loads((ROOT / 'data/processed/quality_report.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == report['sha256'], 'SHA del origen distinto'
    source = read(raw_path)
    expected = [r for r in source if 2010 <= int(r['year']) <= 2023
                and re.fullmatch('[A-Z]{3}', r['iso_code'])]
    clean = read(ROOT / 'data/processed/countries_2010_2023.csv')
    assert len(clean) == len(expected) == report['country_rows'], 'Conteo de filas distinto'
    assert len({(r['iso_code'], r['year']) for r in clean}) == len(clean), 'Claves duplicadas'
    source_lookup = {(r['iso_code'], r['year']): r for r in expected}
    for row in clean:
        raw = source_lookup[(row['iso_code'], row['year'])]
        for field in ['co2', 'population', 'gdp']:
            if raw[field]:
                assert math.isclose(float(row[field]), float(raw[field]), rel_tol=1e-12)
            else:
                assert row[field] == '', 'Se imputó una ausencia'
        if row['co2'] and row['population']:
            independent = float(raw['co2']) / (float(raw['population']) / 1e6)
            assert math.isclose(float(row['co2_per_capita_calc']), independent, rel_tol=1e-12)
        if row['co2'] and row['gdp']:
            independent = float(raw['co2']) / (float(raw['gdp']) / 1e9)
            assert math.isclose(float(row['co2_per_gdp_calc']), independent, rel_tol=1e-12)
    for coverage in report['coverage_by_year']:
        group = [r for r in expected if int(r['year']) == coverage['year']]
        assert len(group) == coverage['rows']
        for field in ['co2', 'population', 'gdp']:
            assert sum(bool(r[field]) for r in group) == coverage[field]
    regions = read(ROOT / 'data/processed/regions_2010_2023.csv')
    assert len(regions) == report['regional_rows']
    assert {r['country'] for r in regions} == {'Africa', 'Asia', 'Europe', 'North America',
                                             'South America', 'Oceania', 'World'}
    raw_top = sorted([r for r in expected if r['year'] == '2023' and r['co2']],
                     key=lambda r: (-float(r['co2']), r['iso_code']))[:5]
    assert [r['iso_code'] for r in raw_top] == [r['iso_code'] for r in report['top5_2023_preview']]
    candidates = []
    for end in [r for r in expected if r['year'] == '2023' and r['co2']]:
        start = source_lookup.get((end['iso_code'], '2013'))
        if not start or not start['co2'] or float(start['co2']) < 1:
            continue
        if not all(source_lookup.get((end['iso_code'], str(y)), {}).get('co2') for y in range(2013, 2024)):
            continue
        change = (float(end['co2']) - float(start['co2'])) / float(start['co2']) * 100
        candidates.append((change, end['iso_code']))
    winner = min(candidates)
    observed = report['largest_relative_reduction_2013_2023_preview'][0]
    assert winner[1] == observed['iso_code'] and math.isclose(winner[0], observed['change_pct'])
    flags = read(ROOT / 'data/processed/quality_flags.csv')
    assert dict(Counter(r['rule'] for r in flags)) == report['issue_counts']
    assert {r['entity'] for r in flags if r['rule'] == 'derived_discrepancy'} == {'North America', 'Oceania'}
    print('OK: SHA-256, filas, claves, ausencia sin imputación, cobertura, regiones, unidades y KPIs.')
    print(f'Validación: {len(clean)} registros de países/territorios; {len(regions)} regionales.')


if __name__ == '__main__':
    main()

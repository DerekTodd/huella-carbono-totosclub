"""Perfilado y limpieza reproducible del CSV de OWID. Solo biblioteca estándar."""
import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://owid-public.owid.io/data/co2/owid-co2-data.csv'
CODEBOOK = 'https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv'
REGIONS = {'Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'World'}
FIELDS = ['iso_code', 'country', 'year', 'co2', 'population', 'gdp', 'co2_per_capita', 'co2_per_gdp',
          'coal_co2', 'oil_co2', 'gas_co2', 'cement_co2', 'flaring_co2', 'other_industry_co2']
NUMERIC = FIELDS[3:]


def download(url, path, refresh):
    if refresh or not path.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'HuellaCarbono-AnalisisAcademico/1.0'})
        with urllib.request.urlopen(req, timeout=90) as response:
            path.write_bytes(response.read())
    return path.read_bytes()


def write_csv(path, rows, columns):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true', help='Descargar una nueva instantánea')
    args = parser.parse_args()
    raw_dir = ROOT / 'data/raw'
    out = ROOT / 'data/processed'
    raw_dir.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / 'owid-co2-data.csv'
    payload = download(URL, raw_path, args.refresh)
    book = download(CODEBOOK, raw_dir / 'owid-co2-codebook.csv', args.refresh)
    reader = csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
    missing_columns = set(FIELDS) - set(reader.fieldnames or [])
    if missing_columns:
        raise ValueError(f'Columnas requeridas ausentes: {sorted(missing_columns)}')
    input_columns = reader.fieldnames
    rows = list(reader)
    selected = [r for r in rows if 2010 <= int(r['year']) <= 2023]
    countries, regional, issues, quarantine = [], [], [], []
    seen = {}
    duplicates = 0
    for raw in selected:
        iso = raw['iso_code'].strip()
        name = raw['country'].strip()
        is_country = bool(re.fullmatch('[A-Z]{3}', iso))
        if not is_country and name not in REGIONS:
            continue
        kind = 'country' if is_country else 'region'
        key = (kind, iso if is_country else name, int(raw['year']))
        if key in seen:
            if seen[key] != raw:
                raise ValueError(f'Duplicado conflictivo: {key}')
            duplicates += 1
            continue
        seen[key] = raw
        row = {f: raw.get(f, '').strip() for f in FIELDS}
        row['year'] = int(row['year'])
        bad_co2 = False
        for field in NUMERIC:
            value = row[field]
            if not value:
                row[field] = None
                continue
            try:
                number = float(value)
                valid = math.isfinite(number) and number >= 0
                if field in {'population', 'gdp'}:
                    valid = valid and number > 0
                if not valid:
                    raise ValueError('fuera de dominio')
                row[field] = number
            except ValueError:
                issues.append({'entity': name, 'year': row['year'], 'field': field,
                               'rule': 'invalid_domain', 'source_value': value})
                row[field] = None
                bad_co2 = bad_co2 or field == 'co2'
        if bad_co2:
            quarantine.append({'entity': name, 'year': row['year'], 'reason': 'co2_invalid'})
            continue
        row['co2_per_capita_calc'] = (row['co2'] * 1e6 / row['population']
                                        if row['co2'] is not None and row['population'] else None)
        row['co2_per_gdp_calc'] = (row['co2'] * 1e9 / row['gdp']
                                    if row['co2'] is not None and row['gdp'] else None)
        if row['co2_per_capita'] is not None and row['co2_per_capita_calc'] is not None:
            tolerance = max(0.005, 500 / row['population'] + 0.0005)
            if abs(row['co2_per_capita_calc'] - row['co2_per_capita']) > tolerance:
                issues.append({'entity': name, 'year': row['year'], 'field': 'co2_per_capita',
                               'rule': 'derived_discrepancy', 'source_value': raw['co2_per_capita']})
        (countries if is_country else regional).append(row)
    countries.sort(key=lambda r: (r['iso_code'], r['year']))
    regional.sort(key=lambda r: (r['country'], r['year']))
    for year in range(2010, 2024):
        group = [r for r in countries if r['year'] == year]
        for field in ['co2', 'co2_per_capita_calc']:
            vals = sorted(r[field] for r in group if r[field] is not None)
            if len(vals) < 4:
                continue
            q1, _, q3 = statistics.quantiles(vals, n=4, method='inclusive')
            low, high = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
            for row in group:
                val = row[field]
                if val is not None and (val < low or val > high):
                    issues.append({'entity': row['country'], 'year': year, 'field': field,
                                   'rule': 'iqr_review_keep', 'source_value': val})
    lookup = {(r['iso_code'], r['year']): r for r in countries}
    for row in countries:
        prev = lookup.get((row['iso_code'], row['year'] - 1))
        if prev and prev['co2'] and row['co2'] is not None:
            pct = (row['co2'] / prev['co2'] - 1) * 100
            if abs(pct) > 30:
                issues.append({'entity': row['country'], 'year': row['year'], 'field': 'co2',
                               'rule': 'annual_change_gt_30_review_keep', 'source_value': pct})
    coverage = []
    for year in range(2010, 2024):
        group = [r for r in countries if r['year'] == year]
        coverage.append({'year': year, 'rows': len(group),
                         **{f: sum(r[f] is not None for r in group) for f in ['co2', 'population', 'gdp']},
                         'gdp_co2_pairs': sum(r['co2'] is not None and r['gdp'] is not None for r in group)})
    target = [r for r in countries if r['year'] == 2023 and r['co2'] is not None]
    top5 = sorted(target, key=lambda r: (-r['co2'], r['iso_code']))[:5]
    improvements = []
    for end in target:
        start = lookup.get((end['iso_code'], 2013))
        if not start or not start['co2'] or start['co2'] < 1:
            continue
        if any(lookup.get((end['iso_code'], y), {}).get('co2') is None for y in range(2013, 2024)):
            continue
        improvements.append({'country': end['country'], 'iso_code': end['iso_code'],
                             'co2_2013': start['co2'], 'co2_2023': end['co2'],
                             'change_pct': (end['co2'] / start['co2'] - 1) * 100})
    improvements.sort(key=lambda r: (r['change_pct'], r['iso_code']))
    report = {
        'analysis_date_local': '2026-11-04',
        'source_url': URL, 'sha256': hashlib.sha256(payload).hexdigest(), 'source_bytes': len(payload),
        'codebook_url': CODEBOOK, 'codebook_sha256': hashlib.sha256(book).hexdigest(),
        'processed_at_utc': datetime.now(timezone.utc).isoformat(),
        'input_rows': len(rows), 'input_columns': len(input_columns), 'rows_2010_2023_all_entities': len(selected),
        'country_rows': len(countries), 'country_entities': len({r['iso_code'] for r in countries}),
        'regional_rows': len(regional),
        'excluded_non_iso_entities': sorted({r['country'] for r in selected
            if not re.fullmatch('[A-Z]{3}', r['iso_code'].strip()) and r['country'] not in REGIONS}),
        'exact_duplicates_removed': duplicates, 'conflicting_duplicates': 0,
        'quarantined_rows': len(quarantine), 'issue_counts': dict(Counter(i['rule'] for i in issues)),
        'coverage_by_year': coverage,
        'top5_2023_preview': [{f: r[f] for f in ['iso_code', 'country', 'co2']} for r in top5],
        'largest_relative_reduction_2013_2023_preview': improvements[:1],
        'sector_columns_found': [f for f in input_columns if 'sector' in f.lower() or f in {'transport_co2', 'electricity_co2'}],
        'scope': 'ISO3 countries/territories only; OWID special entities excluded from country rankings',
    }
    columns = FIELDS + ['co2_per_capita_calc', 'co2_per_gdp_calc']
    write_csv(out / 'countries_2010_2023.csv', countries, columns)
    write_csv(out / 'regions_2010_2023.csv', regional, columns)
    write_csv(out / 'quality_flags.csv', issues, ['entity', 'year', 'field', 'rule', 'source_value'])
    write_csv(out / 'quarantine.csv', quarantine, ['entity', 'year', 'reason'])
    (out / 'quality_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

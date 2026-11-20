function query(database, sql, parameters = []) {
  const statement = database.prepare(sql)
  try {
    statement.bind(parameters)
    const rows = []
    while (statement.step()) rows.push(statement.getAsObject())
    return rows
  } finally {
    statement.free()
  }
}

export function loadCatalog(database) {
  return query(database, "SELECT * FROM entity WHERE kind = 'country'")
    .sort((a, b) => a.name.localeCompare(b.name, 'es'))
}

export function loadYear(database, year) {
  const rows = query(database, `
    SELECT current.*, previous.co2 AS previous_co2, baseline.co2 AS baseline_co2
    FROM indicators AS current
    LEFT JOIN observation AS previous ON previous.entity_id = current.entity_id AND previous.year = current.year - 1
    LEFT JOIN observation AS baseline ON baseline.entity_id = current.entity_id AND baseline.year = current.year - 10
    WHERE current.year = ?
    ORDER BY current.co2 DESC, current.entity_id ASC`, [year])
  const countries = rows.filter(row => row.kind === 'country')
  const world = rows.find(row => row.kind === 'world')
  const eligible = year >= 2020 ? query(database, `
    SELECT current.entity_id, current.name, current.co2, baseline.co2 AS baseline_co2,
           100.0 * (current.co2 / baseline.co2 - 1) AS change
    FROM indicators AS current
    JOIN observation AS baseline ON baseline.entity_id = current.entity_id AND baseline.year = current.year - 10
    WHERE current.year = ? AND current.kind = 'country' AND current.co2 IS NOT NULL AND baseline.co2 >= 1
      AND (SELECT COUNT(*) FROM observation AS history
           WHERE history.entity_id = current.entity_id AND history.year BETWEEN current.year - 10 AND current.year
             AND history.co2 IS NOT NULL) = 11
    ORDER BY change ASC, current.entity_id ASC`, [year]) : []
  const reductions = eligible.filter(row => row.change < 0)
  return {
    countries,
    world,
    top: countries.filter(row => row.co2 !== null).slice(0, 5),
    improvement: reductions[0] ?? null,
    reductions: reductions.slice(0, 5),
    eligibleCount: eligible.length,
  }
}

export function loadTrends(database, ids, start, end) {
  if (!ids.length) return []
  return query(database, `SELECT entity_id, year, co2, per_capita FROM indicators
    WHERE entity_id IN (${ids.map(() => '?').join(',')}) AND year BETWEEN ? AND ?
    ORDER BY year`, [...ids, start, end])
}

export function loadAnnualChanges(database, start, end) {
  // El primer año de la instantánea conserva su cambio como nulo.
  return query(database, `
    SELECT current.year, current.co2, previous.co2 AS previous_co2,
           100.0 * (current.co2 / NULLIF(previous.co2, 0) - 1) AS change
    FROM observation AS current
    LEFT JOIN observation AS previous
      ON previous.entity_id = current.entity_id AND previous.year = current.year - 1
    WHERE current.entity_id = 'WORLD' AND current.year BETWEEN ? AND ?
    ORDER BY current.year`, [start, end])
}

export function loadEconomy(database, year, region) {
  const [{ last_year }] = query(database, "SELECT MAX(year) AS last_year FROM indicators WHERE kind = 'country' AND gdp > 0 AND co2 > 0")
  const effectiveYear = Math.min(last_year, year)
  const rows = query(database, `SELECT entity_id, name, region, co2, gdp, intensity FROM indicators
    WHERE kind = 'country' AND year = ? AND co2 > 0 AND gdp > 0
      AND (? = '' OR region = ?) ORDER BY co2 DESC`, [effectiveYear, region, region])
  return { year: effectiveYear, rows }
}


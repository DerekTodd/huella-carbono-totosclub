import initSqlJs from 'sql.js'
import wasmUrl from 'sql.js/dist/sql-wasm.wasm?url'

export const YEARS = Array.from({ length: 14 }, (_, i) => 2010 + i)
export const REGIONS = [
  { id: 'AS', name: 'Asia', color: '#13745a' },
  { id: 'EU', name: 'Europa', color: '#5c58a8' },
  { id: 'NA', name: 'América del Norte', color: '#a45021' },
  { id: 'SA', name: 'América del Sur', color: '#197b93' },
  { id: 'AF', name: 'África', color: '#a53e72' },
  { id: 'OC', name: 'Oceanía', color: '#696f31' },
]
export const COMPARE_COLORS = ['#13745a', '#5c58a8', '#a45021']
export const FUELS = [
  { id: 'coal', name: 'Carbón', color: '#174d3e' },
  { id: 'oil', name: 'Petróleo', color: '#45876c' },
  { id: 'gas', name: 'Gas', color: '#90be77' },
  { id: 'cement', name: 'Cemento', color: '#d6ad64' },
  { id: 'flaring', name: 'Quema de gas', color: '#aa674e' },
  { id: 'industry', name: 'Otros procesos', color: '#8578a6' },
  { id: 'residual', name: 'Sin desglose', color: '#b8c4bc' },
]

let databasePromise

export function openDatabase() {
  if (!databasePromise) {
    databasePromise = Promise.all([
      initSqlJs({ locateFile: () => wasmUrl }),
      fetch(`${import.meta.env.BASE_URL}data/huella.sqlite`).then(response => {
        if (!response.ok) throw new Error(`No se pudo cargar la base de datos (${response.status}).`)
        return response.arrayBuffer()
      }),
    ]).then(([SQL, file]) => {
      const database = new SQL.Database(new Uint8Array(file))
      database.run('PRAGMA query_only = ON')
      return database
    }).catch(error => {
      databasePromise = undefined
      throw error
    })
  }
  return databasePromise
}

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
  return { countries, world, top: countries.filter(row => row.co2 !== null).slice(0, 5),
    improvement: eligible[0]?.change < 0 ? eligible[0] : null, eligibleCount: eligible.length }
}

export function loadTrends(database, ids, start, end) {
  if (!ids.length) return []
  return query(database, `SELECT entity_id, year, co2, per_capita FROM indicators
    WHERE entity_id IN (${ids.map(() => '?').join(',')}) AND year BETWEEN ? AND ?
    ORDER BY year`, [...ids, start, end])
}

export function loadEconomy(database, year, region) {
  const [{ last_year }] = query(database, "SELECT MAX(year) AS last_year FROM indicators WHERE kind = 'country' AND gdp > 0 AND co2 > 0")
  const effectiveYear = Math.min(last_year, year)
  const rows = query(database, `SELECT entity_id, name, region, co2, gdp, intensity FROM indicators
    WHERE kind = 'country' AND year = ? AND co2 > 0 AND gdp > 0
      AND (? = '' OR region = ?) ORDER BY co2 DESC`, [effectiveYear, region, region])
  return { year: effectiveYear, rows }
}

export function variation(value, baseline) {
  return value !== null && value !== undefined && baseline > 0 ? 100 * (value / baseline - 1) : null
}

export function number(value, digits = 1) {
  return value === null || value === undefined ? '—' : new Intl.NumberFormat('es-MX', { maximumFractionDigits: digits }).format(value)
}

export function percent(value) {
  return value === null || value === undefined ? '—' : `${value > 0 ? '+' : ''}${number(value, 1)} %`
}

export function tonnes(value) {
  if (value === null || value === undefined) return 'Sin datos'
  return value >= 1000 ? `${number(value / 1000, 2)} Gt` : `${number(value, 2)} Mt`
}

export function dollars(value) {
  if (value === null || value === undefined) return 'Sin datos'
  if (value >= 1e12) return `$${number(value / 1e12, 2)} billones`
  if (value >= 1e9) return `$${number(value / 1e9, 2)} mil millones`
  return `$${number(value / 1e6, 1)} millones`
}

export function normalized(text) {
  return text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

export function exportRows(rows, year) {
  const headers = ['país', 'ISO3', 'año', 'CO2_Mt', 'población', 'CO2_t_por_persona', 'PIB_PPA_2011', 'CO2_kg_por_dólar', 'variación_anual_pct', 'variación_decena_pct']
  const csv = [headers, ...rows.map(row => [row.name, row.entity_id, year, row.co2, row.population, row.per_capita,
    row.gdp, row.intensity, variation(row.co2, row.previous_co2), variation(row.co2, row.baseline_co2)])]
    .map(row => row.map(value => `"${String(value ?? '').replaceAll('"', '""')}"`).join(',')).join('\r\n')
  const url = URL.createObjectURL(new Blob(['\ufeff', csv], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `totosclub-emisiones-${year}.csv`
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

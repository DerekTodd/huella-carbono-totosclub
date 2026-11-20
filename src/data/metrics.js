export function variation(value, baseline) {
  return Number.isFinite(value) && Number.isFinite(baseline) && baseline > 0
    ? 100 * (value / baseline - 1)
    : null
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

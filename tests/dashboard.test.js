import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { after, test } from 'node:test'
import initSqlJs from 'sql.js'
import { loadAnnualChanges, loadCatalog, loadEconomy, loadTrends, loadYear } from '../src/data/queries.js'
import { percent, tonnes, variation } from '../src/data/metrics.js'

const SQL = await initSqlJs()
const database = new SQL.Database(readFileSync(new URL('../public/data/huella.sqlite', import.meta.url)))
after(() => database.close())

test('el catálogo y el ranking separan países de agregados', () => {
  const catalog = loadCatalog(database)
  const data = loadYear(database, 2023)
  assert.equal(catalog.length, 218)
  assert.equal(data.countries.length, 218)
  assert.deepEqual(data.top.map(row => row.entity_id), ['CHN', 'USA', 'IND', 'RUS', 'JPN'])
  assert.equal(data.world.entity_id, 'WORLD')
  assert.ok(data.world.co2 > data.top.reduce((sum, row) => sum + row.co2, 0))
})

test('el ranking de reducciones usa diez años, cobertura completa y orden ascendente', () => {
  const data = loadYear(database, 2023)
  assert.equal(data.improvement.entity_id, 'CUW')
  assert.equal(data.reductions[0].entity_id, data.improvement.entity_id)
  assert.equal(data.reductions.length, 5)
  assert.ok(Math.abs(data.improvement.change - (-62.83012464531714)) < 1e-8)
  for (const [index, row] of data.reductions.entries()) {
    assert.ok(row.baseline_co2 >= 1)
    assert.ok(row.change < 0)
    assert.equal(loadTrends(database, [row.entity_id], 2013, 2023).filter(item => item.co2 !== null).length, 11)
    if (index) assert.ok(data.reductions[index - 1].change <= row.change)
  }
  assert.deepEqual(loadYear(database, 2019).reductions, [])
  assert.equal(loadYear(database, 2019).improvement, null)
})

test('la serie mundial conserva el agregado y el cambio anual maneja el año inicial', () => {
  const trend = loadTrends(database, ['WORLD'], 2010, 2023)
  const changes = loadAnnualChanges(database, 2010, 2023)
  assert.equal(trend.length, 14)
  assert.equal(changes[0].change, null)
  assert.ok(changes.find(row => row.year === 2020).change < 0)
  assert.ok(changes.find(row => row.year === 2021).change > 0)
  assert.equal(trend.at(-1).co2, loadYear(database, 2023).world.co2)
  assert.equal(changes.at(-1).change, variation(changes.at(-1).co2, changes.at(-1).previous_co2))
  // El recorte visual conserva el año previo de la instantánea para calcular 2021.
  assert.equal(loadAnnualChanges(database, 2021, 2023)[0].previous_co2, trend.find(row => row.year === 2020).co2)
})

test('el análisis económico usa pares del mismo año y respeta el filtro de región', () => {
  const economy = loadEconomy(database, 2023, '')
  assert.equal(economy.year, 2022)
  assert.equal(economy.rows.length, 164)
  assert.ok(economy.rows.every(row => row.co2 > 0 && row.gdp > 0))
  const northAmerica = loadEconomy(database, 2021, 'NA')
  assert.equal(northAmerica.year, 2021)
  assert.ok(northAmerica.rows.length > 0)
  assert.ok(northAmerica.rows.every(row => row.region === 'NA'))
  assert.equal(loadEconomy(database, 2022, "NA' OR 1=1 --").rows.length, 0)
})

test('faltantes, cero y unidades se mantienen diferenciados', () => {
  const data = loadYear(database, 2023)
  const mexico = data.countries.find(row => row.entity_id === 'MEX')
  assert.equal(mexico.gdp, null)
  assert.equal(mexico.intensity, null)
  assert.equal(data.countries.find(row => row.entity_id === 'MCO').co2, null)
  assert.ok(Math.abs(mexico.per_capita - mexico.co2 * 1e6 / mexico.population) < 1e-10)
  assert.equal(variation(0, 100), -100)
  assert.equal(variation(100, 0), null)
  assert.equal(variation(null, 100), null)
  assert.equal(variation(Infinity, 100), null)
  assert.equal(percent(0), '0 %')
  assert.equal(tonnes(1000), '1 Gt')
  assert.equal(tonnes(null), 'Sin datos')
})

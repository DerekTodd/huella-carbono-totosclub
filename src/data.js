import initSqlJs from 'sql.js'
import wasmUrl from 'sql.js/dist/sql-wasm.wasm?url'

export const YEARS = Array.from({ length: 14 }, (_, i) => 2010 + i)
export const REGIONS = [
  { id: 'AS', name: 'Asia', color: '#13745a', dash: '' },
  { id: 'EU', name: 'Europa', color: '#5c58a8', dash: '8 4' },
  { id: 'NA', name: 'América del Norte', color: '#a45021', dash: '2 4' },
  { id: 'SA', name: 'América del Sur', color: '#197b93', dash: '10 3 2 3' },
  { id: 'AF', name: 'África', color: '#a53e72', dash: '5 3' },
  { id: 'OC', name: 'Oceanía', color: '#696f31', dash: '1 3' },
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

export { loadCatalog, loadYear, loadTrends, loadEconomy, loadAnnualChanges } from './data/queries.js'
export { variation, number, percent, tonnes, dollars, normalized, exportRows } from './data/metrics.js'

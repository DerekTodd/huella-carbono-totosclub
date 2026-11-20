import { useMemo, useState } from 'react'
import { ArrowDown, ArrowDownUp, ArrowLeft, ArrowRight, ArrowUp, Download, Search } from 'lucide-react'
import { dollars, exportRows, normalized, number, percent, variation } from '../data'

const PAGE_SIZE = 10

const COLUMNS = [
  { id: 'name', name: 'País o territorio' }, { id: 'co2', name: 'CO₂ total (Mt)', render: row => number(row.co2, 2) },
  { id: 'per_capita', name: 't por persona', render: row => number(row.per_capita, 2) },
  { id: 'annual', name: 'Cambio anual', render: row => percent(variation(row.co2, row.previous_co2)) },
  { id: 'decade', name: 'Cambio decenal', render: row => percent(variation(row.co2, row.baseline_co2)) },
  { id: 'population', name: 'Población', render: row => number(row.population, 0) },
  { id: 'gdp', name: 'PIB · PPA', render: row => row.gdp == null ? '—' : dollars(row.gdp) },
  { id: 'intensity', name: 'kg CO₂/$', render: row => number(row.intensity, 3) },
]

function sortableValue(row, field) {
  if (field === 'annual') return variation(row.co2, row.previous_co2)
  if (field === 'decade') return variation(row.co2, row.baseline_co2)
  return row[field]
}

export function DataTable({ rows, year, onSelect, selected }) {
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState({ field: 'co2', direction: -1 })
  const [page, setPage] = useState(0)
  const filtered = useMemo(() => rows.filter(row => normalized(`${row.name} ${row.entity_id}`).includes(normalized(search.trim())))
    .sort((a, b) => {
      const av = sortableValue(a, sort.field)
      const bv = sortableValue(b, sort.field)
      if (av == null || bv == null) return Number(av == null) - Number(bv == null)
      return sort.direction * (typeof av === 'string' ? av.localeCompare(bv, 'es') : av - bv)
    }), [rows, search, sort])
  const lastPage = Math.max(0, Math.ceil(filtered.length / PAGE_SIZE) - 1)
  const currentPage = Math.min(page, lastPage)
  const first = currentPage * PAGE_SIZE

  return <div className="card table-card">
    <div className="table-controls">
      <label className="search"><Search size={18} /><input type="search" aria-label="Buscar país o código ISO3" placeholder="Buscar país o código ISO3" value={search} onChange={event => { setSearch(event.target.value); setPage(0) }} /></label>
      <span className="table-count">{filtered.length} {filtered.length === 1 ? 'resultado' : 'resultados'} · {year}</span>
      <button type="button" className="button download" onClick={() => exportRows(filtered, year)} disabled={!filtered.length}><Download size={16} /> Descargar CSV</button>
    </div>
    <div className="table-scroll" tabIndex={0} aria-label="Tabla de indicadores, desplazamiento horizontal">
      <table>
        <thead><tr>{COLUMNS.map(column => {
          const active = sort.field === column.id
          const Icon = active ? sort.direction === 1 ? ArrowUp : ArrowDown : ArrowDownUp
          return <th key={column.id} scope="col" aria-sort={active ? sort.direction === 1 ? 'ascending' : 'descending' : 'none'}><button type="button" onClick={() => {
            setSort({ field: column.id, direction: active ? -sort.direction : column.id === 'name' ? 1 : -1 }); setPage(0)
          }}>{column.name}<Icon size={13} /></button></th>
        })}</tr></thead>
        <tbody>{filtered.length ? filtered.slice(first, first + PAGE_SIZE).map(row => <tr key={row.entity_id}>
          <th scope="row"><button className="table-country" type="button" aria-pressed={selected.includes(row.entity_id)} onClick={() => onSelect(row.entity_id)}><strong>{row.name}</strong><small>{row.entity_id}</small></button></th>
          {COLUMNS.slice(1).map(column => <td key={column.id}>{column.render(row)}</td>)}
        </tr>) : <tr><td colSpan={COLUMNS.length} className="empty-table">No hay países que coincidan con la búsqueda.</td></tr>}</tbody>
      </table>
    </div>
    <div className="table-footer"><span>{filtered.length ? `${first + 1}–${Math.min(first + PAGE_SIZE, filtered.length)} de ${filtered.length}` : '0 resultados'} · — sin dato</span>
      <div><button type="button" aria-label="Página anterior" onClick={() => setPage(currentPage - 1)} disabled={!currentPage}><ArrowLeft size={17} /></button>
        <button type="button" aria-label="Página siguiente" onClick={() => setPage(currentPage + 1)} disabled={currentPage === lastPage}><ArrowRight size={17} /></button></div>
    </div>
  </div>
}

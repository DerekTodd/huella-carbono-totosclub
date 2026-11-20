import { BarChart3, CalendarDays, Globe2, RotateCcw, X } from 'lucide-react'
import { COMPARE_COLORS, REGIONS } from '../data'

export function Controls({ year, setYear, region, setRegion, catalog, selected, onSelect, reset, message }) {
  const available = catalog.filter(row => !selected.includes(row.id) && (!region || row.region === region))
  return <div className="controls card" aria-label="Filtros del dashboard">
    <div className="controls-row">
      <div className="year-control">
        <label htmlFor="year"><CalendarDays size={16} /> Año de referencia <output htmlFor="year">{year}</output></label>
        <div className="range-row"><span>2010</span><input id="year" type="range" min="2010" max="2023" value={year} onChange={event => setYear(Number(event.target.value))} /><span>2023</span></div>
      </div>
      <label className="select-field"><span><Globe2 size={16} /> Región</span>
        <select aria-label="Región" value={region} onChange={event => setRegion(event.target.value)}><option value="">Todas las regiones</option>{REGIONS.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select>
      </label>
      <label className="select-field compare-field"><span><BarChart3 size={16} /> Comparar países</span>
        <select aria-label="Añadir país a la comparación" value="" disabled={selected.length === 3} onChange={event => onSelect(event.target.value)}>
          <option value="">{selected.length === 3 ? '3 países seleccionados' : 'Añadir un país'}</option>
          {available.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}
        </select>
      </label>
      <button className="button subtle reset" type="button" onClick={reset}><RotateCcw size={16} /> Restablecer</button>
    </div>
    {(selected.length > 0 || message) && <div className="comparison-pills">
      {selected.map((id, index) => <button type="button" key={id} className="pill" onClick={() => onSelect(id)} aria-label={`Quitar ${catalog.find(row => row.id === id)?.name}`}>
        <i style={{ background: COMPARE_COLORS[index] }} />{catalog.find(row => row.id === id)?.name}<X size={14} />
      </button>)}<span className="selection-status" role="status">{message || `${selected.length} de 3 países`}</span>
    </div>}
  </div>
}

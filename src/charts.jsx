import { useMemo, useState } from 'react'
import { geoNaturalEarth1, geoPath } from 'd3-geo'
import { feature } from 'topojson-client'
import atlas from 'world-atlas/countries-110m.json'
import { ArrowUpRight, Globe2, MapPin } from 'lucide-react'
import { FUELS, REGIONS, dollars, number, tonnes } from './data'

const MAP_WIDTH = 700
const MAP_HEIGHT = 346
const mapFeatures = feature(atlas, atlas.objects.countries).features.filter(item => item.properties.name !== 'Antarctica')
const projection = geoNaturalEarth1().fitExtent([[8, 8], [692, 338]], { type: 'FeatureCollection', features: mapFeatures })
const pathFor = geoPath(projection)
const shapes = mapFeatures.map((item, index) => ({
  key: index, name: item.properties.name,
  numeric: item.id == null ? null : String(item.id).padStart(3, '0'), path: pathFor(item),
}))
const MAP_COLORS = ['#e2edcf', '#c3ddb1', '#92c18c', '#5b9e78', '#307961', '#174a3b']
const MAP_BINS = { per_capita: [0.5, 2, 5, 10, 20], co2: [10, 50, 200, 500, 1500] }
const MAP_ALIASES = { France: 'FRA', Norway: 'NOR' }
const VIEW = { width: 680, height: 280, left: 64, right: 18, top: 16, bottom: 43 }

function activateWithKeyboard(event, action) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    action()
  }
}

export function WorldMap({ catalog, countries, region, selected, onSelect, metric }) {
  const [hover, setHover] = useState(null)
  const lookup = useMemo(() => new Map(countries.map(row => [row.entity_id, row])), [countries])
  const mapIds = useMemo(() => new Map(catalog.filter(row => row.numeric_code).map(row => [row.numeric_code, row.id])), [catalog])
  const bins = MAP_BINS[metric]
  const unit = metric === 'per_capita' ? 't por persona' : 'Mt de CO₂'
  const hovered = lookup.get(hover)
  const focus = hovered && (!region || hovered.region === region) ? hovered : null

  return <>
    <div className="map-wrap">
      <svg viewBox={`0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`} role="group" aria-label="Mapa mundial de emisiones. Elige un país para compararlo.">
        {shapes.map(shape => {
          const id = mapIds.get(shape.numeric) ?? MAP_ALIASES[shape.name]
          const row = lookup.get(id)
          const value = row?.[metric]
          const visible = !region || row?.region === region
          const canSelect = row && visible
          const active = selected.includes(id)
          const color = value == null ? '#dce3df' : MAP_COLORS[bins.filter(limit => value >= limit).length]
          const select = () => onSelect(id)
          return <path key={shape.key} d={shape.path} fill={color}
            className={`map-shape${canSelect ? ' can-select' : ''}${active ? ' is-selected' : ''}`}
            opacity={visible ? 1 : 0.24} tabIndex={canSelect ? 0 : undefined}
            role={canSelect ? 'button' : undefined} aria-pressed={canSelect ? active : undefined}
            aria-label={canSelect ? `${row.name}: ${value == null ? 'sin datos' : `${number(value, 2)} ${unit}`}` : undefined}
            onPointerEnter={canSelect ? () => setHover(id) : undefined} onPointerLeave={() => setHover(null)}
            onFocus={canSelect ? () => setHover(id) : undefined} onBlur={() => setHover(null)}
            onClick={canSelect ? select : undefined} onKeyDown={canSelect ? event => activateWithKeyboard(event, select) : undefined} />
        })}
      </svg>
    </div>
    <div className="map-meta">
      <div className="map-scale" aria-label={`Escala en ${unit}`}>
        {MAP_COLORS.map((color, i) => <span key={color} title={i === 0 ? `Menos de ${bins[0]}` : `Desde ${bins[i - 1]}`}>
          <i style={{ background: color }} />{i === 0 ? '0' : `${bins[i - 1]}${i === 5 ? '+' : ''}`}
        </span>)}
        <span className="missing-key"><i />Sin datos</span>
      </div>
      <span className="map-unit">{unit}</span>
    </div>
    <div className="chart-readout" aria-live="polite">
      {focus ? <><MapPin size={15} /><strong>{focus.name}</strong><span>{focus[metric] == null ? 'Sin datos' : `${number(focus[metric], 2)} ${unit}`}</span></> : <><Globe2 size={15} /><span>Selecciona un país para añadirlo a la comparación.</span></>}
    </div>
  </>
}

export function TopRanking({ rows, world, year, onSelect, selected }) {
  const max = rows[0]?.co2 || 1
  return <>
    <ol className="ranking-list">
      {rows.map((row, index) => <li key={row.entity_id}>
        <button type="button" onClick={() => onSelect(row.entity_id)} aria-pressed={selected.includes(row.entity_id)}>
          <span className="rank-number">0{index + 1}</span>
          <span className="rank-body">
            <span className="rank-label"><strong>{row.name}</strong><span>{tonnes(row.co2)}</span></span>
            <span className="rank-track"><i style={{ width: `${100 * row.co2 / max}%` }} /></span>
          </span>
          <ArrowUpRight className="rank-arrow" size={15} />
        </button>
      </li>)}
    </ol>
    <p className="chart-caption">{year} · {number(100 * rows.reduce((total, row) => total + row.co2, 0) / world.co2, 1)} % del total mundial entre los cinco países.</p>
  </>
}

function linearTicks(maximum) {
  const step = 10 ** Math.floor(Math.log10(maximum / 4 || 1))
  const interval = [1, 2, 2.5, 5, 10].map(value => value * step).find(value => maximum / value <= 5)
  const top = Math.ceil(maximum / interval) * interval || interval
  return Array.from({ length: Math.round(top / interval) + 1 }, (_, i) => i * interval)
}

function Legend({ series, hidden, onToggle }) {
  return <div className="chart-legend">{series.map(item => onToggle ?
    <button key={item.id} type="button" className={hidden.includes(item.id) ? 'muted-legend' : ''}
      aria-pressed={!hidden.includes(item.id)} onClick={() => onToggle(item.id)}>
      <i style={{ background: item.color }} />{item.name}
    </button> : <span key={item.id}><i style={{ background: item.color }} />{item.name}</span>)}</div>
}

export function TrendChart({ rows, series, start, end }) {
  const [hidden, setHidden] = useState([])
  const [activeYear, setActiveYear] = useState(null)
  const enabled = series.filter(item => !hidden.includes(item.id))
  const visible = rows.filter(row => enabled.some(item => item.id === row.entity_id))
  const years = Array.from({ length: end - start + 1 }, (_, index) => start + index)
  const inspection = Math.min(end, Math.max(start, activeYear ?? end))
  const ticks = linearTicks(Math.max(1, ...visible.map(row => row.co2 ?? 0)))
  const plotWidth = VIEW.width - VIEW.left - VIEW.right
  const plotHeight = VIEW.height - VIEW.top - VIEW.bottom
  const x = year => VIEW.left + (year - start) / Math.max(1, end - start) * plotWidth
  const y = value => VIEW.top + plotHeight * (1 - value / ticks.at(-1))
  const byYear = new Map(visible.map(row => [`${row.entity_id}:${row.year}`, row.co2]))
  const toggle = id => setHidden(previous => previous.includes(id) ? previous.filter(item => item !== id) : [...previous, id])

  function inspect(event) {
    const bounds = event.currentTarget.getBoundingClientRect()
    const point = (event.clientX - bounds.left) * VIEW.width / bounds.width
    setActiveYear(Math.round(start + (point - VIEW.left) / plotWidth * (end - start)))
  }

  return <>
    <Legend series={series} hidden={hidden} onToggle={toggle} />
    {visible.some(row => row.co2 !== null) ? <>
      <svg className="plot" viewBox={`0 0 ${VIEW.width} ${VIEW.height}`} aria-label="Series temporales de CO₂. Usa las flechas para recorrer los años." role="img" tabIndex={0}
        onPointerMove={inspect} onPointerLeave={() => setActiveYear(null)} onKeyDown={event => {
          if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            event.preventDefault()
            setActiveYear(inspection + (event.key === 'ArrowLeft' ? -1 : 1))
          }
        }}>
        {ticks.map(value => <g key={value}><line className="gridline" x1={VIEW.left} x2={VIEW.width - VIEW.right} y1={y(value)} y2={y(value)} /><text className="axis-label" x={VIEW.left - 9} y={y(value) + 4} textAnchor="end">{number(value, ticks.at(-1) < 10 ? 2 : 0)}</text></g>)}
        {years.filter((year, i) => i === 0 || i === years.length - 1 || (i % 2 === 0 && i < years.length - 2)).map(year =>
          <text className="axis-label" key={year} x={x(year)} y={VIEW.height - 15} textAnchor="middle">{year}</text>)}
        <line x1={x(inspection)} x2={x(inspection)} y1={VIEW.top} y2={VIEW.height - VIEW.bottom} stroke="#b5c9bd" strokeDasharray="4 5" />
        {enabled.map(item => {
          let previousExists = false
          const points = years.map(year => {
            const value = byYear.get(`${item.id}:${year}`)
            if (value == null) { previousExists = false; return '' }
            const command = previousExists ? 'L' : 'M'
            previousExists = true
            return `${command}${x(year)},${y(value)}`
          }).join(' ')
          const current = byYear.get(`${item.id}:${inspection}`)
          return <g key={item.id}><path d={points} fill="none" stroke={item.color} strokeWidth="2.7" strokeLinejoin="round" strokeLinecap="round" />
            {current != null && <circle cx={x(inspection)} cy={y(current)} r="4.2" fill={item.color} stroke="white" strokeWidth="1.4" />}</g>
        })}
      </svg>
      <div className="chart-readout trend-readout" aria-live="polite"><strong>{inspection}</strong>{enabled.map(item =>
        <span key={item.id}><i style={{ background: item.color }} />{item.name} · {tonnes(byYear.get(`${item.id}:${inspection}`))}</span>)}</div>
    </> : <div className="empty-chart">Elige una serie con datos para mostrar la tendencia.</div>}
  </>
}

function logCorrelation(rows) {
  if (rows.length < 3) return null
  const pairs = rows.map(row => [Math.log10(row.gdp), Math.log10(row.co2)])
  const [meanX, meanY] = pairs.reduce(([sx, sy], [x, y]) => [sx + x / pairs.length, sy + y / pairs.length], [0, 0])
  const [xy, xx, yy] = pairs.reduce(([sum, squareX, squareY], [x, y]) => [sum + (x - meanX) * (y - meanY), squareX + (x - meanX) ** 2, squareY + (y - meanY) ** 2], [0, 0, 0])
  return xx && yy ? xy / Math.sqrt(xx * yy) : null
}

export function EconomyChart({ rows, year, selected, onSelect }) {
  const [hovered, setHovered] = useState(null)
  if (!rows.length) return <div className="empty-chart">No hay observaciones con PIB y emisiones para este filtro.</div>
  const active = rows.find(row => row.entity_id === hovered)
  const xLow = Math.floor(Math.log10(Math.min(...rows.map(row => row.gdp))))
  const xHigh = Math.max(xLow + 1, Math.ceil(Math.log10(Math.max(...rows.map(row => row.gdp)))))
  const yLow = Math.floor(Math.log10(Math.min(...rows.map(row => row.co2))))
  const yHigh = Math.max(yLow + 1, Math.ceil(Math.log10(Math.max(...rows.map(row => row.co2)))))
  const plotWidth = VIEW.width - VIEW.left - VIEW.right
  const plotHeight = VIEW.height - VIEW.top - VIEW.bottom
  const x = value => VIEW.left + plotWidth * (Math.log10(value) - xLow) / (xHigh - xLow)
  const y = value => VIEW.top + plotHeight * (1 - (Math.log10(value) - yLow) / (yHigh - yLow))
  const xTicks = Array.from({ length: xHigh - xLow + 1 }, (_, i) => 10 ** (xLow + i))
  const yTicks = Array.from({ length: yHigh - yLow + 1 }, (_, i) => 10 ** (yLow + i))
  const correlation = logCorrelation(rows)
  const ordered = [...rows].sort((a, b) => Number(selected.includes(a.entity_id)) - Number(selected.includes(b.entity_id)))

  return <>
    <div className="scatter-summary"><span><strong>{rows.length}</strong> pares en {year}</span><span><strong>{number(correlation, 2)}</strong> r de Pearson en log₁₀</span></div>
    <svg className="plot scatter" viewBox={`0 0 ${VIEW.width} ${VIEW.height}`} role="group" aria-label="Gráfico de dispersión en escala logarítmica. Cada punto representa un país.">
      {yTicks.map(value => <g key={value}><line className="gridline" x1={VIEW.left} x2={VIEW.width - VIEW.right} y1={y(value)} y2={y(value)} /><text className="axis-label" x={VIEW.left - 8} y={y(value) + 4} textAnchor="end">{number(value, 3)}</text></g>)}
      {xTicks.map(value => <g key={value}><line className="gridline" x1={x(value)} x2={x(value)} y1={VIEW.top} y2={VIEW.height - VIEW.bottom} /><text className="axis-label" x={x(value)} y={VIEW.height - 23} textAnchor="middle">{`10${String(Math.round(Math.log10(value))).split('').map(digit => '⁰¹²³⁴⁵⁶⁷⁸⁹'[Number(digit)]).join('')}`}</text></g>)}
      <text className="axis-label" x={(VIEW.width + VIEW.left - VIEW.right) / 2} y={VIEW.height - 4} textAnchor="middle">PIB en dólares internacionales de 2011 · PPA</text>
      {ordered.map(row => {
        const isSelected = selected.includes(row.entity_id)
        const color = REGIONS.find(item => item.id === row.region)?.color ?? '#66746d'
        const choose = () => onSelect(row.entity_id)
        return <circle key={row.entity_id} cx={x(row.gdp)} cy={y(row.co2)} r={isSelected || row.entity_id === hovered ? 6.4 : 4.3} fill={color}
          className="scatter-point" opacity={isSelected ? 1 : 0.78} stroke={isSelected ? '#132b25' : 'white'} strokeWidth={isSelected ? 2 : 1}
          tabIndex={0} role="button" aria-pressed={isSelected} aria-label={`${row.name}, PIB ${dollars(row.gdp)}, emisiones ${tonnes(row.co2)}`}
          onPointerEnter={() => setHovered(row.entity_id)} onPointerLeave={() => setHovered(null)} onFocus={() => setHovered(row.entity_id)} onBlur={() => setHovered(null)}
          onClick={choose} onKeyDown={event => activateWithKeyboard(event, choose)} />
      })}
    </svg>
    <div className="chart-readout" aria-live="polite">{active ? <><strong>{active.name}</strong><span>PIB {dollars(active.gdp)} · {tonnes(active.co2)}</span></> : <span>CO₂ total en Mt · Selecciona un punto para comparar el país.</span>}</div>
  </>
}

export function FuelChart({ rows }) {
  const maximum = Math.max(1, ...rows.map(row => row.co2 || 0))
  return <>
    <Legend series={FUELS} />
    <div className="fuel-rows">{rows.map(row => {
      const observed = FUELS.filter(item => item.id !== 'residual' && row[item.id] > 0)
      const sum = observed.reduce((total, item) => total + row[item.id], 0)
      const compatible = row.co2 > 0 && sum > 0 && sum <= row.co2 + Math.max(0.05, row.co2 * 0.01)
      const residual = Math.max(0, (row.co2 ?? 0) - sum)
      const parts = [...observed.map(item => ({ ...item, value: row[item.id] })),
        ...(residual > 0.005 ? [{ ...FUELS.at(-1), value: residual }] : [])]
      return <div className="fuel-row" key={row.entity_id}>
        <div><strong>{row.name}</strong><span>{tonnes(row.co2)}</span></div>
        {compatible ? <div className="fuel-track" style={{ width: `${100 * row.co2 / maximum}%` }} role="img"
          aria-label={parts.map(part => `${part.name}: ${tonnes(part.value)}`).join(', ')}>
          {parts.map(part => <i key={part.id} style={{ background: part.color, flexGrow: part.value }} title={`${part.name} · ${tonnes(part.value)}`} />)}
        </div> : <small>Desglose insuficiente para esta observación.</small>}
      </div>
    })}</div>
    <p className="chart-caption">«Sin desglose» es la diferencia entre el total y los componentes publicados. Las categorías son combustibles y procesos.</p>
  </>
}

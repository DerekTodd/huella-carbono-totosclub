import { StrictMode, useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  Activity, ArrowDown, ArrowDownUp, ArrowLeft, ArrowRight, ArrowUp, ArrowUpRight, BarChart3,
  BookOpen, CalendarDays, Download, Globe2, Leaf, RotateCcw, Search, TrendingDown, X,
} from 'lucide-react'
import { EconomyChart, FuelChart, TopRanking, TrendChart, WorldMap } from './charts'
import {
  COMPARE_COLORS, REGIONS, YEARS, dollars, exportRows, loadCatalog, loadEconomy, loadTrends, loadYear,
  normalized, number, openDatabase, percent, tonnes, variation,
} from './data'
import './style.css'

const REPO = 'https://github.com/DerekTodd/huella-carbono-totosclub'
const SOURCE = 'https://github.com/owid/co2-data'
const REPORT = `${REPO}/blob/main/output/pdf/TotosClub_Fase1_Huella_de_Carbono.pdf`
const SECTIONS = [ ['panorama', 'Panorama'], ['tendencias', 'Tendencias'], ['datos', 'Datos'], ['metodo', 'Metodología'] ]
const PAGE_SIZE = 10

function Header() {
  return <header className="site-header">
    <div className="shell header-inner">
      <a className="brand" href="#inicio" aria-label="TotosClub, inicio"><span className="brand-icon"><Leaf size={22} /></span>
        <span><strong>TotosClub</strong><small>OBSERVATORIO CLIMÁTICO</small></span></a>
      <nav aria-label="Secciones del dashboard">{SECTIONS.map(([id, label]) => <a key={id} href={`#${id}`}>{label}</a>)}</nav>
      <span className="header-period"><i /> DATOS 2010–2023</span>
    </div>
  </header>
}

function Hero() {
  return <section id="inicio" className="hero" aria-labelledby="page-title">
    <div className="shell hero-inner">
      <div className="hero-copy">
        <div className="hero-label"><span /> OBSERVATORIO GLOBAL <b>01</b></div>
        <h1 id="page-title">Huella de <em>carbono</em></h1>
        <p className="hero-question">¿Quién contamina más?</p>
        <p className="hero-description">Explora cómo se distribuyen las emisiones de CO₂ y cómo cambian con la población y la economía.</p>
      </div>
      <svg className="hero-orb" viewBox="0 0 640 380" aria-hidden="true">
        <defs>
          <radialGradient id="orb-light"><stop offset="0" stopColor="#83bc7f" stopOpacity=".27"/><stop offset="1" stopColor="#83bc7f" stopOpacity="0"/></radialGradient>
          <pattern id="hero-dots" width="15" height="15" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r=".8" fill="#b8d5a0" opacity=".34"/></pattern>
        </defs>
        <rect width="640" height="380" fill="url(#hero-dots)"/>
        <circle cx="394" cy="193" r="195" fill="url(#orb-light)"/>
        <g fill="none" stroke="#9cc794" strokeWidth="1" opacity=".46" transform="rotate(-19 394 193)">
          <circle cx="394" cy="193" r="151"/><ellipse cx="394" cy="193" rx="115" ry="151"/><ellipse cx="394" cy="193" rx="60" ry="151"/>
          <path d="M394 42v302M243 193h302M266 114c66 31 191 31 256 0M266 272c66-31 191-31 256 0M300 70c49 22 140 22 188 0M300 316c49-22 140-22 188 0"/>
          <ellipse cx="394" cy="193" rx="223" ry="63" strokeDasharray="5 7" opacity=".55"/>
        </g>
        <g fill="#d1ed9e"><circle cx="475" cy="86" r="4.5"/><circle cx="317" cy="230" r="4"/><circle cx="523" cy="226" r="4"/></g>
        <g stroke="#d1ed9e" fill="none" opacity=".7"><circle cx="475" cy="86" r="10"/><circle cx="317" cy="230" r="10"/><path d="M485 86h58l21-21h52M307 230h-55l-25 25h-53"/></g>
        <text x="554" y="57" fill="#c5dbb6" fontSize="11" fontFamily="monospace" letterSpacing="2">CO₂ / 01</text>
      </svg>
      <div className="hero-stamp"><Globe2 size={19} /><div><strong>218</strong><span>países y territorios</span></div></div>
    </div>
  </section>
}

function CardHeading({ label, title, description, children, id }) {
  return <div className="card-heading">
    <div>{label && <span className="eyebrow">{label}</span>}<h3 id={id}>{title}</h3>{description && <p>{description}</p>}</div>
    {children}
  </div>
}

function SectionHeading({ number: index, title, description }) {
  return <div className="section-heading"><span>{index}</span><div><h2>{title}</h2><p>{description}</p></div></div>
}

function Segments({ options, value, onChange, label }) {
  return <div className="segments" role="group" aria-label={label}>{options.map(([id, name]) =>
    <button key={id} type="button" aria-pressed={value === id} onClick={() => onChange(id)}>{name}</button>)}</div>
}

function Controls({ year, setYear, region, setRegion, catalog, selected, onSelect, reset, message }) {
  const available = catalog.filter(row => !selected.includes(row.id) && (!region || row.region === region))
  return <div className="controls card" aria-label="Filtros del dashboard">
    <div className="controls-row">
      <div className="year-control">
        <label htmlFor="year"><CalendarDays size={16} /> Año de referencia <output htmlFor="year">{year}</output></label>
        <div className="range-row"><span>2010</span><input id="year" type="range" min="2010" max="2023" value={year} onChange={event => setYear(Number(event.target.value))} /><span>2023</span></div>
      </div>
      <label className="select-field"><span><Globe2 size={16} /> Región</span>
        <select value={region} onChange={event => setRegion(event.target.value)}><option value="">Todas las regiones</option>{REGIONS.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select>
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

function MetricCard({ icon: Icon, title, value, note, tag, tone }) {
  return <article className="card metric-card">
    <div className="metric-top"><span className={`metric-icon ${tone || ''}`}><Icon size={19} /></span>{tag && <span className="metric-tag">{tag}</span>}</div>
    <h3>{title}</h3><strong className="metric-value">{value}</strong><p>{note}</p>
  </article>
}

function Summary({ data, year }) {
  const annual = variation(data.world?.co2, data.world?.previous_co2)
  const leader = data.top[0]
  const improvement = data.improvement
  return <div className="metrics-grid">
    <MetricCard icon={Globe2} title="Emisiones mundiales" value={tonnes(data.world?.co2)} tag={year} note="CO₂ territorial · agregado mundial" />
    <MetricCard icon={annual < 0 ? ArrowDown : Activity} title="Variación mundial anual" value={percent(annual)} tone={annual > 0 ? 'warm' : ''} tag={year > 2010 ? `vs. ${year - 1}` : 'Inicio de serie'} note={annual == null ? 'Sin año previo en el periodo' : `${number(data.world.co2 - data.world.previous_co2, 1)} Mt de diferencia`} />
    <MetricCard icon={BarChart3} title="Mayor emisor" value={leader?.name ?? '—'} tag="GLOBAL" note={leader ? `${tonnes(leader.co2)} de CO₂ en ${year}` : 'Sin observaciones'} />
    <MetricCard icon={TrendingDown} title="Mayor reducción relativa" value={improvement?.name ?? '—'} tag={year >= 2020 ? `${year - 10}–${year}` : 'Década'} note={improvement ? `${percent(improvement.change)} · ${number(improvement.co2 - improvement.baseline_co2, 2)} Mt` : year < 2020 ? 'Disponible desde 2020' : 'Sin reducción entre los elegibles'} />
  </div>
}

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

function DataTable({ rows, year, onSelect, selected }) {
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
      <span className="table-count">{filtered.length} resultados · {year}</span>
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

function Methodology({ year, eligibleCount, economyYear }) {
  return <section id="metodo" className="page-section">
    <SectionHeading number="04" title="Cómo leer los datos" description="Definiciones, alcance y procedencia de los indicadores." />
    <div className="method-grid">
      <article className="card method-card"><Globe2 size={22} /><h3>Emisiones territoriales</h3><p>CO₂ anual de combustibles fósiles y procesos industriales. Se excluye el cambio de uso de suelo. El agregado mundial proviene de la fuente y considera el transporte internacional.</p><p>La medida por persona divide el CO₂ total en toneladas entre la población del mismo año.</p></article>
      <article className="card method-card"><TrendingDown size={22} /><h3>Cambios y reducción</h3><p>Variación (%) = 100 × (emisiones finales ÷ emisiones iniciales − 1). La década termina en el año elegido y usa una base de diez años atrás.</p><p>Para la mayor reducción se exige una base de 1 Mt y once observaciones anuales. {year >= 2020 ? `${eligibleCount} países y territorios elegibles en ${year}.` : 'El indicador se habilita a partir de 2020.'}</p></article>
      <article className="card method-card"><Activity size={22} /><h3>Economía y cobertura</h3><p>El PIB está expresado en dólares internacionales de 2011 ajustados por PPA. La intensidad divide los kg de CO₂ entre el PIB del mismo año.</p><p>La dispersión usa pares positivos del {economyYear}. La correlación describe una asociación. Los valores ausentes se conservan como tales.</p></article>
    </div>
    <div className="sources card"><div className="sources-intro"><BookOpen size={21} /><div><strong>Fuentes y entrega</strong><p>Our World in Data, Global Carbon Budget y Maddison Project Database. Cartografía de Natural Earth y clasificación geográfica de World Countries.</p></div></div>
      <div className="source-links"><a href={SOURCE} target="_blank" rel="noreferrer">Fuente de datos <ArrowUpRight size={15} /></a><a href={REPORT} target="_blank" rel="noreferrer">PDF de Fase 1 <ArrowUpRight size={15} /></a><a href={REPO} target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={15} /></a></div>
    </div>
  </section>
}

function Dashboard({ database }) {
  const [year, setYear] = useState(2023)
  const [region, setRegion] = useState('')
  const [selected, setSelected] = useState([])
  const [message, setMessage] = useState('')
  const [metric, setMetric] = useState('per_capita')
  const [trendMode, setTrendMode] = useState('regions')
  const [start, setStart] = useState(2010)
  const [resetKey, setResetKey] = useState(0)
  const catalog = useMemo(() => loadCatalog(database), [database])
  const data = useMemo(() => loadYear(database, year), [database, year])
  const filtered = useMemo(() => data.countries.filter(row => !region || row.region === region), [data, region])
  const economy = useMemo(() => loadEconomy(database, year, region), [database, year, region])
  const comparison = selected.map((id, index) => ({ id, name: catalog.find(row => row.id === id)?.name ?? id, color: COMPARE_COLORS[index] }))
  const series = trendMode === 'regions' ? REGIONS.filter(item => !region || item.id === region) : comparison
  const firstYear = Math.min(start, year)
  const trends = loadTrends(database, series.map(item => item.id), firstYear, year)
  const fuelRows = selected.length ? selected.map(id => data.countries.find(row => row.entity_id === id)).filter(Boolean) : data.top
  const perCapitaLeader = data.countries.reduce((best, row) => row.per_capita != null && row.per_capita > (best?.per_capita ?? -1) ? row : best, null)

  function choose(id) {
    if (!id) return
    setMessage('')
    if (selected.includes(id)) setSelected(selected.filter(item => item !== id))
    else if (selected.length < 3) { setSelected([...selected, id]); setTrendMode('countries') }
    else setMessage('Quita un país antes de añadir otro.')
  }

  function reset() {
    setYear(2023); setRegion(''); setSelected([]); setMetric('per_capita'); setTrendMode('regions'); setStart(2010); setMessage(''); setResetKey(value => value + 1)
  }

  return <main className="shell main-content" id="contenido">
    <section id="panorama" aria-label="Panorama de emisiones">
      <Controls {...{ year, setYear, region, setRegion, catalog, selected, reset, message }} onSelect={choose} />
      <Summary data={data} year={year} />
      <SectionHeading number="01" title="Panorama de emisiones" description={`Explora la distribución de CO₂ y los mayores emisores en ${year}.`} />
      <div className="overview-grid">
        <article className="card chart-card map-card">
          <CardHeading label="DISTRIBUCIÓN MUNDIAL" title={metric === 'per_capita' ? 'Emisiones por persona' : 'Emisiones totales'} description={`${year} · ${region ? REGIONS.find(item => item.id === region)?.name : 'Todos los países y territorios'}`}>
            <Segments options={[[ 'per_capita', 'Por persona' ], [ 'co2', 'Total' ]]} value={metric} onChange={setMetric} label="Métrica del mapa" />
          </CardHeading>
          <WorldMap {...{ catalog, region, selected, metric }} countries={data.countries} onSelect={choose} />
        </article>
        <article className="card chart-card ranking-card">
          <CardHeading label="RANKING GLOBAL" title="Los 5 mayores emisores" description="CO₂ territorial total por país" />
          <TopRanking rows={data.top} world={data.world} year={year} onSelect={choose} selected={selected} />
        </article>
      </div>
      {data.top[0] && perCapitaLeader && <aside className="insight"><span className="insight-icon"><Leaf size={20} /></span><div><strong>Dos formas de medir la huella en {year}</strong><p>{data.top[0].name} encabeza el volumen total con {tonnes(data.top[0].co2)}. {perCapitaLeader.name} registra el valor por persona más alto, con {number(perCapitaLeader.per_capita, 2)} t entre las entidades con datos.</p></div></aside>}
    </section>
    <section id="tendencias" className="page-section">
      <SectionHeading number="02" title="Tendencias y economía" description="Compara trayectorias y explora el vínculo entre actividad económica y CO₂." />
      <div className="analysis-grid">
        <article className="card chart-card trend-card">
          <CardHeading label="SERIE TEMPORAL" title="Evolución de las emisiones" description={`${firstYear}–${year} · CO₂ total en Mt`}>
            <Segments options={[[ 'regions', 'Continentes' ], [ 'countries', 'Países' ]]} value={trendMode} onChange={setTrendMode} label="Series del gráfico" />
          </CardHeading>
          <label className="trend-year">Desde <select aria-label="Inicio del intervalo" value={firstYear} onChange={event => setStart(Number(event.target.value))}>
            {YEARS.filter(value => value <= year).map(value => <option value={value} key={value}>{value}</option>)}
          </select><span>hasta {year}</span></label>
          <TrendChart key={`${trendMode}-${region}-${resetKey}`} rows={trends} series={series} start={firstYear} end={year} />
        </article>
        <article className="card chart-card economy-card">
          <CardHeading label="ACTIVIDAD ECONÓMICA" title="PIB frente a CO₂" description={`Países y territorios · ${economy.year} · ejes logarítmicos`} />
          {economy.year !== year && <p className="coverage-note">El PIB llega hasta {economy.year}. La gráfica usa emisiones y PIB de ese año.</p>}
          <EconomyChart rows={economy.rows} year={economy.year} selected={selected} onSelect={choose} />
        </article>
      </div>
      <article className="card chart-card fuel-card">
        <CardHeading label="COMPOSICIÓN" title="Emisiones por combustible y proceso" description={`${year} · ${selected.length ? 'Países seleccionados' : 'Cinco mayores emisores globales'} · CO₂ en Mt`} />
        <FuelChart rows={fuelRows} />
      </article>
    </section>
    <section id="datos" className="page-section">
      <SectionHeading number="03" title="Explorador de datos" description="Busca un país, ordena los indicadores y descarga la selección visible de año y región." />
      <DataTable key={resetKey} rows={filtered} year={year} onSelect={choose} selected={selected} />
    </section>
    <Methodology year={year} eligibleCount={data.eligibleCount} economyYear={economy.year} />
  </main>
}

function App() {
  const [state, setState] = useState({ database: null, error: null })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let active = true
    openDatabase().then(database => { if (active) setState({ database, error: null }) })
      .catch(error => { if (active) setState({ database: null, error }) })
    return () => { active = false }
  }, [attempt])

  return <>
    <a className="skip-link" href="#contenido">Saltar al contenido</a>
    <Header /><Hero />
    {state.database ? <Dashboard database={state.database} /> : <main className="shell main-content" id="contenido">
      <div className="card loading-state" role={state.error ? 'alert' : 'status'}><Leaf size={25} />
        <strong>{state.error ? 'Los datos no pudieron cargarse' : 'Cargando observaciones de CO₂…'}</strong>
        {state.error && <button type="button" className="button download" onClick={() => { setState({ database: null, error: null }); setAttempt(value => value + 1) }}><RotateCcw size={16} /> Reintentar</button>}
      </div>
    </main>}
    <footer><div className="shell footer-inner"><span><Leaf size={17} /> <strong>TotosClub</strong> · Derek Todd López</span><span>Huella de carbono · 2010–2023</span></div></footer>
  </>
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>)

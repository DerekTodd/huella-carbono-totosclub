import { StrictMode, useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Leaf, RotateCcw } from 'lucide-react'
import { Header, Hero } from './components/Layout'
import { CardHeading, SectionHeading, Segments } from './components/Shared'
import { Controls } from './components/Controls'
import { Summary } from './components/KpiCards'
import { DataTable } from './components/DataTable'
import { Methodology } from './components/Methodology'
import { AnnualChangeChart, EconomyChart, FuelChart, ReductionRanking, TopRanking, TrendChart, WorldMap } from './charts'
import {
  COMPARE_COLORS, REGIONS, YEARS, loadAnnualChanges, loadCatalog, loadEconomy, loadTrends, loadYear,
  number, openDatabase, tonnes,
} from './data'
import './style.css'

function Dashboard({ database }) {
  const [year, setYear] = useState(2023)
  const [region, setRegion] = useState('')
  const [selected, setSelected] = useState([])
  const [message, setMessage] = useState('')
  const [metric, setMetric] = useState('per_capita')
  const [trendMode, setTrendMode] = useState('regions')
  const [rankingMode, setRankingMode] = useState('top')
  const [start, setStart] = useState(2010)
  const [resetKey, setResetKey] = useState(0)
  const catalog = useMemo(() => loadCatalog(database), [database])
  const data = useMemo(() => loadYear(database, year), [database, year])
  const filtered = useMemo(() => data.countries.filter(row => !region || row.region === region), [data, region])
  const economy = useMemo(() => loadEconomy(database, year, region), [database, year, region])
  const comparison = selected.map((id, index) => ({
    id,
    name: catalog.find(row => row.id === id)?.name ?? id,
    color: COMPARE_COLORS[index],
    dash: ['', '8 4', '2 4'][index],
  }))
  const series = trendMode === 'world'
    ? [{ id: 'WORLD', name: 'Mundo', color: '#2d775d' }]
    : trendMode === 'regions' ? REGIONS.filter(item => !region || item.id === region) : comparison
  const firstYear = Math.min(start, year)
  const trends = useMemo(() => loadTrends(database, series.map(item => item.id), firstYear, year),
    [database, trendMode, region, selected, firstYear, year])
  const annualChanges = useMemo(() => loadAnnualChanges(database, firstYear, year), [database, firstYear, year])
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
    setYear(2023)
    setRegion('')
    setSelected([])
    setMetric('per_capita')
    setTrendMode('regions')
    setRankingMode('top')
    setStart(2010)
    setMessage('')
    setResetKey(value => value + 1)
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
          <CardHeading label="RANKING GLOBAL"
            title={rankingMode === 'top' ? 'Los 5 mayores emisores' : 'Mayores reducciones'}
            description={rankingMode === 'top' ? 'CO₂ territorial total por país' : year >= 2020 ? `${year - 10}–${year} · cambio relativo de CO₂` : 'Décadas completas disponibles desde 2020'}>
            <Segments options={[[ 'top', 'Top 5' ], [ 'reductions', 'Reducciones' ]]} value={rankingMode} onChange={setRankingMode} label="Vista del ranking" />
          </CardHeading>
          {rankingMode === 'top'
            ? <TopRanking rows={data.top} world={data.world} year={year} onSelect={choose} selected={selected} />
            : <ReductionRanking rows={data.reductions} eligibleCount={data.eligibleCount} year={year} onSelect={choose} selected={selected} />}
        </article>
      </div>
      {data.top[0] && perCapitaLeader && <aside className="insight"><span className="insight-icon"><Leaf size={20} /></span><div><strong>Dos formas de medir la huella en {year}</strong><p>{data.top[0].name} encabeza el volumen total con {tonnes(data.top[0].co2)}. {perCapitaLeader.name} registra el valor por persona más alto, con {number(perCapitaLeader.per_capita, 2)} t entre las entidades con datos.</p></div></aside>}
    </section>
    <section id="tendencias" className="page-section">
      <SectionHeading number="02" title="Tendencias y economía" description="Compara trayectorias y explora el vínculo entre actividad económica y CO₂." />
      <div className="analysis-grid">
        <article className="card chart-card trend-card">
          <CardHeading label="SERIE TEMPORAL" title={trendMode === 'annual' ? 'Cambio mundial anual' : 'Evolución de las emisiones'} description={`${firstYear}–${year} · ${trendMode === 'annual' ? 'Variación respecto al año anterior (%)' : 'CO₂ total en Mt'}`}>
            <Segments options={[[ 'world', 'Mundo' ], [ 'regions', 'Continentes' ], [ 'countries', 'Países' ], [ 'annual', 'Cambio %' ]]} value={trendMode} onChange={setTrendMode} label="Series del gráfico" />
          </CardHeading>
          <label className="trend-year">Desde <select aria-label="Inicio del intervalo" value={firstYear} onChange={event => setStart(Number(event.target.value))}>
            {YEARS.filter(value => value <= year).map(value => <option value={value} key={value}>{value}</option>)}
          </select><span>hasta {year}</span></label>
          {trendMode === 'annual'
            ? <AnnualChangeChart rows={annualChanges} />
            : <TrendChart key={`${trendMode}-${region}-${resetKey}`} rows={trends} series={series} start={firstYear} end={year} />}
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

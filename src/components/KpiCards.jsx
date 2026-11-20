import { Activity, ArrowDown, BarChart3, Globe2, TrendingDown } from 'lucide-react'
import { number, percent, tonnes, variation } from '../data'

function MetricCard({ icon: Icon, title, value, note, tag, tone, primary = false }) {
  return <article className={`card metric-card${primary ? ' metric-primary' : ''}`}>
    <div className="metric-top"><span className={`metric-icon ${tone || ''}`}><Icon size={19} /></span>{tag && <span className="metric-tag">{tag}</span>}</div>
    <h3>{title}</h3><strong className="metric-value">{value}</strong><p>{note}</p>
  </article>
}

export function Summary({ data, year }) {
  const annual = variation(data.world?.co2, data.world?.previous_co2)
  const leader = data.top[0]
  const improvement = data.improvement
  return <div className="metrics-grid">
    <MetricCard primary icon={Globe2} title="Emisiones mundiales" value={tonnes(data.world?.co2)} tag={`${year} · KPI principal`} note="CO₂ territorial · agregado mundial" />
    <MetricCard icon={annual < 0 ? ArrowDown : Activity} title="Variación mundial anual" value={percent(annual)} tone={annual > 0 ? 'warm' : ''} tag={year > 2010 ? `vs. ${year - 1}` : 'Inicio de serie'} note={annual == null ? 'Sin año previo en el periodo' : `${number(data.world.co2 - data.world.previous_co2, 1)} Mt de diferencia`} />
    <MetricCard icon={BarChart3} title="Mayor emisor" value={leader?.name ?? '—'} tag="GLOBAL" note={leader ? `${tonnes(leader.co2)} de CO₂ en ${year}` : 'Sin observaciones'} />
    <MetricCard icon={TrendingDown} title="Mayor reducción relativa" value={improvement?.name ?? '—'} tag={year >= 2020 ? `${year - 10}–${year}` : 'Década'} note={improvement ? `${percent(improvement.change)} · ${number(improvement.co2 - improvement.baseline_co2, 2)} Mt` : year < 2020 ? 'Disponible desde 2020' : 'Sin reducción entre los elegibles'} />
  </div>
}

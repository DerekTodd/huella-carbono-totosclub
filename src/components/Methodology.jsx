import { Activity, ArrowUpRight, BookOpen, Globe2, TrendingDown } from 'lucide-react'
import { SectionHeading } from './Shared'

const REPO = 'https://github.com/DerekTodd/huella-carbono-totosclub'
const SOURCE = 'https://github.com/owid/co2-data'
const REPORT = `${REPO}/blob/main/output/pdf/TotosClub_Fase1_Huella_de_Carbono.pdf`
const DESIGN = `${REPO}/blob/main/output/pdf/TotosClub_Fase2_Diseno_del_Dashboard.pdf`
const IMPLEMENTATION = `${REPO}/blob/main/output/pdf/TotosClub_Fase3_Implementacion_React.pdf`

export function Methodology({ year, eligibleCount, economyYear }) {
  return <section id="metodo" className="page-section">
    <SectionHeading number="04" title="Cómo leer los datos" description="Definiciones, alcance y procedencia de los indicadores." />
    <div className="method-grid">
      <article className="card method-card"><Globe2 size={22} /><h3>Emisiones territoriales</h3><p>CO₂ anual de combustibles fósiles y procesos industriales. Se excluye el cambio de uso de suelo. El agregado mundial proviene de la fuente y considera el transporte internacional.</p><p>La medida por persona divide el CO₂ total en toneladas entre la población del mismo año.</p></article>
      <article className="card method-card"><TrendingDown size={22} /><h3>Cambios y reducción</h3><p>Variación (%) = 100 × (emisiones finales ÷ emisiones iniciales − 1). La década termina en el año elegido y usa una base de diez años atrás.</p><p>Para la mayor reducción se exige una base de 1 Mt y once observaciones anuales. {year >= 2020 ? `${eligibleCount} países y territorios elegibles en ${year}.` : 'El indicador se habilita a partir de 2020.'}</p></article>
      <article className="card method-card"><Activity size={22} /><h3>Economía y cobertura</h3><p>El PIB está expresado en dólares internacionales de 2011 ajustados por PPA. La intensidad divide los kg de CO₂ entre el PIB del mismo año.</p><p>La dispersión usa pares positivos del {economyYear}. La correlación describe una asociación. Los valores ausentes se conservan como tales.</p></article>
    </div>
    <div className="sources card"><div className="sources-intro"><BookOpen size={21} /><div><strong>Fuentes y entrega</strong><p>Our World in Data, Global Carbon Budget y Maddison Project Database. Cartografía de Natural Earth y clasificación geográfica de World Countries.</p></div></div>
      <div className="source-links"><a href={SOURCE} target="_blank" rel="noreferrer">Fuente de datos <ArrowUpRight size={15} /></a><a href={REPORT} target="_blank" rel="noreferrer">Fase 1 <ArrowUpRight size={15} /></a><a href={DESIGN} target="_blank" rel="noreferrer">Fase 2 <ArrowUpRight size={15} /></a><a href={IMPLEMENTATION} target="_blank" rel="noreferrer">Fase 3 <ArrowUpRight size={15} /></a><a href={REPO} target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={15} /></a></div>
    </div>
  </section>
}

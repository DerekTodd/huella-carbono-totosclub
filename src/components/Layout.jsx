import { Globe2, Leaf } from 'lucide-react'

const SECTIONS = [ ['panorama', 'Panorama'], ['tendencias', 'Tendencias'], ['datos', 'Datos'], ['metodo', 'Metodología'] ]

export function Header({ anonymous = false }) {
  return <header className="site-header">
    <div className="shell header-inner">
      <a className="brand" href="#inicio" aria-label={anonymous ? 'Huella de carbono, inicio' : 'TotosClub, inicio'}><span className="brand-icon"><Leaf size={22} /></span>
        <span><strong>{anonymous ? 'Huella de carbono' : 'TotosClub'}</strong><small>OBSERVATORIO CLIMÁTICO</small></span></a>
      <nav aria-label="Secciones del dashboard">{SECTIONS.map(([id, label]) => <a key={id} href={`#${id}`}>{label}</a>)}</nav>
      <span className="header-period"><i /> DATOS 2010–2023</span>
    </div>
  </header>
}

export function Hero() {
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

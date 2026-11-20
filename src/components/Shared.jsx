export function CardHeading({ label, title, description, children, id }) {
  return <div className="card-heading">
    <div>{label && <span className="eyebrow">{label}</span>}<h3 id={id}>{title}</h3>{description && <p>{description}</p>}</div>
    {children}
  </div>
}

export function SectionHeading({ number: index, title, description }) {
  return <div className="section-heading"><span>{index}</span><div><h2>{title}</h2><p>{description}</p></div></div>
}

export function Segments({ options, value, onChange, label }) {
  return <div className="segments" role="group" aria-label={label}>{options.map(([id, name]) =>
    <button key={id} type="button" aria-pressed={value === id} onClick={() => onChange(id)}>{name}</button>)}</div>
}

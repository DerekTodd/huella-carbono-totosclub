import { BookOpen } from 'lucide-react'

const TERMS = [
  ['CO₂', 'Dióxido de carbono: gas de efecto invernadero que se emite, por ejemplo, al quemar carbón, petróleo o gas. Las cifras de este dashboard corresponden a este gas.'],
  ['t · Tonelada', 'Unidad de masa. Una tonelada equivale a 1,000 kilogramos. En las emisiones, indica la cantidad de CO₂ liberada durante un año.'],
  ['kg · Kilogramo', 'Unidad de masa: 1 kg equivale a 1,000 gramos. Se necesitan 1,000 kg para formar una tonelada.'],
  ['Mt · Megatonelada', 'Un millón de toneladas: 1 Mt = 1,000,000 t. Se usa para expresar las emisiones de un país sin escribir cifras tan largas.'],
  ['Gt · Gigatonelada', 'Mil millones de toneladas: 1 Gt = 1,000 Mt = 1,000,000,000 t. Se usa para cantidades grandes, como las emisiones mundiales.'],
  ['t por persona · Per cápita', 'Promedio anual: emisiones totales en toneladas divididas entre la población del mismo año. Es un promedio del país; las personas pueden tener huellas individuales diferentes.'],
  ['PIB · Producto Interno Bruto', 'Valor de los bienes y servicios finales producidos dentro de un país durante un año. Ayuda a describir el tamaño de su economía.'],
  ['PPA · Paridad de Poder Adquisitivo', 'Ajuste que toma en cuenta las diferencias de precios entre países. Permite comparar sus economías según lo que el dinero puede comprar en cada lugar.'],
  ['Dólar internacional de 2011 · $', 'Unidad usada para expresar el PIB con un poder de compra comparable entre países y con precios de 2011 como referencia. El símbolo $ del gráfico y de la tabla se refiere a esta unidad.'],
  ['kg CO₂/$ · Intensidad de carbono', 'Kilogramos de CO₂ emitidos por cada dólar internacional de PIB. Por ejemplo, 0.2 kg CO₂/$ equivale a 200 gramos de CO₂ por esa unidad de actividad económica.'],
  ['Mil millones y billones', 'En las cifras de PIB, mil millones son 1,000,000,000 y un billón es 1,000,000,000,000. Por ejemplo, $2 billones representan dos millones de millones de dólares internacionales.'],
  ['% · Porcentaje de cambio', 'Indica cuánto aumentaron o disminuyeron las emisiones respecto a un año de comparación. +10 % es un aumento de una décima parte; −10 % es una reducción de una décima parte.'],
  ['Cambio anual y decenal', 'Anual compara con el año anterior. Decenal compara con diez años atrás: por ejemplo, 2023 frente a 2013. El periodo de comparación aparece junto al indicador.'],
  ['KPI · Indicador clave de desempeño', 'Cifra que resume un aspecto importante del análisis. La tarjeta de emisiones mundiales es el KPI principal de este dashboard.'],
  ['Escala logarítmica · log₁₀', 'Avanza por factores de diez, como 10, 100 y 1,000. Permite comparar países cuyos valores de PIB o emisiones tienen tamaños muy diferentes.'],
  ['r de Pearson · Correlación', 'Mide una asociación lineal entre −1 y +1: los valores positivos indican que las variables tienden a aumentar juntas. Aquí se calcula sobre log₁₀ de PIB y CO₂. Una asociación no demuestra que una variable cause la otra.'],
  ['Pares de datos', 'Cada par reúne el PIB y las emisiones de CO₂ de un mismo país y año. El número de pares indica cuántos países cuentan con ambos datos para la dispersión.'],
  ['ISO3 · Código de país', 'Identificador de tres letras, como MEX para México o USA para Estados Unidos. Puedes usarlo para buscar un país en la tabla.'],
  ['CSV · Valores separados por comas', 'Formato de archivo que guarda una tabla y se puede abrir en Excel u otras herramientas. Descargar CSV exporta los datos del año, la región y la búsqueda que tengas seleccionados.'],
  ['— · Sin datos', 'Significa que la fuente no tiene un valor disponible. Es diferente de cero: cero sí es una cantidad conocida.'],
]

export function Glossary() {
  return <article className="card glossary" id="glosario" aria-labelledby="glossary-title">
    <div className="glossary-heading"><BookOpen size={23} aria-hidden="true" /><div>
      <h3 id="glossary-title">Siglas y unidades, en palabras sencillas</h3>
      <p>Una guía para entender las etiquetas de las tarjetas, el mapa, los gráficos y la tabla. Usamos Gt, Mt, t y kg como símbolos de las unidades.</p>
    </div></div>
    <dl className="glossary-grid">{TERMS.map(([term, meaning]) => <div key={term}>
      <dt>{term}</dt><dd>{meaning}</dd>
    </div>)}</dl>
    <div className="glossary-example"><strong>Un ejemplo para distinguir total y promedio</strong>
      <p>Si un país emite 10 Mt de CO₂ en un año y tiene 1,000,000 de habitantes, su promedio es de 10 t por persona. El total describe cuánto emite el país; el promedio ayuda a comparar países con poblaciones diferentes.</p>
    </div>
  </article>
}

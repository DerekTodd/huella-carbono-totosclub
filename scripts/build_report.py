"""Genera PDF y fuente Markdown desde un mismo contenido de Fase 1."""
import html
import json
import re
from pathlib import Path

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                               PageBreak, Flowable, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT / 'data/processed/quality_report.json').read_text(encoding='utf-8'))
OUT = ROOT / 'output/pdf/TotosClub_Fase1_Huella_de_Carbono.pdf'
TEAM = 'TotosClub'
AUTHOR = 'Derek Todd López'
INK = colors.HexColor('#153B3A')
GREEN = colors.HexColor('#147D68')
MUTED = colors.HexColor('#536A6A')
LIGHT = colors.HexColor('#EDF5F1')
RULE = colors.HexColor('#CADCD5')
GOLD = colors.HexColor('#E5A94F')
fonts = Path(reportlab.__file__).parent / 'fonts'
for name, filename in [('Body', 'Vera.ttf'), ('Bold', 'VeraBd.ttf'), ('Italic', 'VeraIt.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Italic', boldItalic='Bold')


def n(value):
    return f'{value:,}'.replace(',', ' ')


def p(text): return ('p', text)
def h(text): return ('h', text)
def bullet(text): return ('b', text)
def table(headers, rows, widths=None): return ('t', headers, rows, widths)
def note(title, text): return ('note', title, text)


coverage = REPORT['coverage_by_year']
years_with_gdp = [r['year'] for r in coverage if r['gdp_co2_pairs']]
latest_gdp = max(years_with_gdp)
flags = REPORT['issue_counts']
top = REPORT['top5_2023_preview']
winner = REPORT['largest_relative_reduction_2013_2023_preview'][0]
pages = [
('Propósito del proyecto', [
    note('Pregunta central', '¿Cómo cambia la comparación entre países cuando se observan sus emisiones totales, por persona y en relación con su economía?'),
    p('El proyecto propone un dashboard en React para explorar emisiones territoriales de CO₂, población y actividad económica entre 2010 y 2023. La Fase 1 establece qué preguntas responder, qué datos utilizar y qué reglas aplicar antes de construir la aplicación.'),
    h('Ficha de entrega'),
    table(['Elemento', 'Definición'], [
        ['Equipo', TEAM], ['Integrante', AUTHOR], ['Tema', 'Medio ambiente y sostenibilidad'],
        ['Tipo elegido', 'Dashboard estratégico'], ['Cobertura temporal', '2010-2023, ambos años incluidos'],
        ['Fecha de consulta y entrega', '4 de noviembre de 2026'],
        ['Tecnologías previstas', 'React + API de lectura + PostgreSQL'],
    ], [0.31, 0.69]),
    h('Alcance de esta fase'),
    p('Se realizó el análisis de requisitos, se descargó y perfiló la fuente, se aplicó una limpieza inicial reproducible y se definieron métricas, visualizaciones y un modelo de datos. Se entregan el documento, el README y los archivos de preparación del repositorio.'),
    p('El desarrollo de React, la ejecución del esquema en PostgreSQL, la API y el despliegue corresponden a las fases siguientes. La Fase 1 se entrega en el repositorio público https://github.com/DerekTodd/huella-carbono-totosclub. La aplicación web aún no está desplegada.'),
    note('Criterio de lectura', '“Huella de carbono” es el título del proyecto. El indicador base mide CO₂ territorial anual: no representa por sí solo toda la huella de consumo, todos los gases de efecto invernadero ni la responsabilidad histórica acumulada.'),
]),
('Audiencia y objetivos', [
    h('Problema que resuelve'),
    p('Una clasificación basada únicamente en emisiones totales puede confundir el tamaño de una población o economía con su intensidad de contaminación. El dashboard reunirá varias perspectivas y sus límites para facilitar comparaciones comprensibles y verificables.'),
    table(['Audiencia', 'Decisiones o usos', 'Detalle requerido'], [
        ['Estudiantes y docentes', 'Elegir casos de estudio y argumentar diferencias entre países.', 'Resumen, definiciones, comparaciones y datos por año.'],
        ['Analistas y organizaciones ambientales', 'Priorizar países para investigación y observar trayectorias.', 'Series por país, indicadores normalizados y cobertura.'],
        ['Responsables de sostenibilidad', 'Comparar tendencias y orientar preguntas de política a largo plazo.', 'KPIs, variaciones, contexto económico y acceso al detalle.'],
    ], [0.23, 0.39, 0.38]),
    p('Se asume un nivel estadístico básico o intermedio. La interfaz ofrecerá una vista general y permitirá profundizar mediante filtros, tooltips y una tabla descargable. No se presupone experiencia con bases de datos.'),
    h('Objetivo general'),
    note('Objetivo', 'Facilitar la comparación de las emisiones territoriales de CO₂ de países y territorios entre 2010 y 2023, mediante indicadores totales, per cápita y económicos, para identificar diferencias y tendencias relevantes para la sostenibilidad.'),
    h('Objetivos específicos verificables'),
    bullet('Identificar los cinco mayores emisores con datos del año seleccionado y mostrar su volumen en Mt.'),
    bullet('Comparar la evolución anual y el cambio entre 2013 y 2023, diferenciando aumentos y reducciones.'),
    bullet('Relacionar PIB y CO₂ exclusivamente en observaciones del mismo año con datos de ambas variables.'),
    bullet('Permitir comparar al menos dos países y consultar los seis continentes con una definición regional consistente.'),
    bullet('Mostrar fuente, unidad, año, cobertura y significado de cada indicador para que el usuario pueda verificarlo.'),
    p('La validación de comprensión con usuarios se realizará al disponer del prototipo; en esta fase la caracterización de audiencia deriva de la consigna y del uso previsto, no de entrevistas realizadas.'),
]),
('Fuente, alcance y variables', [
    p('La visualización facilitada [1] sirve como referencia conceptual. Para incorporar población y PIB se utiliza el CSV completo de Our World in Data [2], junto con su diccionario [3]. Los datos de CO₂ proceden de Global Carbon Budget; el PIB se basa en Maddison Project Database. Cada registro representa una entidad geográfica y un año.'),
    table(['Variable', 'Significado y formato', 'Uso'], [
        ['country / iso_code', 'Nombre y código geográfico de texto.', 'Identificación y unión con el mapa.'],
        ['year', 'Año entero; se conserva 2010-2023.', 'Filtros y comparación temporal.'],
        ['co2', 'Emisiones anuales; número en Mt de CO₂.', 'Rankings y tendencias.'],
        ['population', 'Población; personas.', 'Denominador per cápita.'],
        ['gdp', 'PIB real en dólares internacionales de 2011, ajustado por PPA.', 'Dispersión e intensidad económica.'],
        ['co2_per_capita', 'Indicador publicado en t por persona.', 'Contraste con el recálculo.'],
        ['co2_per_gdp', 'Indicador publicado en kg por dólar internacional.', 'Contraste y documentación.'],
        ['coal_co2, oil_co2, gas_co2 y otros', 'Desglose por combustible/proceso, en Mt.', 'Exploración complementaria condicionada a cobertura.'],
    ], [0.23, 0.47, 0.30]),
    h('Delimitación geográfica'),
    p('Los rankings utilizan entidades con código de tres letras mayúsculas: se describen como países y territorios, sin afirmar que todas sean Estados soberanos. Se excluyen del ranking World, continentes, grupos de ingresos y agregados superpuestos. Kosovo queda fuera de este universo por tener un código especial OWID; esta limitación debe mostrarse.'),
    p('Las series continentales conservarán únicamente Africa, Asia, Europe, North America, South America y Oceania del proveedor. World se mantiene separado. No se mezclarán con grupos alternativos como Europe (GCP) o la Unión Europea.'),
    note('Comparabilidad', 'En la gráfica web de referencia las emisiones se muestran en toneladas; en el CSV completo co2 está en Mt. El periodo 2010-2023 es una decisión del proyecto, aunque la fuente publique años posteriores. El transporte internacional no se asigna a países; por ello la suma de países no equivale automáticamente al total mundial [1].'),
]),
('Perfilado y limpieza aplicados', [
    p('Se ejecutó scripts/preprocess.py sobre una instantánea real de la descarga oficial. El script conserva el archivo original local, verifica columnas y genera dos tablas depuradas, un registro de banderas y un informe JSON. Los siguientes resultados son del procesamiento realizado, no una simulación.'),
    table(['Comprobación', 'Resultado observado'], [
        ['Archivo de origen', f"{n(REPORT['input_rows'])} filas; {REPORT['input_columns']} columnas; {n(REPORT['source_bytes'])} bytes."],
        ['Filas 2010-2023, todas las entidades', n(REPORT['rows_2010_2023_all_entities'])],
        ['Universo de países/territorios', f"{REPORT['country_entities']} entidades; {n(REPORT['country_rows'])} filas."],
        ['Continentes y World, por separado', f"{REPORT['regional_rows']} filas: 7 entidades × 14 años."],
        ['Duplicados exactos / conflictivos', f"{REPORT['exact_duplicates_removed']} / {REPORT['conflicting_duplicates']}"],
        ['Filas en cuarentena por CO₂ inválido', str(REPORT['quarantined_rows'])],
    ], [0.54, 0.46]),
    h('Cobertura de variables principales'),
    table(['Periodo', 'Filas/año', 'CO₂', 'Población', 'PIB y CO₂'], [
        ['2010-2022', '218', '215', '216', '164'],
        ['2023', '218', '215', '216', '0'],
    ], [0.24, 0.19, 0.16, 0.19, 0.22]),
    p('Los conteos anteriores corresponden a países/territorios con valores disponibles en cada año. En 2023 faltan emisiones para Monaco, San Marino y Vatican; faltan poblaciones para Antarctica y Christmas Island. Estas ausencias no se sustituyeron por cero.'),
    note('Decisión derivada del perfilado', f'El último año con pares PIB-CO₂ es {latest_gdp}, con 164 entidades. En 2023 el gráfico económico debe mostrar “Sin datos de PIB para este año” o permitir elegir 2022 de forma explícita. No se asociará el PIB de 2022 con emisiones de 2023.'),
    h('Trazabilidad'),
    p('El informe data/processed/quality_report.json registra URL, tamaño, fecha de procesamiento y SHA-256 del CSV y del diccionario. La huella identifica exactamente los archivos utilizados; no implica que la URL mutable conserve esa versión en el futuro.'),
    p('Se retienen 3 052 registros de países/territorios, incluidos los que tienen alguna variable ausente. El conjunto utilizable por cada gráfico se define por sus variables necesarias, no eliminando indiscriminadamente filas incompletas.'),
]),
('Reglas de calidad y valores atípicos', [
    table(['Situación', 'Regla aplicada o decisión prevista', 'Justificación'], [
        ['Faltantes', 'Cadena vacía pasa a nulo. Se excluye solo del cálculo que requiera ese valor.', 'Distinguir falta de medición de una emisión igual a cero.'],
        ['Tipos y dominio', 'Año entero; valores finitos; CO₂ no negativo; población y PIB positivos.', 'Evitar unidades inválidas y divisiones sin sentido.'],
        ['Duplicados', 'Eliminar copias idénticas; detener el proceso ante claves conflictivas.', 'No elegir arbitrariamente entre dos mediciones.'],
        ['Dato inválido', 'CO₂ inválido: fila a cuarentena. Otros campos inválidos: nulo y evento de calidad.', 'Conservar evidencia y evitar contaminar métricas.'],
        ['Uniones geográficas', 'Clave ISO3 para países; agregados en conjunto separado.', 'Evitar doble conteo y pérdidas silenciosas.'],
    ], [0.18, 0.48, 0.34]),
    h('Atípicos: detectar, revisar y conservar'),
    p('Por cada año se calculan Q1 y Q3 de CO₂ total y CO₂ per cápita entre países/territorios. Se marcan valores fuera de [Q1 - 1,5 × RIQ, Q3 + 1,5 × RIQ], donde RIQ = Q3 - Q1. También se marca un cambio interanual absoluto superior a 30 %, con años consecutivos y base positiva. Son umbrales de revisión del equipo, no reglas universales de error.'),
    p('La asimetría internacional hace esperables países con emisiones muy altas. Las marcas no producen eliminación ni ajuste automático. Solo se corregirá un valor al confirmar un error con la fuente; se registrarán valor previo, motivo y decisión. Para facilitar lectura se podrán usar escalas logarítmicas sin modificar los datos.'),
    table(['Bandera generada', 'Número de eventos'], [
        ['Fuera del intervalo RIQ; se conserva', str(flags.get('iqr_review_keep', 0))],
        ['Cambio interanual > 30 %; se conserva', str(flags.get('annual_change_gt_30_review_keep', 0))],
        ['Discrepancia entre per cápita publicado y recalculado', str(flags.get('derived_discrepancy', 0))],
    ], [0.79, 0.21]),
    p('Un evento no equivale a una fila distinta: una observación puede activar varias reglas. Las 28 discrepancias per cápita se concentran en North America y Oceania durante 14 años; su causa queda pendiente de revisión. Se conservan ambos valores y no se utilizará el per cápita regional en esta versión. Las series continentales utilizarán CO₂ total.'),
    p('El contraste per cápita admite una tolerancia de máx(0,005; 500/población + 0,0005) t/persona para diferencias de precisión. La revisión de cada bandera y la comparación exacta con las fuentes quedan registradas como actividad posterior, sin afirmar que ya se hayan resuelto.'),
]),
('Métricas y KPIs reproducibles', [
    p('Sea E(c,t) el CO₂ territorial del país/territorio c en el año t, medido en Mt; P su población y G su PIB en dólares internacionales de 2011. Los nulos se muestran como “Sin datos” y los cocientes requieren denominadores positivos. Se calcula con la precisión disponible y se redondea solo al presentar.'),
    table(['Indicador', 'Definición y criterio de lectura'], [
        ['Emisiones per cápita', 'E × 1 000 000 / P; unidad: t CO₂/persona. Permite comparar poblaciones de distinto tamaño.'],
        ['Variación en una década', '100 × (E(c,2023) / E(c,2013) - 1). Los extremos están separados por diez años. 2010-2023 es un cambio de 13 años y se etiquetará como tal.'],
        ['Aumento o reducción anual', '100 × (E(c,t) / E(c,t-1) - 1). Mostrar además E(c,t) - E(c,t-1) en Mt. Exigir años consecutivos.'],
        ['Intensidad de carbono del PIB', 'E × 1 000 000 000 / G; unidad: kg CO₂ por dólar internacional de 2011. Menor intensidad no garantiza menores emisiones totales.'],
        ['Top 5 emisores', 'Orden descendente de E en el año seleccionado, solo países/territorios con E válido. Empates: código ascendente. El Top 5 global no cambia al filtrar un continente; el ranking regional se etiqueta aparte.'],
        ['Mayor reducción relativa', 'Menor variación 2013-2023, exigiendo E(2013) ≥ 1 Mt y cobertura anual completa 2013-2023. Mostrar también reducción en Mt, universo elegible y periodo.'],
    ], [0.26, 0.74]),
    note('Cómo interpretar “mejora ambiental”', 'Se operacionaliza únicamente como mayor reducción relativa de CO₂ territorial. El umbral de 1 Mt limita efectos de bases diminutas y excluye ciertos territorios; debe publicarse. Una reducción puede responder a recesiones, cierres industriales, conflictos o cambios productivos; no demuestra por sí misma una mejor política ambiental.'),
    h('Comprobación inicial del cálculo, no conclusión definitiva'),
    p('En 2023, el orden obtenido es China, Estados Unidos, India, Rusia y Japón. Con la regla de reducción definida, Curacao (CUW) registra aproximadamente -62,83 % entre 2013 y 2023. Son resultados preliminares del universo de países/territorios y requieren contexto antes de atribuir causas.'),
    p('La relación PIB-CO₂ se explorará con pares del mismo año; una correlación será descriptiva y no causal. Si se calcula Pearson se hará sobre log10(PIB) y log10(CO₂), con ambos valores positivos, informando año y número de pares. No se mezclarán observaciones de varios años como si fueran independientes.'),
]),
('Tipo de dashboard y visualizaciones', [
    h('Justificación del tipo estratégico'),
    p('Se selecciona un dashboard estratégico por su horizonte multianual, sus datos anuales y su finalidad de comparar trayectorias de largo plazo. Permitirá reflexionar sobre sostenibilidad y orientar prioridades de análisis. Aunque también será útil en contextos educativos, su clasificación depende del horizonte y de las decisiones que apoya.'),
    p('Un dashboard operativo requeriría seguimiento frecuente de procesos y decisiones cotidianas; la actualización anual de esta fuente no responde a ese uso. Un dashboard táctico se centraría en metas y acciones de una organización a medio plazo, que no constituyen el foco de este proyecto.'),
    table(['Vista propuesta', 'Pregunta y codificación', 'Reglas y límites'], [
        ['Mapa coroplético mundial', '¿Dónde es mayor el CO₂ por persona? Color secuencial en t/persona.', 'Mismo año; nulos en gris; leyenda explícita y tooltip con total y población. Unir geometrías por código geográfico.'],
        ['Líneas por continente', '¿Cómo cambian las emisiones? Año en X, CO₂ total en Mt en Y.', 'Seis series regionales oficiales; no añadir World a la suma. No unir huecos como si hubiera mediciones.'],
        ['Dispersión PIB vs. CO₂', '¿Cómo se relacionan tamaño económico y emisiones? PIB en X, CO₂ en Y.', 'Pares del mismo año, hasta 2022; escalas logarítmicas etiquetadas y tabla accesible. Informar n y exclusiones.'],
        ['Barras horizontales Top 5', '¿Qué países/territorios emiten más? Longitud proporcional a Mt.', 'Año y universo visibles; eje desde cero. Se acompaña de tarjetas KPI.'],
        ['Barras apiladas, opcionales', '¿Qué combustibles o procesos aportan emisiones?', 'No hay columnas sectoriales en la instantánea. Solo usar carbón, petróleo, gas, cemento y otros componentes si son completos y reconciliables.'],
    ], [0.22, 0.37, 0.41]),
    p('El desglose por transporte, agricultura o industria requeriría otra fuente y una nueva evaluación de compatibilidad. No se prometerá ese gráfico sectorial con los datos actuales. Para el desglose por combustible/proceso se verificará la suma contra el total y se mostrarán las diferencias de cobertura; queda fuera del alcance mínimo.'),
    h('Interacción y accesibilidad'),
    p('Filtros de año, intervalo temporal y países; selector de continente para vistas compatibles; restablecimiento y descarga de la tabla filtrada. Año inicial: 2023 para emisiones; el gráfico económico pedirá elegir 2022 explícitamente. Incluir navegación por teclado, etiquetas, unidades y tabla alternativa; no depender solo del color para distinguir aumentos y reducciones.'),
]),
('Integración y diseño de base de datos', [
    p('Se elige PostgreSQL porque los datos se organizan naturalmente por entidad y año, requieren relaciones consistentes y consultas de agregación. Las claves, restricciones y transacciones permiten evitar duplicados y publicar lotes validados [4]. El SQL adjunto es un diseño para la siguiente fase; no constituye evidencia de un servidor ya implementado.'),
    ('pipeline',),
    table(['Tabla prevista', 'Contenido y controles'], [
        ['ingestion_runs', 'URL, SHA-256 de CSV y diccionario, fecha de descarga, versión de reglas y lote activo. Una sola instantánea activa.'],
        ['locations', 'Código único, nombre, tipo country/region/world e ISO3 opcional. Los agregados no tienen ISO3 de país.'],
        ['annual_observations', 'CO₂, población, PIB e indicadores fuente por lote, entidad y año. Clave primaria compuesta; controles de dominio.'],
        ['quality_events', 'Entidad, variable, regla, valor original, estado de revisión y motivo de decisión.'],
        ['active_metrics, vista', 'Cálculos per cápita y por PIB sobre el lote activo. Separación explícita del tipo de entidad.'],
    ], [0.28, 0.72]),
    h('Proceso de carga previsto'),
    bullet('Descargar y conservar originales; registrar fecha, tamaño, hash y diccionario antes de transformar.'),
    bullet('Validar y producir CSV separados. En staging, mapear co2 a co2_mt, gdp a gdp_ppp_2011 y vacíos a NULL. Conservar cifras originales de indicadores publicados.'),
    bullet('Crear o reutilizar el catálogo: ISO3 como entity_code para países; códigos estables REG_AFRICA, REG_ASIA y equivalentes para regiones, y WORLD para el mundo.'),
    bullet('Dentro de una transacción, insertar el nuevo lote, las observaciones y los eventos. Verificar claves, dominios, conteos y muestras de indicadores contra el informe.'),
    bullet('Desactivar el lote anterior y activar el validado al final de la transacción. Ante error, rollback. Conservar el lote previo para trazabilidad y reversión.'),
    h('Consulta y publicación de la aplicación'),
    p('React consultará una API de solo lectura con filtros validados de año y entidad. Se prevén endpoints /countries, /metrics, /rankings y /timeseries. Las credenciales de PostgreSQL estarán en el servidor, con un usuario limitado a lectura para la API. No se incluirán en el repositorio público.'),
    p('Se plantea publicar el frontend en GitHub Pages [5]; la API y PostgreSQL se alojarán aparte. Pages sirve contenido estático y no ejecuta PostgreSQL. La selección concreta de alojamiento y los conectores se resolverán en la fase de implementación, manteniendo React como frontend [6].'),
]),
('Repositorio, plan y aceptación', [
    h('Repositorio público'),
    p('Repositorio público: https://github.com/DerekTodd/huella-carbono-totosclub. El README incluye el equipo TotosClub, el único integrante Derek Todd López y la descripción del proyecto. La rama principal main contiene el PDF, la fuente editable, los datos preparados y los scripts de la Fase 1.'),
    table(['Ruta entregada', 'Propósito'], [
        ['README.md', 'Identidad del equipo, alcance, fuentes y reproducción.'],
        ['docs/fase-1.md y output/pdf/', 'Fuente editable y documento de justificación.'],
        ['scripts/preprocess.py', 'Limpieza y perfilado reproducibles.'],
        ['data/processed/', 'Datos preparados, cobertura, banderas y cuarentena.'],
        ['db/schema.sql', 'Diseño relacional para PostgreSQL.'],
        ['scripts/build_report.py', 'Regeneración del PDF y del texto editable.'],
    ], [0.45, 0.55]),
    h('Plan por fases y responsabilidad'),
    p('Derek Todd López asume todas las funciones. Usará issues para requisitos y problemas de calidad, ramas para cambios y pull requests para registrar revisión y evidencia, aun siendo el único integrante.'),
    bullet('Fase 1: análisis, perfilado, reglas, documento y publicación de los entregables en el repositorio público.'),
    bullet('Fase 2: ejecutar esquema y carga transaccional; revisar las discrepancias; implementar API y componentes React.'),
    bullet('Fase 3: integrar mapa y gráficos, validar filtros y accesibilidad, probar con usuarios y publicar la aplicación.'),
    h('Criterios de aceptación'),
    table(['Criterio', 'Evidencia / estado'], [
        ['Audiencia, objetivo, datos y tipo justificados', 'Documentados en esta entrega.'],
        ['Limpieza aplicada y reproducible', 'CSV, flags y JSON generados desde la fuente real.'],
        ['Repositorio público accesible sin sesión', 'Repositorio público de entrega enlazado en esta página.'],
        ['README con equipo e integrante', 'Publicado con los datos solicitados.'],
        ['Persistencia y dashboard web', 'Previstos para fases posteriores; sin implementación ni URL aún.'],
    ], [0.55, 0.45]),
    p('La entrega permite consultar el README y descargar el PDF desde el repositorio público. En las fases siguientes se comprobarán tres países contra la fuente, años extremos, divisiones por cero, faltantes y separación de agregados. El PIB ausente de 2023 se conservará como nulo.'),
]),
('Conclusiones, límites y referencias', [
    h('Conclusión de la Fase 1'),
    p('El análisis define un dashboard estratégico viable para estudiar diferencias y trayectorias de CO₂ territorial entre países y territorios. La limpieza inicial confirma que el periodo 2010-2023 es utilizable para emisiones, mientras que el análisis económico debe limitarse a años con PIB disponible, hasta 2022 en esta instantánea.'),
    p('La comparación combinará valores absolutos y normalizados: un gran volumen total no implica necesariamente el mayor valor por persona. La fase siguiente deberá probar cómo se relacionan población, economía y emisiones; no se adelantan conclusiones causales a partir de una clasificación o una correlación.'),
    h('Límites que acompañarán al dashboard'),
    bullet('Cobertura incompleta, código especial de Kosovo fuera del universo ISO3 y diferencias entre países y territorios.'),
    bullet('CO₂ territorial sin cambio de uso del suelo; no incluye todos los gases ni ajusta por importaciones. No mide por sí solo responsabilidad histórica o ambiental total.'),
    bullet('PIB y CO₂ pueden revisarse; el conjunto se actualiza y cada publicación debe conservar su instantánea y reglas.'),
    bullet('Las 28 discrepancias regionales siguen pendientes de revisión. La serie de CO₂ total continental puede construirse sin usar esos cocientes per cápita.'),
    h('Referencias consultadas el 4 de noviembre de 2026'),
    p('[1] Our World in Data. Annual CO₂ emissions. Emisiones territoriales, unidades y alcance. https://ourworldindata.org/grapher/annual-co2-emissions-per-country'),
    p('[2] Our World in Data. CO₂ and Greenhouse Gas Emissions dataset. CSV, procedencia, metodología y atribución. https://github.com/owid/co2-data'),
    p('[3] Our World in Data. Diccionario de variables owid-co2-codebook.csv. Incluye Global Carbon Budget (2025), población y Maddison Project Database 2023. https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv'),
    p('[4] PostgreSQL. Constraints. https://www.postgresql.org/docs/current/ddl-constraints.html'),
    p('[5] GitHub Docs. What is GitHub Pages? https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages'),
    p('[6] React. Quick Start. https://react.dev/learn'),
    note('Atribución y conservación', 'Se atribuyen los datos a Our World in Data y sus proveedores originales. La reutilización de datos de terceros depende de sus condiciones originales; no se les aplica automáticamente una licencia nueva del proyecto. Los hashes completos están en el informe de calidad.'),
]),
]


def markup(text):
    text = html.escape(text)
    text = text.replace('₂', '<sub>2</sub>')
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(https://[^\s]+)', r'<link href="\1" color="#147D68">\1</link>', text)
    return text


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyTextCustom', fontName='Body', fontSize=9.2, leading=13.7,
                          textColor=INK, spaceAfter=8, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='SectionCustom', fontName='Bold', fontSize=23, leading=28,
                          textColor=INK, spaceAfter=16))
styles.add(ParagraphStyle(name='SubCustom', fontName='Bold', fontSize=11.2, leading=15,
                          textColor=GREEN, spaceBefore=9, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle(name='CellCustom', fontName='Body', fontSize=8.25, leading=11.8,
                          textColor=INK, spaceAfter=0))
styles.add(ParagraphStyle(name='CellHeadCustom', parent=styles['CellCustom'], fontName='Bold',
                          textColor=colors.white))
styles.add(ParagraphStyle(name='BulletCustom', parent=styles['BodyTextCustom'],
                          leftIndent=11, firstLineIndent=-9, spaceAfter=5))
styles.add(ParagraphStyle(name='NoteCustom', parent=styles['BodyTextCustom'], fontSize=8.7, leading=12.8,
                          spaceAfter=0))


class Pipeline(Flowable):
    def __init__(self, width):
        Flowable.__init__(self)
        self.width, self.height = width, 59

    def draw(self):
        c = self.canv
        labels = ['OWID CSV', 'Python / calidad', 'PostgreSQL', 'API / React']
        gap = 14
        width = (self.width - 3 * gap) / 4
        for i, label in enumerate(labels):
            x = i * (width + gap)
            c.setFillColor(LIGHT)
            c.setStrokeColor(RULE)
            c.roundRect(x, 17, width, 30, 5, stroke=1, fill=1)
            c.setFillColor(INK)
            c.setFont('Bold', 8)
            c.drawCentredString(x + width / 2, 29, label)
            if i < 3:
                c.setStrokeColor(GREEN)
                c.line(x + width + 2, 32, x + width + gap - 2, 32)
                c.line(x + width + gap - 5, 35, x + width + gap - 2, 32)
                c.line(x + width + gap - 5, 29, x + width + gap - 2, 32)


def draw_page(canvas, doc):
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(GREEN)
    canvas.rect(0, height - 9, width, 9, fill=1, stroke=0)
    canvas.setFont('Bold', 8)
    canvas.setFillColor(GREEN)
    canvas.drawString(doc.leftMargin, height - 31, 'TOTOSCLUB  /  HUELLA DE CARBONO')
    canvas.setFont('Body', 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - doc.rightMargin, height - 31, 'FASE 1 · ANÁLISIS')
    canvas.setStrokeColor(RULE)
    canvas.line(doc.leftMargin, 37, width - doc.rightMargin, 37)
    canvas.setFont('Body', 7.5)
    canvas.drawString(doc.leftMargin, 24, f'{AUTHOR}  |  4 de noviembre de 2026')
    canvas.drawRightString(width - doc.rightMargin, 24, f'{doc.page} / {len(pages)}')
    canvas.restoreState()


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / 'docs').mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=20 * mm, bottomMargin=19 * mm,
                            title='Huella de carbono: ¿quién contamina más? | Fase 1',
                            author=f'{TEAM} - {AUTHOR}', subject='Documento de justificación y análisis')
    story, md = [], ['# Huella de carbono: ¿quién contamina más?\n',
                     f'**Equipo:** {TEAM}  \n**Integrante:** {AUTHOR}  \n**Fase:** 1 - Análisis  \n**Fecha:** 4 de noviembre de 2026\n']
    for index, (title, blocks) in enumerate(pages):
        if index:
            story.append(PageBreak())
        story.append(Paragraph(f'{index + 1:02d}', styles['SubCustom']))
        story.append(Paragraph(markup(title), styles['SectionCustom']))
        if index == 0:
            story.append(Paragraph('Huella de carbono:<br/>¿quién contamina más?',
                                    ParagraphStyle('CoverTitle', fontName='Bold', fontSize=27,
                                                   leading=32, textColor=GREEN, spaceAfter=15)))
        md.append(f'\n## {index + 1}. {title}\n')
        for block in blocks:
            kind = block[0]
            if kind in {'p', 'h', 'b'}:
                style = {'p': 'BodyTextCustom', 'h': 'SubCustom', 'b': 'BulletCustom'}[kind]
                text = ('• ' if kind == 'b' else '') + block[1]
                story.append(Paragraph(markup(text), styles[style]))
                md.append(('### ' if kind == 'h' else '- ' if kind == 'b' else '') + block[1] + '\n')
            elif kind == 'note':
                content = Paragraph('<b>' + markup(block[1]) + '</b><br/>' + markup(block[2]), styles['NoteCustom'])
                box = Table([[content]], colWidths=[doc.width], hAlign='LEFT')
                box.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT),
                                        ('LINEBEFORE', (0, 0), (0, 0), 3, GREEN),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 11),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 11),
                                        ('TOPPADDING', (0, 0), (-1, -1), 9),
                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 9)]))
                story.extend([box, Spacer(1, 9)])
                md.append('**' + block[1] + ':** ' + block[2] + '\n')
            elif kind == 't':
                headers, rows, widths = block[1:]
                count = len(headers)
                widths = widths or [1 / count] * count
                cells = [[Paragraph(markup(x), styles['CellHeadCustom']) for x in headers]]
                cells += [[Paragraph(markup(str(x)), styles['CellCustom']) for x in row] for row in rows]
                item = Table(cells, colWidths=[doc.width * w for w in widths], repeatRows=1, hAlign='LEFT')
                item.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), INK),
                                         ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
                                         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                         ('LEFTPADDING', (0, 0), (-1, -1), 7),
                                         ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                                         ('TOPPADDING', (0, 0), (-1, -1), 6),
                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                         ('LINEBELOW', (0, -1), (-1, -1), 0.5, RULE)]))
                story.extend([item, Spacer(1, 9)])
                md.append('| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join(['---'] * count) + ' |\n')
                md.append('\n'.join('| ' + ' | '.join(str(c) for c in row) + ' |' for row in rows) + '\n')
            elif kind == 'pipeline':
                story.append(Pipeline(doc.width))
                md.append('```text\nOWID CSV -> Python / calidad -> PostgreSQL -> API / React\n```\n')
    (ROOT / 'docs/fase-1.md').write_text('\n'.join(md), encoding='utf-8')
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    if doc.page != len(pages):
        raise ValueError(f'Desbordamiento de diseño: {doc.page} páginas; se esperaban {len(pages)}.')
    print(OUT)


if __name__ == '__main__':
    main()

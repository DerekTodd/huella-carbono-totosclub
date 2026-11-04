# Huella de carbono: ¿quién contamina más?

**Equipo:** TotosClub  
**Integrante:** Derek Todd López  
**Fase:** 1 - Análisis  
**Fecha:** 4 de noviembre de 2026


## 1. Propósito del proyecto

**Pregunta central:** ¿Cómo cambia la comparación entre países cuando se observan sus emisiones totales, por persona y en relación con su economía?

El proyecto propone un dashboard en React para explorar emisiones territoriales de CO₂, población y actividad económica entre 2010 y 2023. La Fase 1 establece qué preguntas responder, qué datos utilizar y qué reglas aplicar antes de construir la aplicación.

### Ficha de entrega

| Elemento | Definición |
| --- | --- |

| Equipo | TotosClub |
| Integrante | Derek Todd López |
| Tema | Medio ambiente y sostenibilidad |
| Tipo elegido | Dashboard estratégico |
| Cobertura temporal | 2010-2023, ambos años incluidos |
| Fecha de consulta y entrega | 4 de noviembre de 2026 |
| Tecnologías previstas | React + API de lectura + PostgreSQL |

### Alcance de esta fase

Se realizó el análisis de requisitos, se descargó y perfiló la fuente, se aplicó una limpieza inicial reproducible y se definieron métricas, visualizaciones y un modelo de datos. Se entregan el documento, el README y los archivos de preparación del repositorio.

El desarrollo de React, la ejecución del esquema en PostgreSQL, la API y el despliegue corresponden a las fases siguientes. La Fase 1 se entrega en el repositorio público https://github.com/DerekTodd/huella-carbono-totosclub. La aplicación web aún no está desplegada.

**Criterio de lectura:** “Huella de carbono” es el título del proyecto. El indicador base mide CO₂ territorial anual: no representa por sí solo toda la huella de consumo, todos los gases de efecto invernadero ni la responsabilidad histórica acumulada.


## 2. Audiencia y objetivos

### Problema que resuelve

Una clasificación basada únicamente en emisiones totales puede confundir el tamaño de una población o economía con su intensidad de contaminación. El dashboard reunirá varias perspectivas y sus límites para facilitar comparaciones comprensibles y verificables.

| Audiencia | Decisiones o usos | Detalle requerido |
| --- | --- | --- |

| Estudiantes y docentes | Elegir casos de estudio y argumentar diferencias entre países. | Resumen, definiciones, comparaciones y datos por año. |
| Analistas y organizaciones ambientales | Priorizar países para investigación y observar trayectorias. | Series por país, indicadores normalizados y cobertura. |
| Responsables de sostenibilidad | Comparar tendencias y orientar preguntas de política a largo plazo. | KPIs, variaciones, contexto económico y acceso al detalle. |

Se asume un nivel estadístico básico o intermedio. La interfaz ofrecerá una vista general y permitirá profundizar mediante filtros, tooltips y una tabla descargable. No se presupone experiencia con bases de datos.

### Objetivo general

**Objetivo:** Facilitar la comparación de las emisiones territoriales de CO₂ de países y territorios entre 2010 y 2023, mediante indicadores totales, per cápita y económicos, para identificar diferencias y tendencias relevantes para la sostenibilidad.

### Objetivos específicos verificables

- Identificar los cinco mayores emisores con datos del año seleccionado y mostrar su volumen en Mt.

- Comparar la evolución anual y el cambio entre 2013 y 2023, diferenciando aumentos y reducciones.

- Relacionar PIB y CO₂ exclusivamente en observaciones del mismo año con datos de ambas variables.

- Permitir comparar al menos dos países y consultar los seis continentes con una definición regional consistente.

- Mostrar fuente, unidad, año, cobertura y significado de cada indicador para que el usuario pueda verificarlo.

La validación de comprensión con usuarios se realizará al disponer del prototipo; en esta fase la caracterización de audiencia deriva de la consigna y del uso previsto, no de entrevistas realizadas.


## 3. Fuente, alcance y variables

La visualización facilitada [1] sirve como referencia conceptual. Para incorporar población y PIB se utiliza el CSV completo de Our World in Data [2], junto con su diccionario [3]. Los datos de CO₂ proceden de Global Carbon Budget; el PIB se basa en Maddison Project Database. Cada registro representa una entidad geográfica y un año.

| Variable | Significado y formato | Uso |
| --- | --- | --- |

| country / iso_code | Nombre y código geográfico de texto. | Identificación y unión con el mapa. |
| year | Año entero; se conserva 2010-2023. | Filtros y comparación temporal. |
| co2 | Emisiones anuales; número en Mt de CO₂. | Rankings y tendencias. |
| population | Población; personas. | Denominador per cápita. |
| gdp | PIB real en dólares internacionales de 2011, ajustado por PPA. | Dispersión e intensidad económica. |
| co2_per_capita | Indicador publicado en t por persona. | Contraste con el recálculo. |
| co2_per_gdp | Indicador publicado en kg por dólar internacional. | Contraste y documentación. |
| coal_co2, oil_co2, gas_co2 y otros | Desglose por combustible/proceso, en Mt. | Exploración complementaria condicionada a cobertura. |

### Delimitación geográfica

Los rankings utilizan entidades con código de tres letras mayúsculas: se describen como países y territorios, sin afirmar que todas sean Estados soberanos. Se excluyen del ranking World, continentes, grupos de ingresos y agregados superpuestos. Kosovo queda fuera de este universo por tener un código especial OWID; esta limitación debe mostrarse.

Las series continentales conservarán únicamente Africa, Asia, Europe, North America, South America y Oceania del proveedor. World se mantiene separado. No se mezclarán con grupos alternativos como Europe (GCP) o la Unión Europea.

**Comparabilidad:** En la gráfica web de referencia las emisiones se muestran en toneladas; en el CSV completo co2 está en Mt. El periodo 2010-2023 es una decisión del proyecto, aunque la fuente publique años posteriores. El transporte internacional no se asigna a países; por ello la suma de países no equivale automáticamente al total mundial [1].


## 4. Perfilado y limpieza aplicados

Se ejecutó scripts/preprocess.py sobre una instantánea real de la descarga oficial. El script conserva el archivo original local, verifica columnas y genera dos tablas depuradas, un registro de banderas y un informe JSON. Los siguientes resultados son del procesamiento realizado, no una simulación.

| Comprobación | Resultado observado |
| --- | --- |

| Archivo de origen | 50 411 filas; 79 columnas; 33 246 106 bytes. |
| Filas 2010-2023, todas las entidades | 3 556 |
| Universo de países/territorios | 218 entidades; 3 052 filas. |
| Continentes y World, por separado | 98 filas: 7 entidades × 14 años. |
| Duplicados exactos / conflictivos | 0 / 0 |
| Filas en cuarentena por CO₂ inválido | 0 |

### Cobertura de variables principales

| Periodo | Filas/año | CO₂ | Población | PIB y CO₂ |
| --- | --- | --- | --- | --- |

| 2010-2022 | 218 | 215 | 216 | 164 |
| 2023 | 218 | 215 | 216 | 0 |

Los conteos anteriores corresponden a países/territorios con valores disponibles en cada año. En 2023 faltan emisiones para Monaco, San Marino y Vatican; faltan poblaciones para Antarctica y Christmas Island. Estas ausencias no se sustituyeron por cero.

**Decisión derivada del perfilado:** El último año con pares PIB-CO₂ es 2022, con 164 entidades. En 2023 el gráfico económico debe mostrar “Sin datos de PIB para este año” o permitir elegir 2022 de forma explícita. No se asociará el PIB de 2022 con emisiones de 2023.

### Trazabilidad

El informe data/processed/quality_report.json registra URL, tamaño, fecha de procesamiento y SHA-256 del CSV y del diccionario. La huella identifica exactamente los archivos utilizados; no implica que la URL mutable conserve esa versión en el futuro.

Se retienen 3 052 registros de países/territorios, incluidos los que tienen alguna variable ausente. El conjunto utilizable por cada gráfico se define por sus variables necesarias, no eliminando indiscriminadamente filas incompletas.


## 5. Reglas de calidad y valores atípicos

| Situación | Regla aplicada o decisión prevista | Justificación |
| --- | --- | --- |

| Faltantes | Cadena vacía pasa a nulo. Se excluye solo del cálculo que requiera ese valor. | Distinguir falta de medición de una emisión igual a cero. |
| Tipos y dominio | Año entero; valores finitos; CO₂ no negativo; población y PIB positivos. | Evitar unidades inválidas y divisiones sin sentido. |
| Duplicados | Eliminar copias idénticas; detener el proceso ante claves conflictivas. | No elegir arbitrariamente entre dos mediciones. |
| Dato inválido | CO₂ inválido: fila a cuarentena. Otros campos inválidos: nulo y evento de calidad. | Conservar evidencia y evitar contaminar métricas. |
| Uniones geográficas | Clave ISO3 para países; agregados en conjunto separado. | Evitar doble conteo y pérdidas silenciosas. |

### Atípicos: detectar, revisar y conservar

Por cada año se calculan Q1 y Q3 de CO₂ total y CO₂ per cápita entre países/territorios. Se marcan valores fuera de [Q1 - 1,5 × RIQ, Q3 + 1,5 × RIQ], donde RIQ = Q3 - Q1. También se marca un cambio interanual absoluto superior a 30 %, con años consecutivos y base positiva. Son umbrales de revisión del equipo, no reglas universales de error.

La asimetría internacional hace esperables países con emisiones muy altas. Las marcas no producen eliminación ni ajuste automático. Solo se corregirá un valor al confirmar un error con la fuente; se registrarán valor previo, motivo y decisión. Para facilitar lectura se podrán usar escalas logarítmicas sin modificar los datos.

| Bandera generada | Número de eventos |
| --- | --- |

| Fuera del intervalo RIQ; se conserva | 684 |
| Cambio interanual > 30 %; se conserva | 74 |
| Discrepancia entre per cápita publicado y recalculado | 28 |

Un evento no equivale a una fila distinta: una observación puede activar varias reglas. Las 28 discrepancias per cápita se concentran en North America y Oceania durante 14 años; su causa queda pendiente de revisión. Se conservan ambos valores y no se utilizará el per cápita regional en esta versión. Las series continentales utilizarán CO₂ total.

El contraste per cápita admite una tolerancia de máx(0,005; 500/población + 0,0005) t/persona para diferencias de precisión. La revisión de cada bandera y la comparación exacta con las fuentes quedan registradas como actividad posterior, sin afirmar que ya se hayan resuelto.


## 6. Métricas y KPIs reproducibles

Sea E(c,t) el CO₂ territorial del país/territorio c en el año t, medido en Mt; P su población y G su PIB en dólares internacionales de 2011. Los nulos se muestran como “Sin datos” y los cocientes requieren denominadores positivos. Se calcula con la precisión disponible y se redondea solo al presentar.

| Indicador | Definición y criterio de lectura |
| --- | --- |

| Emisiones per cápita | E × 1 000 000 / P; unidad: t CO₂/persona. Permite comparar poblaciones de distinto tamaño. |
| Variación en una década | 100 × (E(c,2023) / E(c,2013) - 1). Los extremos están separados por diez años. 2010-2023 es un cambio de 13 años y se etiquetará como tal. |
| Aumento o reducción anual | 100 × (E(c,t) / E(c,t-1) - 1). Mostrar además E(c,t) - E(c,t-1) en Mt. Exigir años consecutivos. |
| Intensidad de carbono del PIB | E × 1 000 000 000 / G; unidad: kg CO₂ por dólar internacional de 2011. Menor intensidad no garantiza menores emisiones totales. |
| Top 5 emisores | Orden descendente de E en el año seleccionado, solo países/territorios con E válido. Empates: código ascendente. El Top 5 global no cambia al filtrar un continente; el ranking regional se etiqueta aparte. |
| Mayor reducción relativa | Menor variación 2013-2023, exigiendo E(2013) ≥ 1 Mt y cobertura anual completa 2013-2023. Mostrar también reducción en Mt, universo elegible y periodo. |

**Cómo interpretar “mejora ambiental”:** Se operacionaliza únicamente como mayor reducción relativa de CO₂ territorial. El umbral de 1 Mt limita efectos de bases diminutas y excluye ciertos territorios; debe publicarse. Una reducción puede responder a recesiones, cierres industriales, conflictos o cambios productivos; no demuestra por sí misma una mejor política ambiental.

### Comprobación inicial del cálculo, no conclusión definitiva

En 2023, el orden obtenido es China, Estados Unidos, India, Rusia y Japón. Con la regla de reducción definida, Curacao (CUW) registra aproximadamente -62,83 % entre 2013 y 2023. Son resultados preliminares del universo de países/territorios y requieren contexto antes de atribuir causas.

La relación PIB-CO₂ se explorará con pares del mismo año; una correlación será descriptiva y no causal. Si se calcula Pearson se hará sobre log10(PIB) y log10(CO₂), con ambos valores positivos, informando año y número de pares. No se mezclarán observaciones de varios años como si fueran independientes.


## 7. Tipo de dashboard y visualizaciones

### Justificación del tipo estratégico

Se selecciona un dashboard estratégico por su horizonte multianual, sus datos anuales y su finalidad de comparar trayectorias de largo plazo. Permitirá reflexionar sobre sostenibilidad y orientar prioridades de análisis. Aunque también será útil en contextos educativos, su clasificación depende del horizonte y de las decisiones que apoya.

Un dashboard operativo requeriría seguimiento frecuente de procesos y decisiones cotidianas; la actualización anual de esta fuente no responde a ese uso. Un dashboard táctico se centraría en metas y acciones de una organización a medio plazo, que no constituyen el foco de este proyecto.

| Vista propuesta | Pregunta y codificación | Reglas y límites |
| --- | --- | --- |

| Mapa coroplético mundial | ¿Dónde es mayor el CO₂ por persona? Color secuencial en t/persona. | Mismo año; nulos en gris; leyenda explícita y tooltip con total y población. Unir geometrías por código geográfico. |
| Líneas por continente | ¿Cómo cambian las emisiones? Año en X, CO₂ total en Mt en Y. | Seis series regionales oficiales; no añadir World a la suma. No unir huecos como si hubiera mediciones. |
| Dispersión PIB vs. CO₂ | ¿Cómo se relacionan tamaño económico y emisiones? PIB en X, CO₂ en Y. | Pares del mismo año, hasta 2022; escalas logarítmicas etiquetadas y tabla accesible. Informar n y exclusiones. |
| Barras horizontales Top 5 | ¿Qué países/territorios emiten más? Longitud proporcional a Mt. | Año y universo visibles; eje desde cero. Se acompaña de tarjetas KPI. |
| Barras apiladas, opcionales | ¿Qué combustibles o procesos aportan emisiones? | No hay columnas sectoriales en la instantánea. Solo usar carbón, petróleo, gas, cemento y otros componentes si son completos y reconciliables. |

El desglose por transporte, agricultura o industria requeriría otra fuente y una nueva evaluación de compatibilidad. No se prometerá ese gráfico sectorial con los datos actuales. Para el desglose por combustible/proceso se verificará la suma contra el total y se mostrarán las diferencias de cobertura; queda fuera del alcance mínimo.

### Interacción y accesibilidad

Filtros de año, intervalo temporal y países; selector de continente para vistas compatibles; restablecimiento y descarga de la tabla filtrada. Año inicial: 2023 para emisiones; el gráfico económico pedirá elegir 2022 explícitamente. Incluir navegación por teclado, etiquetas, unidades y tabla alternativa; no depender solo del color para distinguir aumentos y reducciones.


## 8. Integración y diseño de base de datos

Se elige PostgreSQL porque los datos se organizan naturalmente por entidad y año, requieren relaciones consistentes y consultas de agregación. Las claves, restricciones y transacciones permiten evitar duplicados y publicar lotes validados [4]. El SQL adjunto es un diseño para la siguiente fase; no constituye evidencia de un servidor ya implementado.

```text
OWID CSV -> Python / calidad -> PostgreSQL -> API / React
```

| Tabla prevista | Contenido y controles |
| --- | --- |

| ingestion_runs | URL, SHA-256 de CSV y diccionario, fecha de descarga, versión de reglas y lote activo. Una sola instantánea activa. |
| locations | Código único, nombre, tipo country/region/world e ISO3 opcional. Los agregados no tienen ISO3 de país. |
| annual_observations | CO₂, población, PIB e indicadores fuente por lote, entidad y año. Clave primaria compuesta; controles de dominio. |
| quality_events | Entidad, variable, regla, valor original, estado de revisión y motivo de decisión. |
| active_metrics, vista | Cálculos per cápita y por PIB sobre el lote activo. Separación explícita del tipo de entidad. |

### Proceso de carga previsto

- Descargar y conservar originales; registrar fecha, tamaño, hash y diccionario antes de transformar.

- Validar y producir CSV separados. En staging, mapear co2 a co2_mt, gdp a gdp_ppp_2011 y vacíos a NULL. Conservar cifras originales de indicadores publicados.

- Crear o reutilizar el catálogo: ISO3 como entity_code para países; códigos estables REG_AFRICA, REG_ASIA y equivalentes para regiones, y WORLD para el mundo.

- Dentro de una transacción, insertar el nuevo lote, las observaciones y los eventos. Verificar claves, dominios, conteos y muestras de indicadores contra el informe.

- Desactivar el lote anterior y activar el validado al final de la transacción. Ante error, rollback. Conservar el lote previo para trazabilidad y reversión.

### Consulta y publicación de la aplicación

React consultará una API de solo lectura con filtros validados de año y entidad. Se prevén endpoints /countries, /metrics, /rankings y /timeseries. Las credenciales de PostgreSQL estarán en el servidor, con un usuario limitado a lectura para la API. No se incluirán en el repositorio público.

Se plantea publicar el frontend en GitHub Pages [5]; la API y PostgreSQL se alojarán aparte. Pages sirve contenido estático y no ejecuta PostgreSQL. La selección concreta de alojamiento y los conectores se resolverán en la fase de implementación, manteniendo React como frontend [6].


## 9. Repositorio, plan y aceptación

### Repositorio público

Repositorio público: https://github.com/DerekTodd/huella-carbono-totosclub. El README incluye el equipo TotosClub, el único integrante Derek Todd López y la descripción del proyecto. La rama principal main contiene el PDF, la fuente editable, los datos preparados y los scripts de la Fase 1.

| Ruta entregada | Propósito |
| --- | --- |

| README.md | Identidad del equipo, alcance, fuentes y reproducción. |
| docs/fase-1.md y output/pdf/ | Fuente editable y documento de justificación. |
| scripts/preprocess.py | Limpieza y perfilado reproducibles. |
| data/processed/ | Datos preparados, cobertura, banderas y cuarentena. |
| db/schema.sql | Diseño relacional para PostgreSQL. |
| scripts/build_report.py | Regeneración del PDF y del texto editable. |

### Plan por fases y responsabilidad

Derek Todd López asume todas las funciones. Usará issues para requisitos y problemas de calidad, ramas para cambios y pull requests para registrar revisión y evidencia, aun siendo el único integrante.

- Fase 1: análisis, perfilado, reglas, documento y publicación de los entregables en el repositorio público.

- Fase 2: ejecutar esquema y carga transaccional; revisar las discrepancias; implementar API y componentes React.

- Fase 3: integrar mapa y gráficos, validar filtros y accesibilidad, probar con usuarios y publicar la aplicación.

### Criterios de aceptación

| Criterio | Evidencia / estado |
| --- | --- |

| Audiencia, objetivo, datos y tipo justificados | Documentados en esta entrega. |
| Limpieza aplicada y reproducible | CSV, flags y JSON generados desde la fuente real. |
| Repositorio público accesible sin sesión | Repositorio público de entrega enlazado en esta página. |
| README con equipo e integrante | Publicado con los datos solicitados. |
| Persistencia y dashboard web | Previstos para fases posteriores; sin implementación ni URL aún. |

La entrega permite consultar el README y descargar el PDF desde el repositorio público. En las fases siguientes se comprobarán tres países contra la fuente, años extremos, divisiones por cero, faltantes y separación de agregados. El PIB ausente de 2023 se conservará como nulo.


## 10. Conclusiones, límites y referencias

### Conclusión de la Fase 1

El análisis define un dashboard estratégico viable para estudiar diferencias y trayectorias de CO₂ territorial entre países y territorios. La limpieza inicial confirma que el periodo 2010-2023 es utilizable para emisiones, mientras que el análisis económico debe limitarse a años con PIB disponible, hasta 2022 en esta instantánea.

La comparación combinará valores absolutos y normalizados: un gran volumen total no implica necesariamente el mayor valor por persona. La fase siguiente deberá probar cómo se relacionan población, economía y emisiones; no se adelantan conclusiones causales a partir de una clasificación o una correlación.

### Límites que acompañarán al dashboard

- Cobertura incompleta, código especial de Kosovo fuera del universo ISO3 y diferencias entre países y territorios.

- CO₂ territorial sin cambio de uso del suelo; no incluye todos los gases ni ajusta por importaciones. No mide por sí solo responsabilidad histórica o ambiental total.

- PIB y CO₂ pueden revisarse; el conjunto se actualiza y cada publicación debe conservar su instantánea y reglas.

- Las 28 discrepancias regionales siguen pendientes de revisión. La serie de CO₂ total continental puede construirse sin usar esos cocientes per cápita.

### Referencias consultadas el 4 de noviembre de 2026

[1] Our World in Data. Annual CO₂ emissions. Emisiones territoriales, unidades y alcance. https://ourworldindata.org/grapher/annual-co2-emissions-per-country

[2] Our World in Data. CO₂ and Greenhouse Gas Emissions dataset. CSV, procedencia, metodología y atribución. https://github.com/owid/co2-data

[3] Our World in Data. Diccionario de variables owid-co2-codebook.csv. Incluye Global Carbon Budget (2025), población y Maddison Project Database 2023. https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv

[4] PostgreSQL. Constraints. https://www.postgresql.org/docs/current/ddl-constraints.html

[5] GitHub Docs. What is GitHub Pages? https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages

[6] React. Quick Start. https://react.dev/learn

**Atribución y conservación:** Se atribuyen los datos a Our World in Data y sus proveedores originales. La reutilización de datos de terceros depende de sus condiciones originales; no se les aplica automáticamente una licencia nueva del proyecto. Los hashes completos están en el informe de calidad.

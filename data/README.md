# Datos y trazabilidad

Fuente: [Our World in Data - CO₂ and Greenhouse Gas Emissions](https://github.com/owid/co2-data).

`raw/` conserva localmente los originales descargados y queda excluido de Git y del paquete de entrega. Si no están presentes, `python scripts/preprocess.py` descargará la versión vigente; esa versión puede diferir de la utilizada en esta entrega. No se garantiza reproducir una instantánea antigua desde una URL mutable.

`processed/` contiene:

- `countries_2010_2023.csv`: países y territorios con código de tres letras mayúsculas, 2010-2023.
- `regions_2010_2023.csv`: seis continentes y World, separados del universo de países.
- `quality_report.json`: cobertura, reglas, hashes del CSV y el diccionario, conteos y avances de KPIs.
- `quality_flags.csv`: eventos de revisión. Una fila de datos puede tener varias banderas.
- `quarantine.csv`: filas apartadas por CO₂ inválido; contiene solo encabezados cuando no hay casos.

Campos calculados: `co2_per_capita_calc` en t/persona y `co2_per_gdp_calc` en kg/dólar internacional de 2011. Los campos fuente se conservan aparte. Los vacíos significan dato ausente, nunca cero imputado. No se han eliminado valores únicamente por ser atípicos.

Los 28 eventos `derived_discrepancy` corresponden al per cápita de North America y Oceania; su causa sigue pendiente de revisión. El alcance mínimo usa sus emisiones totales, no ese cociente regional.

La revisión de atribución debe incluir Our World in Data, Global Carbon Budget y Maddison Project Database. Los datos de terceros conservan las condiciones de sus autores originales.

# Huella de carbono: ¿quién contamina más?

**Equipo:** TotosClub  
**Integrante:** Derek Todd López  
**Tema:** Medio ambiente y sostenibilidad  
**Entrega:** Dashboard interactivo y análisis de Fase 1  
**Periodo de estudio:** 2010-2023

**Repositorio público:** [DerekTodd/huella-carbono-totosclub](https://github.com/DerekTodd/huella-carbono-totosclub)

Proyecto de dashboard en React para comparar emisiones territoriales de CO₂ entre países y territorios, su evolución y su relación con la población y la actividad económica. Busca facilitar comparaciones informadas entre emisiones totales, emisiones por persona e intensidad de carbono de la economía.

El dashboard es **estratégico** y estudia tendencias anuales y cambios de largo plazo. El periodo 2010–2023 corresponde a la consigna.

## Abrir el dashboard

Con Node.js 22.12 o posterior y Python 3.10 o posterior:

```powershell
npm ci
npm run dev
```

Abre la dirección que imprime Vite. `npm run build` construye la versión de publicación en `dist/` y `npm run preview` permite probarla localmente.

La aplicación incluye un mapa por persona y por volumen, un top 5 global, el cambio mundial anual, la mayor reducción relativa en diez años, series por continente, comparación de hasta tres países, una dispersión PIB–CO₂ y barras por combustible y proceso. La tabla permite buscar, ordenar y exportar los datos filtrados en CSV.

## Entregables

- [Documento de justificación en PDF](output/pdf/TotosClub_Fase1_Huella_de_Carbono.pdf).
- [Documento editable en Markdown](docs/fase-1.md).
- [Diseño preliminar de PostgreSQL de la Fase 1](db/schema.sql).
- [Esquema SQLite implementado](db/dashboard.sql) y [constructor de la base](scripts/build_dashboard_db.py).
- [Proceso reproducible de limpieza y perfilado](scripts/preprocess.py).
- [Informe de calidad y cobertura](data/processed/quality_report.json).
- Datos preparados de países/territorios y regiones en `data/processed/`.

## Estado y alcance

El PDF de Fase 1 documenta el perfilado y el diseño preliminar. La implementación usa SQLite para que la aplicación se pueda desplegar como sitio estático. El informe conserva las huellas SHA-256 de los originales. Los datos preparados incluyen 3,150 observaciones y mantienen las ausencias como valores nulos.

## Fuente y unidades

- [Visualización de referencia](https://ourworldindata.org/grapher/annual-co2-emissions-per-country?country=USA~GBR~IND~CHN).
- [Repositorio y metodología de Our World in Data](https://github.com/owid/co2-data).
- [Descarga oficial del CSV completo](https://owid-public.owid.io/data/co2/owid-co2-data.csv).
- [Diccionario de variables](https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv).

En el CSV completo, `co2` se expresa en millones de toneladas (Mt); la visualización de referencia lo muestra en toneladas. El PIB usa dólares internacionales de 2011 ajustados por inflación y paridad de poder adquisitivo. Las emisiones territoriales excluyen cambio de uso del suelo y no equivalen a emisiones de consumo ni al conjunto de gases de efecto invernadero.

Se deben atribuir Our World in Data y las fuentes originales, particularmente Global Carbon Budget y Maddison Project Database; los datos de terceros conservan sus propias condiciones de reutilización. Véase la [sección de licencia del proveedor](https://github.com/owid/co2-data#license).

## Reproducir la limpieza

Requiere Python 3.10 o posterior; el script utiliza únicamente su biblioteca estándar.

```powershell
python scripts/preprocess.py
```

La primera ejecución descarga el CSV y el diccionario. Las siguientes reutilizan los originales locales para conservar la instantánea. Para actualizar ambos:

```powershell
python scripts/preprocess.py --refresh
```

El proceso filtra 2010-2023, separa países/territorios con código ISO3 de agregados regionales, comprueba duplicados y dominios, conserva ausencias, recalcula indicadores y marca atípicos sin eliminarlos automáticamente. Genera `quality_flags.csv`, `quarantine.csv`, los CSV depurados y `quality_report.json`. Las cifras publicadas están redondeadas en origen; por ello los recálculos pueden diferir ligeramente.

Para verificar las salidas contra los originales locales y comprobar los KPIs:

```powershell
python scripts/validate_data.py
```

Para regenerar el documento, instalar ReportLab y ejecutar:

```powershell
python -m pip install -r requirements-report.txt
python scripts/build_report.py
```

## Arquitectura implementada

```text
OWID CSV -> validación y limpieza en Python -> base SQLite -> consultas desde React con sql.js
```

Vite empaqueta la aplicación y publica una copia de SQLite con los datos depurados. El navegador consulta esa base en modo de lectura con WebAssembly. El esquema separa entidades de observaciones e impide duplicar un país y año. Cada construcción comprueba integridad y claves foráneas.

El gráfico económico usa PIB y CO₂ del mismo año. Para 2023 muestra explícitamente 2022, el último año con PIB en esta instantánea. Las barras usan los combustibles y procesos que publica la fuente. El segmento «Sin desglose» representa la diferencia entre el total y la suma disponible. Los países pequeños que no aparecen en el mapa a escala 1:110 millones se pueden consultar en la tabla y comparar con el selector.

## Acceso al repositorio de GitHub

Repositorio: [DerekTodd/huella-carbono-totosclub](https://github.com/DerekTodd/huella-carbono-totosclub). Visibilidad pública; rama principal `main`. El README y el PDF pueden consultarse sin iniciar sesión. Para obtener una copia local:

```powershell
git clone https://github.com/DerekTodd/huella-carbono-totosclub.git
cd huella-carbono-totosclub
```

El flujo [Publicar dashboard](.github/workflows/pages.yml) construye y despliega `dist/`. En **Settings → Pages → Source**, selecciona **GitHub Actions**. Después, ejecuta el flujo desde **Actions** o publica un cambio en `main`. La dirección de GitHub Pages para este proyecto es [derektodd.github.io/huella-carbono-totosclub](https://derektodd.github.io/huella-carbono-totosclub/).

## Organización del trabajo

Derek Todd López asume análisis, datos, desarrollo y revisión. Gestionar tareas mediante issues; usar ramas `codex/` o ramas de funcionalidad y pull requests con un objetivo breve y evidencia de validación. En esta fase, cada cambio de datos debe registrar origen, fecha, SHA-256 y reglas aplicadas. La planificación y los criterios de aceptación figuran en el documento de justificación.

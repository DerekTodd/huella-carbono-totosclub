# Huella de carbono: ¿quién contamina más?

**Equipo:** TotosClub  
**Integrante:** Derek Todd López  
**Tema:** Medio ambiente y sostenibilidad  
**Entrega:** Fase 1 - Análisis  
**Periodo de estudio:** 2010-2023

**Repositorio público:** [DerekTodd/huella-carbono-totosclub](https://github.com/DerekTodd/huella-carbono-totosclub)

Proyecto de dashboard en React para comparar emisiones territoriales de CO₂ entre países y territorios, su evolución y su relación con la población y la actividad económica. Busca facilitar comparaciones informadas entre emisiones totales, emisiones por persona e intensidad de carbono de la economía.

El dashboard será **estratégico**, porque estudia tendencias anuales y cambios de largo plazo. No se considera un monitor en tiempo real. La selección del periodo responde a la consigna; no implica que 2023 sea el último año publicado por la fuente.

## Entregables

- [Documento de justificación en PDF](output/pdf/TotosClub_Fase1_Huella_de_Carbono.pdf).
- [Documento editable en Markdown](docs/fase-1.md).
- [Diseño de base de datos PostgreSQL](db/schema.sql).
- [Proceso reproducible de limpieza y perfilado](scripts/preprocess.py).
- [Informe de calidad y cobertura](data/processed/quality_report.json).
- Datos preparados de países/territorios y regiones en `data/processed/`.

## Estado y alcance

El análisis, la limpieza inicial y el diseño están preparados en esta entrega. El PDF contiene resultados reales del perfilado de la instantánea descargada. Los CSV originales se conservan localmente en `data/raw/`, fuera de Git; el informe registra sus huellas SHA-256.

La aplicación React, la API, la carga en un servidor PostgreSQL y el despliegue web corresponden a las siguientes fases y **todavía no están implementados**. El archivo SQL es un diseño ejecutable; no se ha ejecutado contra un servidor PostgreSQL. El repositorio de la Fase 1 es público y contiene el documento, los datos preparados y los scripts de reproducción.

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

## Arquitectura prevista

```text
OWID CSV -> validación y limpieza en Python -> PostgreSQL
                                            |
                                       API de lectura
                                            |
                                      dashboard React
```

El frontend se podrá publicar en GitHub Pages. La API y PostgreSQL requerirán alojamiento separado: Pages sirve archivos estáticos. Las credenciales de la base de datos permanecerán en el servidor. La lectura pública del dashboard no necesitará autenticación de usuario.

## Acceso al repositorio de GitHub

Repositorio: [DerekTodd/huella-carbono-totosclub](https://github.com/DerekTodd/huella-carbono-totosclub). Visibilidad pública; rama principal `main`. El README y el PDF pueden consultarse sin iniciar sesión. Para obtener una copia local:

```powershell
git clone https://github.com/DerekTodd/huella-carbono-totosclub.git
cd huella-carbono-totosclub
```

En esta fase no existe una URL de dashboard desplegado. Tras implementar React, configurar GitHub Actions/Pages y verificar la URL pública. No subir `.env` ni credenciales.

## Organización del trabajo

Derek Todd López asume análisis, datos, desarrollo y revisión. Gestionar tareas mediante issues; usar ramas `codex/` o ramas de funcionalidad y pull requests con un objetivo breve y evidencia de validación. En esta fase, cada cambio de datos debe registrar origen, fecha, SHA-256 y reglas aplicadas. La planificación y los criterios de aceptación figuran en el documento de justificación.

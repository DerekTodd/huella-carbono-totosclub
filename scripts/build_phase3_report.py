"""Informe de implementación de la Fase 3 con evidencia de la aplicación real."""

import json
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader

from build_phase2_report import (
    BODY, BOLD, FOREST, GREEN, INK, IVORY, LIME, LINE, MUTED, TITLE, WHITE,
    Report, sample_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/TotosClub_Fase3_Implementacion_React.pdf'
EVIDENCE = ROOT / 'docs/evidence'
REPOSITORY = 'https://github.com/DerekTodd/huella-carbono-totosclub'
DASHBOARD = 'https://derektodd.github.io/huella-carbono-totosclub/'
MARGIN = 40
TOTAL_PAGES = 9


class ImplementationReport(Report):
    def __init__(self):
        super().__init__(OUT)
        self.c.setTitle('TotosClub | Fase 3 | Implementación del dashboard en React')
        self.c.setSubject('Correspondencia entre el wireframe y la aplicación, componentes y validación')

    def begin(self, wide=False):
        self.width, self.height = landscape(A4) if wide else A4
        self.c.setPageSize((self.width, self.height))
        self.box(0, 0, self.width, self.height, WHITE)
        self.box(0, 0, self.width, 5, GREEN)
        self.label(MARGIN, 21, 'TOTOSCLUB   /   IMPLEMENTACIÓN EN REACT', 8.1, GREEN, BOLD)
        self.label(self.width - MARGIN, 21, 'FASE 03', 8.1, MUTED, BOLD, right=True)

    def end(self, page):
        y = self.height - 36
        self.rule(MARGIN, y, self.width - MARGIN, y)
        self.label(MARGIN, y + 8, 'Derek Todd López  ·  TotosClub', 8.1, MUTED)
        self.label(self.width - MARGIN, y + 8, f'{page:02d} / {TOTAL_PAGES:02d}', 8.1, MUTED, BOLD, right=True)
        self.c.showPage()

    def image(self, name, x, y, width, height, crop=None):
        with Image.open(EVIDENCE / name) as source:
            frame = source.crop(crop) if crop else source.copy()
        self.c.drawImage(ImageReader(frame), x, self.height - y - height,
                         width=width, height=height, preserveAspectRatio=True, anchor='c', mask='auto')

    def heading(self, y, text):
        self.label(MARGIN, y, text, 16.5, FOREST, TITLE)
        return y + 28


def introduction(report, metrics):
    report.begin()
    width = report.width - 2 * MARGIN
    report.box(MARGIN, 51, width, 213, FOREST, radius=12)
    report.label(60, 71, 'FASE 3 · DESARROLLO Y DOCUMENTACIÓN', 9, LIME, BOLD)
    report.label(60, 102, 'Huella de carbono', 33, WHITE, TITLE)
    report.label(60, 149, '¿Quién contamina más?', 20, LIME, BOLD)
    report.par(60, 188, width - 40, 'Del wireframe a un dashboard funcional con React, Vite y SQLite.', 12, WHITE)
    report.label(60, 231, 'TotosClub · Derek Todd López', 10.5, WHITE, BOLD)
    report.label(MARGIN, 288, 'Introducción', 23, FOREST, TITLE)
    y = report.par(MARGIN, 323, width,
        'El dashboard permite explorar las emisiones territoriales de CO₂ entre 2010 y 2023, identificar los mayores emisores y comparar trayectorias por continente o país. La combinación de valores totales, emisiones por persona y PIB permite analizar el fenómeno desde varias escalas.', 11)
    y = report.par(MARGIN, y + 12, width,
        'La Fase 3 convierte las decisiones de la Fase 2 en componentes React y deja una correspondencia verificable entre los indicadores, los gráficos y la distribución visual. El trabajo completa las vistas Mundo, Cambio % y Reducciones, destaca el KPI principal y separa los componentes de las consultas.', 11)
    y = report.heading(y + 24, 'Resultado de la implementación')
    y = report.table(MARGIN, y, [158, width - 158], ['Aspecto', 'Resultado'], [
        ('Indicadores', f'Un KPI principal y tres secundarios. Ejemplo de 2023: {metrics["world"]} mundiales, {metrics["annual"]} anual, China como mayor emisor y Curazao como mayor reducción decenal.'),
        ('Interacción', 'Filtros de año y región, comparación de hasta tres países, selección desde mapa o ranking, búsqueda, ordenamiento y exportación CSV.'),
        ('Datos', '225 entidades y 3,150 observaciones en SQLite. 218 países y territorios, seis continentes y el agregado mundial.'),
        ('Validación', 'Cinco pruebas automatizadas aprobadas, compilación de producción y verificaciones de la interfaz en escritorio y vista móvil.'),
    ], 9.5)
    report.par(MARGIN, y + 14, width, 'Documento cerrado el 20 de noviembre de 2026. Capturas y registro de pruebas de interfaz del 18 de noviembre de 2026. Las cifras pertenecen a la instantánea del proyecto.', 9.4, MUTED)
    report.end(1)


def structure(report):
    report.begin()
    y = report.title('01   /   ESTRUCTURA DEL PROYECTO', 'Componentes y flujo de datos',
        'Las carpetas separan la estructura visual, las consultas SQL, la preparación de datos y las evidencias de la entrega.')
    tree = [
        'src/',
        '  main.jsx                 Estado, carga y secciones del tablero',
        '  components/',
        '    Layout.jsx             Header y Hero',
        '    Controls.jsx           Filtros y selección de países',
        '    KpiCards.jsx           Summary y MetricCard',
        '    Shared.jsx             Títulos y botones de vista',
        '    DataTable.jsx          Tabla, búsqueda, orden y CSV',
        '    Methodology.jsx        Definiciones y enlaces de entrega',
        '  charts.jsx               Mapa y componentes de gráficos',
        '  data.js                  Apertura de SQLite y catálogo visual',
        '  data/queries.js          Consultas de indicadores y series',
        '  data/metrics.js          Variación y formato de unidades',
        '  style.css                Paleta, retícula y adaptación',
        'db/dashboard.sql           Esquema relacional y vista indicators',
        'scripts/                   Limpieza, SQLite e informes PDF',
        'data/processed/            Instantánea depurada y calidad',
        'public/data/huella.sqlite  Base generada en cada construcción',
        'tests/dashboard.test.js    Pruebas de consultas e indicadores',
        'docs/evidence/             Capturas y validación de interfaz',
        '.github/workflows/         Pruebas, construcción y despliegue',
    ]
    width = report.width - 2 * MARGIN
    report.box(MARGIN, y, width, 276, IVORY, LINE, 8)
    for index, line in enumerate(tree):
        report.label(MARGIN + 12, y + 10 + index * 12.1, line, 8.1, INK, 'Courier')
    y = report.heading(y + 296, 'De la fuente a la pantalla')
    y = report.par(MARGIN, y, width,
        'CSV depurados → build_dashboard_db.py → huella.sqlite → Fetch y sql.js → consultas SQL → props de componentes React. El archivo public/data/huella.sqlite se regenera antes de desarrollo, pruebas y construcción.', 10.6)
    y = report.par(MARGIN, y + 11, width,
        'App utiliza useEffect para abrir la base y conserva los estados de carga y error. Dashboard mantiene con useState el año, la región, los países, el intervalo y las vistas. useMemo evita repetir consultas cuando sus entradas no cambian.', 10.6)
    report.par(MARGIN, y + 11, width,
        'Cada selección actualiza las props de Summary, WorldMap, los rankings y los gráficos. Las tarjetas mundiales conservan su alcance global al filtrar una región. Restablecer devuelve el estado inicial de 2023.', 10.6)
    report.end(2)


def technical_choices(report):
    report.begin()
    y = report.title('02   /   JUSTIFICACIÓN TÉCNICA', 'Herramientas y componentes',
        'Las versiones corresponden a las dependencias instaladas y fijadas en package-lock.json. El stack de la consigna se presenta como sugerido.')
    width = report.width - 2 * MARGIN
    y = report.table(MARGIN, y, [138, width - 138], ['Elección', 'Razón y uso en el proyecto'], [
        ('React 19.3.1', 'Componentes reutilizables para tarjetas, filtros, tabla y gráficos. El estado de Dashboard coordina el año y las selecciones sin recargar la página.'),
        ('Vite 7.3.7', 'Servidor de desarrollo y construcción de producción. La base relativa ./ resuelve los recursos al publicar el proyecto dentro de la ruta de GitHub Pages.'),
        ('Fetch + sql.js 1.15.2', 'Fetch descarga la instantánea SQLite. sql.js ejecuta consultas de lectura en WebAssembly y permite conservar la misma representación relacional en un alojamiento estático.'),
        ('SQLite + Python', 'El constructor usa la biblioteca estándar sqlite3, tablas STRICT, claves foráneas y una clave entidad-año. Comprueba integridad y reemplaza la base generada al terminar.'),
        ('SVG + d3-geo 3.1.2', 'React renderiza barras, líneas, puntos y sus estados. d3-geo aporta proyección y geometría del mapa; las escalas explícitas mantienen las decisiones del wireframe.'),
        ('world-atlas 2.0.2\ny topojson-client 3.1.0', 'La geometría Natural Earth se distribuye en TopoJSON. topojson-client convierte los países en GeoJSON para proyectarlos en el mapa.'),
        ('CSS y lucide-react', 'Las variables CSS concentran la paleta y las reglas de tamaño. Los iconos de lucide-react acompañan etiquetas de texto para reconocer controles y tarjetas.'),
        ('Node test runner', 'node --test ejecuta las cinco pruebas de consultas y unidades. El flujo de GitHub Actions las exige antes de construir y desplegar.'),
    ], 9.8)
    y = report.heading(y + 19, 'Navegación y organización visual')
    report.par(MARGIN, y, width,
        'La navegación usa anclas a Panorama, Tendencias, Datos y Metodología dentro de una sola pantalla. Los componentes reciben props concretas y la capa de consultas acepta parámetros SQL enlazados para los filtros.', 10.4)
    report.end(3)


def correspondence(report):
    report.begin(wide=True)
    report.title('03   /   CORRESPONDENCIA DISEÑO-IMPLEMENTACIÓN', 'Del wireframe a React',
        'La captura del diseño de Fase 2 se contrasta con la vista real de escritorio. Se conserva el orden de lectura y se aplica la jerarquía propuesta.')
    gap = 18
    width = (report.width - 2 * MARGIN - gap) / 2
    right = MARGIN + width + gap
    report.label(MARGIN, 142, 'A · WIREFRAME CON RETÍCULA', 9, GREEN, BOLD)
    report.label(right, 142, 'B · DASHBOARD EN REACT', 9, GREEN, BOLD)
    report.image('fase2-wireframe.png', MARGIN, 164, width, 260)
    report.image('fase3-escritorio.jpg', right, 164, width, 260, (0, 0, 1920, 1500))
    report.par(MARGIN, 433, width, 'Fuente A: página 4 del informe de diseño de TotosClub. La retícula establece tarjetas 4/2/3/3, mapa y ranking 8/4 y análisis 6/6.', 9.5, MUTED)
    report.par(right, 433, width, 'Fuente B: captura de la aplicación local verificada. La cifra mundial ocupa más ancho y fondo lima; el mapa se sitúa a la izquierda del ranking.', 9.5, MUTED)
    report.par(MARGIN, 491, report.width - 2 * MARGIN,
        'CSS Grid expresa la fila de KPIs en proporciones 4fr 2fr 3fr 3fr, el panorama en 2fr 1fr y el análisis en dos columnas iguales. Las alturas se ajustan al contenido. La cabecera incorpora una ilustración de apoyo y las secciones mantienen el orden del boceto.', 10.3)
    report.end(4)


def kpis(report, metrics):
    report.begin()
    y = report.title('04   /   IMPLEMENTACIÓN DE KPIS', 'Cálculo, consulta y renderizado',
        'E representa el CO₂ en millones de toneladas (Mt), P la población y G el PIB en dólares internacionales de 2011. El año seleccionado se identifica como t.')
    width = report.width - 2 * MARGIN
    y = report.table(MARGIN, y, [123, 247, width - 370], ['KPI de Fase 2', 'Cálculo y ubicación', 'Ejemplo 2023'], [
        ('Emisiones mundiales\nPrincipal', 'loadYear recupera WORLD. Summary renderiza E(World,t)/1000 en Gt mediante tonnes(). La tarjeta usa la clase metric-primary.', metrics['world']),
        ('Variación mundial\nSecundario', '100 × (E(World,t)/E(World,t−1) − 1). El LEFT JOIN recupera el año previo y variation() exige una base positiva. Se renderiza en Summary.', metrics['annual']),
        ('Mayor emisor\nSecundario', 'Filtrar kind=country y ordenar por E descendente. El primer registro de top alimenta la tarjeta y TopRanking muestra los cinco primeros.', f'China\n{metrics["leader"]}'),
        ('Mayor reducción\nSecundario', 'Menor cambio porcentual t frente a t−10. La consulta exige base ≥ 1 Mt, 11 observaciones con CO₂ y una variación negativa. Summary y ReductionRanking comparten el resultado.', f'Curazao\n{metrics["reduction"]}'),
    ], 9.5)
    y = report.heading(y + 22, 'Indicadores del mapa y el explorador')
    y = report.table(MARGIN, y, [164, width - 164], ['Métrica', 'Expresión y unidad'], [
        ('CO₂ por persona', 'E × 1,000,000 / P; toneladas de CO₂ por persona.'),
        ('Intensidad del PIB', 'E × 1,000,000,000 / G; kg de CO₂ por dólar internacional de 2011.'),
        ('Variación decenal', '100 × (E(c,t)/E(c,t−10) − 1). Los extremos están separados por diez años.'),
    ], 9.6)
    report.par(MARGIN, y + 15, width,
        'Las consultas preservan NULL. La interfaz muestra un guion o un mensaje de cobertura cuando falta una variable. En 2010 falta el año previo dentro de la instantánea; las comparaciones decenales están disponibles desde 2020.', 10.2, MUTED)
    report.end(5)


def graphics_and_map(report):
    report.begin()
    y = report.title('05   /   IMPLEMENTACIÓN DE GRÁFICOS Y MAPA', 'Visualizaciones del wireframe',
        'src/charts.jsx contiene los componentes SVG. Los cambios de vista comparten el año y el intervalo definidos en Dashboard.')
    width = report.width - 2 * MARGIN
    y = report.table(MARGIN, y, [143, width - 143], ['Componente', 'Decisión de Fase 2 llevada a código'], [
        ('TrendChart · Mundo', 'Una línea con el agregado WORLD de loadTrends. El gráfico utiliza el tiempo en X y Mt de CO₂ en Y.'),
        ('TrendChart · Continentes\ny Países', 'Líneas con leyenda para activar o desactivar series, patrones de trazo y lectura por año. Los países usan hasta tres selecciones.'),
        ('AnnualChangeChart', 'Columnas divergentes de loadAnnualChanges. El eje horizontal cruza en cero y los signos acompañan los colores de aumento y reducción.'),
        ('TopRanking y\nReductionRanking', 'Barras desde un origen común para el top cinco. Las reducciones se orientan hacia la izquierda del cero y muestran su porcentaje y periodo.'),
        ('EconomyChart', 'Un punto por país con PIB y CO₂ positivos del mismo año. Los ejes logarítmicos permiten representar varios órdenes de magnitud. Se informa el tamaño de la muestra.'),
        ('FuelChart', 'Barras apiladas por carbón, petróleo, gas, cemento y otros procesos. El residual se etiqueta como «Sin desglose». La leyenda identifica las categorías.'),
    ], 9.6)
    y = report.heading(y + 20, 'WorldMap y procedencia de la geometría')
    y = report.par(MARGIN, y, width,
        'WorldMap convierte countries-110m.json de world-atlas en entidades GeoJSON y usa la proyección Natural Earth de d3-geo. La unión utiliza códigos numéricos del catálogo world-countries y contempla los alias Francia y Noruega. El detalle cartográfico es de 1:110 millones.', 10.2)
    y = report.par(MARGIN, y + 11, width,
        'El mapa permite alternar t/persona y Mt. Cada opción conserva una escala secuencial fija con seis clases y una leyenda visible. El gris representa ausencia de datos. El filtro regional atenúa las entidades externas y la selección de un país lo añade a la comparación.', 10.2)
    report.par(MARGIN, y + 11, width,
        'La cartografía facilita reconocer patrones geográficos. Los territorios pequeños que carecen de una silueta legible en esta escala se consultan desde el selector y la tabla. La procedencia de las cifras permanece en Our World in Data.', 9.8, MUTED)
    report.end(6)


def style_and_mobile(report, validation):
    report.begin()
    y = report.title('06   /   PALETA Y ESTILOS', 'Coherencia visual y adaptación',
        'Las cuatro decisiones principales de color se conservan en :root de src/style.css y se aplican mediante clases de los componentes React.')
    width = report.width - 2 * MARGIN
    colors = [('Bosque', '--deep', FOREST), ('Verde hoja', '--green', GREEN), ('Lima suave', '--lime', LIME), ('Marfil verde', 'Fondo', IVORY)]
    swatch = (width - 27) / 4
    for index, (name, variable, color) in enumerate(colors):
        x = MARGIN + index * (swatch + 9)
        report.box(x, y, swatch, 86, WHITE, LINE, 6)
        report.box(x + 7, y + 7, swatch - 14, 25, color, radius=3)
        report.label(x + 8, y + 37, name, 9.4, INK, BOLD)
        report.label(x + 8, y + 53, color, 8.4, MUTED, 'Courier')
        report.label(x + 8, y + 67, variable, 8.1, MUTED)
    y += 103
    y = report.par(MARGIN, y, width,
        'El título usa Georgia y el contenido usa Segoe UI con alternativas del sistema. Las tarjetas y los filtros usan tamaños consistentes, bordes suaves y superficies claras. La tarjeta principal tiene mayor cifra y fondo lima para expresar el nivel 1 de la jerarquía.', 10.3)
    y += 16
    report.image('fase3-movil.jpg', MARGIN, y, 143, 411, (0, 0, 520, 1495))
    text_x = MARGIN + 163
    text_width = width - 163
    report.label(text_x, y, 'Vista móvil comprobada', 17, FOREST, TITLE)
    paragraph_y = report.par(text_x, y + 29, text_width,
        f'La validación registró un ancho efectivo de {validation["responsive"]["width"]} px. La tarjeta principal ocupa todo el ancho de la retícula y los KPIs secundarios se distribuyen en dos columnas.', 10.2)
    paragraph_y = report.par(text_x, paragraph_y + 12, text_width,
        'A partir de los puntos de corte de 820 y 600 px, filtros, mapa, ranking y gráficos se apilan conservando la secuencia del diseño. La tabla mantiene sus columnas mediante desplazamiento horizontal.', 10.2)
    paragraph_y = report.par(text_x, paragraph_y + 12, text_width,
        'La prueba encontró desbordamiento horizontal de página igual a falso y desplazamiento habilitado en la tabla. Los controles tienen etiquetas accesibles y un contorno de foco visible.', 10.2)
    report.par(text_x, paragraph_y + 12, text_width,
        'La imagen es una captura de la aplicación real. Las evidencias completas de escritorio, móvil y vistas alternativas se conservan en docs/evidence/.', 9.6, MUTED)
    report.end(7)


def problems_and_checks(report):
    report.begin()
    y = report.title('07   /   PROBLEMAS Y SOLUCIONES', 'Decisiones verificadas',
        'La revisión contrastó cada vista propuesta en el wireframe con la implementación existente y probó los casos que afectan la lectura de los indicadores.')
    width = report.width - 2 * MARGIN
    y = report.table(MARGIN, y, [170, width - 170], ['Situación encontrada', 'Solución implementada'], [
        ('El boceto añadía tres vistas\ny una jerarquía mayor.', 'Se implementaron Mundo, Cambio % y Reducciones. La fila de tarjetas pasó a proporciones 4/2/3/3 y la tarjeta mundial recibió la clase metric-primary.'),
        ('Los componentes estaban\nconcentrados en main.jsx.', 'Se separaron Layout, Controls, KpiCards, Shared, DataTable y Methodology. Las consultas y el formato se extrajeron a src/data/ conservando la interfaz de importación.'),
        ('El PIB falta en 2023.', 'EconomyChart muestra 2022 con su nota visible y pares del mismo año. La tabla de 2023 conserva el PIB y la intensidad como valores ausentes.'),
        ('Faltan años de comparación\nen el inicio del periodo.', 'La variación de 2010 queda sin valor. Las reducciones decenales se habilitan desde 2020 y se informa el motivo cuando falta una década completa.'),
    ], 9.5)
    y = report.heading(y + 19, 'Verificación automatizada y funcional')
    y = report.table(MARGIN, y, [252, width - 252], ['Comprobación', 'Resultado observado'], [
        ('npm test', '5 pruebas aprobadas; 0 fallos.'),
        ('npm run build', 'Construcción de producción completada.'),
        ('Mundo, Cambio % y Reducciones', '38.09 Gt; 13 columnas anuales; Curazao encabeza 5 reducciones en 2023.'),
        ('Año, región y comparación', '2010 muestra estados de cobertura. Tres países bloquean una cuarta selección. México se filtra en 2022.'),
        ('CSV y visualización móvil', 'CSV con encabezado y un registro MEX. Vista de 520 px sin desbordamiento de página. 0 errores de consola registrados.'),
    ], 9.1)
    report.par(MARGIN, y + 12, width,
        'La evidencia de interfaz está en validacion-fase3.json. Las pruebas usan la misma base SQLite y las funciones de consulta utilizadas por React. GitHub Actions ejecuta npm test antes de construir y desplegar.', 9.6, MUTED)
    report.end(8)


def conclusion(report):
    report.begin()
    y = report.title('08   /   CONCLUSIÓN Y REPRODUCCIÓN', 'Entrega documentada',
        'La implementación conserva los KPIs y la secuencia visual del diseño, completa las vistas planificadas y permite relacionar cada decisión con su componente.')
    width = report.width - 2 * MARGIN
    y = report.heading(y, 'Aprendizajes de la implementación')
    y = report.par(MARGIN, y, width,
        'Separar la consulta, el cálculo y la presentación facilita verificar que una cifra representa el indicador acordado. La reutilización de las mismas funciones en las tarjetas, los gráficos y las pruebas mantiene una interpretación consistente del dato.', 10.8)
    y = report.par(MARGIN, y + 12, width,
        'El wireframe funciona como una guía verificable para asignar ancho, prioridad y orden. CSS Grid conserva esas relaciones y los puntos de corte adaptan la estructura a pantallas pequeñas. Las capturas permiten comprobar esa correspondencia.', 10.8)
    y = report.heading(y + 23, 'Ejecutar y comprobar el proyecto')
    for command, detail in [
        ('npm ci', 'Instala las versiones del archivo de bloqueo con Node.js 22.12 o posterior.'),
        ('npm run dev', 'Construye SQLite con Python y abre el servidor de desarrollo.'),
        ('npm test', 'Regenera la base y ejecuta cinco pruebas automatizadas.'),
        ('npm run build', 'Genera los archivos publicables en dist/.'),
        ('python scripts/build_phase3_report.py', 'Regenera este PDF usando los datos y las evidencias guardadas.'),
    ]:
        report.box(MARGIN, y, width, 42, IVORY, LINE, 5)
        report.label(MARGIN + 10, y + 5, command, 9.2, FOREST, 'Courier')
        report.label(MARGIN + 10, y + 23, detail, 8.8, MUTED)
        y += 49
    y = report.heading(y + 11, 'Fuentes y archivos de entrega')
    report.par(MARGIN, y, width,
        'Indicaciones fase 3, pp. 1-3, consigna del curso. Informe de diseño de TotosClub, Fase 2, p. 4. Capturas locales y registro de pruebas del 18 de noviembre de 2026. Instantánea depurada de Our World in Data del proyecto.', 9.6, MUTED)
    report.link(MARGIN, y + 53, 'Dashboard publicado', DASHBOARD)
    report.link(MARGIN + 170, y + 53, 'Repositorio del proyecto', REPOSITORY)
    report.link(MARGIN + 349, y + 53, 'Fuente de datos', 'https://github.com/owid/co2-data')
    report.end(9)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    validation = json.loads((EVIDENCE / 'validacion-fase3.json').read_text(encoding='utf-8'))
    report = ImplementationReport()
    introduction(report, sample_metrics())
    structure(report)
    technical_choices(report)
    correspondence(report)
    kpis(report, sample_metrics())
    graphics_and_map(report)
    style_and_mobile(report, validation)
    problems_and_checks(report)
    conclusion(report)
    report.c.save()
    print(OUT)


if __name__ == '__main__':
    main()

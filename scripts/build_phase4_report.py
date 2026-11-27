"""Informe de evaluación con las cinco respuestas reales del 25/11/2026."""
import json
from pathlib import Path

from build_phase2_report import Report, BODY, BOLD, TITLE, FOREST, GREEN, LIME, IVORY, WHITE, MUTED, LINE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/pdf/Huella_de_carbono_Fase4_Evaluacion_y_Validacion.pdf'
MARGIN, PAGES = 40, 9
DASHBOARD = 'https://derektodd.github.io/huella-carbono-totosclub/?evaluacion=1'
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSdhbkG4oES_HigRY7eSkBmnOdA6s82TCer8ORhsWno0_BJrbQ/viewform?usp=publish-editor'
REPO = 'https://github.com/DerekTodd/huella-carbono-totosclub'


class EvaluationReport(Report):
    def __init__(self):
        super().__init__(OUT)
        self.c.setAuthor('')
        self.c.setTitle('Huella de carbono: ¿quién contamina más? - Fase 4')
        self.c.setSubject('Evaluación con usuarios, resultados y recomendaciones de mejora')

    @property
    def content_width(self):
        return self.width-2*MARGIN

    def begin(self):
        self.box(0, 0, self.width, self.height, WHITE)
        self.box(0, 0, self.width, 5, GREEN)
        self.label(MARGIN, 21, 'HUELLA DE CARBONO  /  EVALUACIÓN Y VALIDACIÓN', 8, GREEN, BOLD)
        self.label(self.width-MARGIN, 21, 'FASE 04', 8, MUTED, BOLD, right=True)

    def end(self, page, bottom):
        if bottom > self.height-55:
            raise ValueError(f'Contenido fuera del margen en página {page}: {bottom:.1f}')
        y = self.height-36
        self.rule(MARGIN, y, self.width-MARGIN, y)
        self.label(MARGIN, y+8, 'Evaluación del 26 de noviembre de 2026', 8, MUTED)
        self.label(self.width-MARGIN, y+8, f'{page:02d} / {PAGES:02d}', 8, MUTED, BOLD, right=True)
        self.c.showPage()

    def heading(self, y, text):
        self.label(MARGIN, y, text, 16.5, FOREST, TITLE)
        return y+28

    def body(self, y, text, size=10.5, color=FOREST):
        return self.par(MARGIN, y, self.content_width, text, size, color)

    def table(self, x, y, widths, headers, rows, size=9.6):
        return super().table(x, y, widths, headers, [[str(v) for v in row] for row in rows], size)


def cover(r, d):
    r.begin()
    w = r.content_width
    r.box(MARGIN, 61, w, 185, FOREST, radius=12)
    r.label(60, 80, 'FASE 4 - EVALUACIÓN CON USUARIOS', 9, LIME, BOLD)
    r.label(60, 111, 'Huella de carbono', 32, WHITE, TITLE)
    r.label(60, 155, '¿Quién contamina más?', 24, LIME, BOLD)
    r.label(60, 208, 'Respuestas: 25/11/2026  -  Análisis: 26/11/2026', 10.4, WHITE)
    cards = [('5 personas', 'Distintas y de nivel universitario'),
             (f'{d["overall"]["mean"]:.2f}/5', 'Promedio de las diez afirmaciones'),
             (f'{d["questions"][9]["mean"]:.1f}/5', 'Satisfacción general (Q10)'),
             ('45 de 50', 'Valoraciones de 4 o 5: 90 %')]
    cw = (w-12)/2
    for index, (value, label) in enumerate(cards):
        x, y = MARGIN+(index%2)*(cw+12), 271+(index//2)*86
        r.box(x, y, cw, 74, IVORY, LINE, 7)
        r.label(x+13, y+9, value, 25, FOREST, BOLD)
        r.par(x+13, y+43, cw-26, label, 9.2, MUTED)
    y = r.heading(467, 'Introducción')
    y = r.body(y, 'Esta fase evalúa si el dashboard resulta claro, útil y fácil de utilizar para la audiencia definida. Se analizaron cinco cuestionarios reales de Google Forms, con 50 valoraciones cerradas y 25 respuestas abiertas. Los códigos P01-P05 sustituyen cualquier identificación personal.')
    y = r.heading(y+18, 'Resultado principal')
    y = r.body(y, 'La percepción global es favorable. La identificación del KPI principal alcanza 4.8/5 y la satisfacción general 4.6/5. Las mejoras prioritarias se concentran en lectura de textos, alcance de los filtros y comprensión de algunos gráficos. La interactividad incluye una valoración de 2/5 que merece atención aunque su media sea 4.2/5.')
    y = r.body(y+12, 'Se aplicaron cuatro ajustes de lectura y ayuda el 26 de noviembre. Las puntuaciones corresponden a la versión evaluada el día anterior. La eficacia de los ajustes deberá medirse en una segunda ronda.', 10.1, MUTED)
    r.link(MARGIN, 754, 'Dashboard público', DASHBOARD)
    r.link(MARGIN+168, 754, 'Formulario de evaluación', FORM)
    r.link(MARGIN+352, 754, 'Repositorio del proyecto', REPO)
    r.end(1, max(y, 770))


def sample(r, d):
    r.begin()
    y = r.title('01  /  AUDIENCIA Y MUESTRA', 'Quién participó y con qué alcance',
        'La audiencia principal son estudiantes y docentes interesados en sostenibilidad. La Fase 1 también contempla analistas y responsables de sostenibilidad, con lectura estadística básica o intermedia.')
    y = r.body(y, 'La muestra recibida reúne a cinco personas de 18 a 24 años. El responsable del proyecto confirmó el 26/11/2026 que son personas diferentes y que su nivel educativo es universitario. La consigna solicita un mínimo de tres participantes distintos.', 10.3)
    y = r.table(MARGIN, y+16, [55,90,120,r.content_width-265], ['Código','Edad','Nivel educativo*','Experiencia con dashboards'],
        [(p['id'],p['age'],p['education'],p['experience']) for p in d['participants']], 9.5)
    y = r.body(y+11, '* Edad y experiencia proceden del CSV. El nivel educativo se complementó mediante confirmación del responsable; el formulario actual recogió género en lugar de ese dato. Esta diferencia se conserva en la trazabilidad.', 9.6, MUTED)
    y = r.heading(y+21, 'Cobertura de la muestra')
    y = r.body(y, 'Tres participantes usan dashboards con frecuencia y dos los usan ocasionalmente. Ninguno declaró que fuera su primer uso. El dato opcional de género registra tres mujeres y dos hombres; se presenta agregado para evitar vincularlo con comentarios individuales.')
    y = r.body(y+12, 'Se trata de una muestra pequeña de conveniencia. Ofrece evidencia inicial de una audiencia universitaria joven, pero no permite generalizar el resultado a profesionales, personas de otras edades ni usuarios que nunca han utilizado un dashboard.')
    y = r.body(y+12, 'Los códigos se asignaron en el orden del CSV exportado. Se omitieron las horas individuales y no se solicitaron nombres ni correos. La confirmación de personas distintas procede del responsable, porque la encuesta anónima no verifica identidades.', 10, MUTED)
    r.end(2,y)


def instrument(r, d):
    r.begin()
    y = r.title('02  /  INSTRUMENTO Y PROCEDIMIENTO', 'Encuesta estructurada y abierta',
        'Se utilizó un cuestionario autoadministrado. La instrucción pide explorar el dashboard por cuenta propia antes de responder y comunica únicamente el propósito general de la evaluación.')
    y = r.body(y, 'Escala: 1 = totalmente en desacuerdo; 2 = en desacuerdo; 3 = neutral; 4 = de acuerdo; 5 = totalmente de acuerdo. La cuadrícula exige una respuesta en cada una de sus diez filas.', 10.2)
    y = r.table(MARGIN, y+12, [43,r.content_width-43], ['Código','Afirmación evaluada'], [(q['id'],q['text']) for q in d['questions']], 9.3)
    y = r.heading(y+18, 'Preguntas abiertas')
    for number, question in enumerate(d['open_questions'],1):
        y = r.body(y, f'{number}. {question}', 9.5)+3
    y = r.body(y+8, 'La evaluación se recibió el 25/11 y se exportó el 26/11. Se calcularon medias, medianas y frecuencias, y se revisaron los 25 comentarios por tema. No se realizaron entrevistas ni se midieron tiempos de tareas. El instrumento es propio y no corresponde a la escala SUS; no se calculó una puntuación SUS.', 9.6, MUTED)
    r.end(3,y)


def quantitative(r, d):
    r.begin()
    y = r.title('03  /  RESULTADOS CUANTITATIVOS', 'Cómo se valoró el dashboard',
        'Cada afirmación tiene cinco respuestas completas. Las medias describen esta muestra y se complementan con las distribuciones y los comentarios para conservar los desacuerdos individuales.')
    plot_x, plot_w = 250, 255
    start = y+9
    for tick in range(6):
        x = plot_x+plot_w*tick/5
        r.rule(x,start-3,x,start+350,LINE,.5)
        r.label(x-3,start+356,str(tick),8.5,MUTED)
    for index,q in enumerate(d['questions']):
        top = start+index*35
        r.par(MARGIN,top,194,f'{q["id"]}  {q["short"]}',9.6)
        r.box(plot_x,top+3,plot_w*q['mean']/5,15,FOREST if q['id']=='Q03' else GREEN,radius=3)
        r.label(r.width-MARGIN,top+1,f'{q["mean"]:.1f}',10.5,FOREST,BOLD,right=True)
    y = start+383
    y = r.body(y, 'Media en escala 1-5. Las barras parten de cero para no exagerar las diferencias. Q01-Q10 se describen completos en la página anterior.', 9.2, MUTED)
    y = r.heading(y+21, 'Interpretación')
    y = r.body(y, 'La identificación del KPI principal (Q03) obtiene la media más alta: 4.8/5. La satisfacción general y la representación de los datos alcanzan 4.6/5. Colores y claridad de textos comparten la media menor, 4.0/5, todavía dentro de una valoración positiva.')
    y = r.body(y+12, 'El promedio de las 50 puntuaciones es 4.36/5. De ellas, 45 son 4 o 5 (90 %). Este porcentaje describe valoraciones de afirmaciones, no el porcentaje de personas satisfechas. En Q10, las cinco personas marcaron 4 o 5.', 10.2)
    r.end(4,y)


def audit_scores(r, d):
    r.begin()
    y = r.title('04  /  DISTRIBUCIÓN Y TRAZABILIDAD', 'El detalle detrás del promedio',
        'Las columnas 1-5 muestran cuántas personas eligieron cada puntuación. La última columna conserva el numerador y el denominador de las valoraciones favorables.')
    rows = [(f'{q["id"]} {q["short"]}',q['n'],*[q['counts'][str(v)] for v in range(1,6)],
             f'{q["mean"]:.1f}',f'{q["favorable"]}/{q["n"]} ({q["favorable_pct"]:.0f} %)') for q in d['questions']]
    y = r.table(MARGIN,y,[190,30,30,30,30,30,30,45,r.content_width-415],
                ['Ítem','n','1','2','3','4','5','Media','4 o 5'],rows,8.5)
    y = r.heading(y+20,'Matriz anónima de respuestas')
    y = r.table(MARGIN,y,[55]+[39]*10+[r.content_width-445],
                ['Código']+[f'Q{i}' for i in range(1,11)]+['Media'],
                [(p['id'],*p['scores'],f'{p["mean"]:.1f}') for p in d['participants']],8.8)
    y = r.body(y+13,'Se conservaron las cinco respuestas completas. Hay 24 puntuaciones de 5, 21 de 4, cuatro de 3 y una de 2; no hay puntuaciones de 1. Las medias individuales van de 3.7 a 5.0. El promedio general se calcula con 218 puntos divididos entre 50 valoraciones.',9.8,MUTED)
    r.end(5,y)


def qualitative(r, d):
    r.begin()
    y = r.title('05  /  ANÁLISIS CUALITATIVO', 'Qué explican los comentarios',
        'Se revisaron las cinco respuestas de cada pregunta abierta. Los temas son una codificación manual descriptiva y pueden solaparse: una persona puede valorar el diseño y pedir una mejora al mismo tiempo.')
    y = r.heading(y,'Aspectos que funcionan bien')
    y = r.body(y,'Cuatro personas mencionan positivamente el diseño o los colores (P01-P04). Dos destacan la organización o estructura (P01 y P05). P02 también valora la interactividad y la guía para leer los datos. Estas respuestas respaldan conservar la identidad visual.')
    y = r.body(y+9,'Al preguntar por utilidad, P02 y P03 nombran explícitamente el mapa por persona; P04 y P05, el mayor emisor o la mayor reducción; P01 se refiere al panorama general. Las visualizaciones de síntesis tienen un uso reconocible en esta muestra.',10.2)
    y = r.heading(y+18,'Problemas detectados')
    problem_rows = []
    for theme in [t for t in d['qualitative'] if t['group']=='Problemas']:
        problem_rows.append((f'{theme["quote_id"]}\n{theme["theme"]}',f'«{theme["quote"]}»\n{theme["interpretation"]}'))
    y = r.table(MARGIN,y,[142,r.content_width-142],['Caso y dificultad','Evidencia y lectura'],problem_rows,9.2)
    y = r.heading(y+18,'Recomendaciones de mejora')
    y = r.body(y,'Atender primero la legibilidad de la tabla y la explicación del alcance de los filtros. Añadir orientación junto a las series y a la dispersión. Probar después una comparación con más países y una página más compacta sin incrementar la confusión visual.',10.1)
    y = r.body(y+10,'P03 marcó 5 en las diez afirmaciones y aun así señaló dificultad con el PIB. Esa combinación muestra por qué las puntuaciones deben leerse junto con las respuestas abiertas. P05 no expresó confusión, pero propuso ampliar la comparación.',9.6,MUTED)
    r.end(6,y)


def indicator_validation(r,d):
    r.begin()
    y = r.title('06  /  PERTINENCIA DE KPIS', 'De la pregunta analítica al uso',
        'El objetivo es comparar emisiones territoriales de CO₂ entre países, su evolución y su relación con población y economía durante 2010-2023. Cada indicador aporta una perspectiva concreta.')
    y = r.table(MARGIN,y,[135,r.content_width-135],['Indicador','Pertinencia e interpretación'],[
        ('Emisiones mundiales\nKPI principal','Resume la escala del problema. Q03 obtiene 4.8/5: cuatro personas marcaron 5 y una 4 al identificar el KPI principal. Este resultado respalda la jerarquía visual, aunque el total mundial no sustituye la comparación entre países.'),
        ('Mayor emisor\ny top 5','Responde quién emite más en volumen total. P04 y P05 mencionan el mayor emisor o la mayor reducción como referencias útiles. Cambiar el año permite comparar trayectorias.'),
        ('Cambio anual y\nreducción decenal','Distingue aumentos y descensos. La mayor reducción exige una base de al menos 1 Mt y once años con datos. Una caída de CO₂ por sí sola no demuestra una mejora integral de la política ambiental.'),
        ('Emisiones por persona\ny relación con PIB','El mapa por persona fue señalado por P02 y P03 como el más útil. Normalizar por población complementa el volumen total. La dispersión agrega contexto económico; el comentario de P03 justifica explicar ejes y escala.'),
    ],9.4)
    y = r.heading(y+19,'Resultados por dimensión')
    y = r.table(MARGIN,y,[225,160,r.content_width-385],['Dimensión','Ítems agrupados','Media / 5'],
        [(item['name'],', '.join(item['questions']),f'{item["mean"]:.1f}') for item in d['dimensions']],9.1)
    y = r.body(y+12,'Q03 mide la identificación del KPI principal. Su pertinencia se contrasta además con el objetivo analítico y las preguntas abiertas. Las agrupaciones son descriptivas y Q10 se conserva como satisfacción general independiente. Las medias expresan percepciones; los cálculos se verifican mediante comprobaciones técnicas.',9.6,MUTED)
    r.end(7,y)


def improvements(r,d,v):
    r.begin()
    y = r.title('07  /  AJUSTES Y VALIDACIÓN TÉCNICA','Mejoras aplicadas y pendientes',
        'Se priorizó según la dificultad descrita, la puntuación individual y el esfuerzo de solución. P1 indica prioridad mayor dentro de esta revisión. Los ajustes se aplicaron después de recibir las cinco encuestas.')
    y = r.table(MARGIN,y,[95,310,r.content_width-405],['Prioridad y caso','Cambio realizado','Estado'],[
        ('P1 - P01\nLectura de tabla','Valores de 12 a 16 px y encabezados de 11 a 14 px. Búsqueda y recuentos más legibles, conservando el desplazamiento horizontal de la tabla.','Aplicado\n26/11/2026'),
        ('P1 - P04\nAlcance de filtros','Ayuda desplegable que distingue año, región, comparación y Desde. Informa que las tarjetas y el ranking conservan su alcance mundial.','Aplicado\n26/11/2026'),
        ('P2 - P02\nSeries temporales','Indicación junto a la leyenda para ocultar o mostrar series y comparar menos líneas. Se conservan colores y patrones de trazo.','Aplicado\n26/11/2026'),
        ('P2 - P03\nDispersión del PIB','Explicación visible de cada punto, la orientación de los ejes y los factores de diez de la escala logarítmica.','Aplicado\n26/11/2026'),
    ],9.2)
    y = r.heading(y+18,'Siguientes mejoras por probar')
    y = r.body(y,'P05: explorar una vista alternativa para comparar más de tres países y comprobar su legibilidad. P04: probar una versión más compacta. P01: revisar el contraste y la distinción de series conservando la paleta, valorada positivamente por otros participantes.',10)
    y = r.heading(y+18,'Comprobaciones realizadas')
    ui = v['browser']
    y = r.table(MARGIN,y,[150,r.content_width-150],['Comprobación','Resultado'],[
        ('Pruebas automatizadas',f'{v["unit_tests"]["passed"]} pruebas aprobadas, {v["unit_tests"]["failed"]} fallos. Se comprueban rankings, década, series, pares PIB-CO₂, ausencias y unidades.'),
        ('Construcción y publicación','npm run build correcto. GitHub Actions completó la publicación de los ajustes.'),
        ('Interfaz publicada',ui['summary']),
    ],9.2)
    y = r.body(y+11,'Estas comprobaciones verifican funcionamiento y presentación. Aún falta una segunda evaluación con personas para medir si aumentó la claridad o disminuyó la confusión.',9.7,MUTED)
    r.end(8,y)


def conclusions(r,d):
    r.begin()
    y = r.title('08  /  CONCLUSIÓN Y EVIDENCIA','Conclusiones de la Fase 4',
        'La evaluación aporta resultados reales y decisiones trazables para continuar la mejora del dashboard, siguiendo los cinco criterios de la rúbrica docente.')
    y = r.body(y,'Las cinco personas participantes valoraron favorablemente la experiencia, con 4.36/5 en el conjunto de afirmaciones y 4.6/5 en satisfacción general. El KPI principal se reconoce con facilidad y el mapa por persona y los KPIs de emisor y reducción aportan utilidad declarada.')
    y = r.body(y+10,'Los casos concretos orientan la revisión: texto pequeño, filtros de alcance poco evidente y dos gráficos que requieren mayor explicación. Se aplicaron cuatro ajustes y se mantuvieron para una prueba posterior las propuestas de más países, mayor compacidad y revisión de contraste.')
    y = r.heading(y+19,'Límites y próxima evaluación')
    y = r.body(y,'La muestra es pequeña y homogénea: nivel universitario, 18-24 años y experiencia previa en dashboards. El nivel educativo y la condición de personas distintas se confirmaron fuera del formulario. No se midieron tiempos ni errores observados. Los resultados no representan una prueba causal del impacto del dashboard.',10.1)
    y = r.body(y+10,'En la segunda ronda se recomienda repetir las diez afirmaciones con al menos tres usuarios representativos e incluir personas sin experiencia previa. Observar tareas de lectura de tabla, filtro regional, comparación temporal y dispersión; registrar éxito, tiempo y comentarios. Comparar resultados por ítem conservando su escala y su población.',10.1)
    y = r.heading(y+19,'Correspondencia con la rúbrica')
    y = r.table(MARGIN,y,[185,45,r.content_width-230],['Criterio','Peso','Evidencia en este informe'],[
        ('Instrumento de evaluación','20 %','Escala, diez afirmaciones y cinco preguntas abiertas (p. 3).'),
        ('Aplicación con usuarios reales','25 %','Cinco personas distintas, perfiles, fecha y exportación (pp. 1-2).'),
        ('Análisis e interpretación','25 %','Medias, frecuencias, matriz, temas y pertinencia de KPIs (pp. 4-7).'),
        ('Áreas de mejora','20 %','Prioridades, cuatro ajustes aplicados y acciones pendientes (p. 8).'),
        ('Presentación y evidencia','10 %','Informe, fuente identificada y resultados reproducibles. La calificación corresponde al docente.'),
    ],8.8)
    y = r.body(y+11,'Fuentes: Indicaciones fase 4.pdf, pp. 4-7; CSV de Google Forms exportado el 26/11/2026; confirmación del responsable del proyecto; código y pruebas del dashboard. Se preservaron las cinco respuestas completas y se omitieron las horas individuales.',9,MUTED)
    r.label(MARGIN,y+10,'SHA-256 del CSV fuente:',8,MUTED,BOLD)
    r.label(MARGIN,y+24,d['source']['sha256'],7.5,MUTED,'Courier')
    r.end(9,y+39)


def main():
    d = json.loads((ROOT/'docs/evaluacion/resultados_fase4.json').read_text(encoding='utf-8'))
    v = json.loads((ROOT/'docs/evaluacion/verificacion_tecnica.json').read_text(encoding='utf-8'))
    if v['browser']['status'] != 'passed' or v['unit_tests']['failed'] or v['build'] != 'passed':
        raise ValueError('Completar la verificación antes de emitir el informe final.')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    r = EvaluationReport()
    cover(r,d); sample(r,d); instrument(r,d); quantitative(r,d); audit_scores(r,d)
    qualitative(r,d); indicator_validation(r,d); improvements(r,d,v); conclusions(r,d)
    r.c.save()
    print(OUT)


if __name__ == '__main__':
    main()

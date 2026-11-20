"""Genera la entrega de diseño y su wireframe vectorial en un PDF."""

import csv
from html import escape
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/TotosClub_Fase2_Diseno_del_Dashboard.pdf'
FOREST = '#132B25'
GREEN = '#2D775D'
LIME = '#D2EC9E'
IVORY = '#F3F6EF'
WHITE = '#FFFFFF'
INK = '#172E25'
MUTED = '#53655B'
LINE = '#D4E1D4'
GRAY = '#DCE3DF'
LAVENDER = '#6559A2'
GOLD = '#9A6029'
DASHBOARD = 'https://derektodd.github.io/huella-carbono-totosclub/'
OWID = 'https://github.com/owid/co2-data'
WCAG = 'https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html'
MAP_COLORS = ['#E2EDCF', '#C3DDB1', '#92C18C', '#5B9E78', '#307961', '#174A3B']
MARGIN = 40


def fonts():
    directory = Path('C:/Windows/Fonts')
    files = [('Report', 'segoeui.ttf'), ('ReportBold', 'segoeuib.ttf'), ('ReportTitle', 'georgia.ttf')]
    if all((directory / file).exists() for _, file in files):
        for name, file in files:
            pdfmetrics.registerFont(TTFont(name, str(directory / file)))
        pdfmetrics.registerFontFamily('Report', normal='Report', bold='ReportBold')
        return 'Report', 'ReportBold', 'ReportTitle'
    return 'Helvetica', 'Helvetica-Bold', 'Times-Roman'


BODY, BOLD, TITLE = fonts()


def sample_metrics():
    data = ROOT / 'data/processed'
    with (data / 'regions_2010_2023.csv').open(encoding='utf-8', newline='') as stream:
        world = {int(row['year']): float(row['co2']) for row in csv.DictReader(stream) if row['country'] == 'World'}
    with (data / 'countries_2010_2023.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    emissions = {(row['iso_code'], int(row['year'])): float(row['co2']) for row in rows if row['co2']}
    top = sorted(((code, value) for (code, year), value in emissions.items() if year == 2023), key=lambda item: -item[1])[:5]
    reductions = [(100 * (value / emissions[code, 2013] - 1), code)
                  for (code, year), value in emissions.items() if year == 2023
                  and emissions.get((code, 2013), 0) >= 1
                  and all((code, end) in emissions for end in range(2013, 2024))]
    decline, code = min(reductions)
    assert top[0][0] == 'CHN' and code == 'CUW'
    return {
        'world': f'{world[2023] / 1000:.2f} Gt', 'annual': f'{100 * (world[2023] / world[2022] - 1):+.1f} %',
        'leader': f'{top[0][1] / 1000:.2f} Gt', 'reduction': f'{decline:.1f} %', 'top': top,
    }


def contrast(foreground, background):
    def luminance(color):
        srgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in srgb]
        return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))

    darker, lighter = sorted((luminance(foreground), luminance(background)))
    return (lighter + 0.05) / (darker + 0.05)


def paragraph(text, size=10.5, color=INK, leading=None, bold=False):
    safe = escape(text).replace('₂', '<sub>2</sub>').replace('\n', '<br/>')
    return Paragraph(safe, ParagraphStyle('cell', fontName=BOLD if bold else BODY, fontSize=size,
                                           leading=leading or size * 1.38, textColor=HexColor(color), alignment=TA_LEFT))


class Report:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=A4)
        self.c.setTitle('TotosClub | Huella de carbono | Fase 2')
        self.c.setAuthor('Derek Todd López')
        self.width, self.height = A4

    def begin(self, wide=False):
        self.width, self.height = landscape(A4) if wide else A4
        self.c.setPageSize((self.width, self.height))
        self.box(0, 0, self.width, self.height, WHITE)
        self.box(0, 0, self.width, 5, GREEN)
        self.label(MARGIN, 21, 'TOTOSCLUB   /   DISEÑO DEL DASHBOARD', 8.1, GREEN, BOLD)
        self.label(self.width - MARGIN, 21, 'FASE 02', 8.1, MUTED, BOLD, right=True)

    def end(self, page):
        y = self.height - 36
        self.rule(MARGIN, y, self.width - MARGIN, y)
        self.label(MARGIN, y + 8, 'Derek Todd López  ·  TotosClub', 8.1, MUTED)
        self.label(self.width - MARGIN, y + 8, f'{page:02d} / 05', 8.1, MUTED, BOLD, right=True)
        self.c.showPage()

    def label(self, x, y, text, size=10, color=INK, font=BODY, right=False):
        self.c.setFont(font, size)
        self.c.setFillColor(HexColor(color))
        method = self.c.drawRightString if right else self.c.drawString
        method(x, self.height - y - size, text)

    def par(self, x, y, w, text, size=10.5, color=INK, bold=False):
        item = paragraph(text, size=size, color=color, bold=bold)
        _, height = item.wrap(w, self.height - y)
        item.drawOn(self.c, x, self.height - y - height)
        return y + height

    def box(self, x, y, w, h, fill, border=None, radius=0):
        self.c.setFillColor(HexColor(fill))
        self.c.setStrokeColor(HexColor(border or fill))
        self.c.setLineWidth(.65)
        if radius:
            self.c.roundRect(x, self.height - y - h, w, h, radius, stroke=int(border is not None), fill=1)
        else:
            self.c.rect(x, self.height - y - h, w, h, stroke=int(border is not None), fill=1)

    def rule(self, x1, y1, x2, y2, color=LINE, width=.75):
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(width)
        self.c.line(x1, self.height - y1, x2, self.height - y2)

    def dot(self, x, y, radius, fill):
        self.c.setFillColor(HexColor(fill))
        self.c.circle(x, self.height - y, radius, stroke=0, fill=1)

    def title(self, index, title, intro):
        self.label(MARGIN, 53, index, 8.8, GREEN, BOLD)
        self.label(MARGIN, 68, title, 26, FOREST, TITLE)
        return self.par(MARGIN, 110, self.width - 2 * MARGIN, intro, 11, MUTED) + 19

    def table(self, x, y, widths, headers, rows, size=9.6):
        w = sum(widths)
        self.box(x, y, w, 27, FOREST, radius=4)
        left = x
        for header, col in zip(headers, widths):
            self.label(left + 9, y + 7, header, 9, WHITE, BOLD)
            left += col
        y += 27
        for index, row in enumerate(rows):
            cells = [paragraph(value, size=size, bold=i == 0) for i, value in enumerate(row)]
            heights = [cell.wrap(col - 18, 700)[1] for cell, col in zip(cells, widths)]
            height = max(heights) + 16
            self.box(x, y, w, height, IVORY if index % 2 == 0 else WHITE)
            left = x
            for cell, col, content_height in zip(cells, widths, heights):
                cell.drawOn(self.c, left + 9, self.height - y - 8 - content_height)
                left += col
            self.rule(x, y + height, x + w, y + height)
            y += height
        return y

    def link(self, x, y, label, url):
        self.label(x, y, label, 9.3, GREEN, BOLD)
        length = pdfmetrics.stringWidth(label, BOLD, 9.3)
        self.c.linkURL(url, (x, self.height - y - 14, x + length, self.height - y + 2), relative=0)


def overview(report, data):
    report.begin()
    w = report.width - 2 * MARGIN
    report.box(MARGIN, 50, w, 222, FOREST, radius=13)
    report.label(61, 69, 'MEDIO AMBIENTE Y SOSTENIBILIDAD', 8.5, LIME, BOLD)
    report.label(61, 92, 'Huella de carbono', 35, WHITE, TITLE)
    report.label(61, 144, '¿Quién contamina más?', 19, LIME, BOLD)
    report.par(61, 181, 410, 'Diseño de un dashboard estratégico para comparar el volumen, la distribución y el cambio de las emisiones territoriales de CO₂.', 10.9, WHITE)
    report.rule(61, 229, report.width - 61, 229, '#5A7968')
    report.label(61, 240, 'TotosClub   ·   Derek Todd López', 10, WHITE, BOLD)
    report.label(report.width - 61, 241, '6 de noviembre de 2026', 8.8, LIME, right=True)

    report.label(MARGIN, 297, 'La pregunta que guía el tablero', 20, FOREST, TITLE)
    report.par(MARGIN, 329, w, '¿Cuánto CO₂ se emitió en el mundo en un año, qué países aportaron más y cómo cambió su contribución? La vista inicial resume el año elegido. El mapa, las series y el explorador permiten profundizar por región o país.', 10.8)

    report.box(MARGIN, 391, w, 139, IVORY, LINE, 9)
    report.box(MARGIN, 391, 5, 139, GREEN)
    report.label(55, 404, 'KPI PRINCIPAL   /   NIVEL 1', 8.3, GREEN, BOLD)
    report.label(55, 421, data['world'], 35, FOREST, BOLD)
    report.label(55, 476, 'Emisiones mundiales de CO₂ · 2023', 12, FOREST, BOLD)
    report.par(55, 496, w - 33, 'El total mundial dimensiona el fenómeno y da una base común para interpretar el volumen de cada país. Se toma el agregado mundial de la fuente.', 9.6, MUTED)

    report.label(MARGIN, 548, 'Tres indicadores secundarios', 16, FOREST, TITLE)
    card_width = (w - 20) / 3
    summaries = [
        ('VARIACIÓN ANUAL', data['annual'], 'Cambio mundial de 2022 a 2023. Muestra la dirección y el ritmo reciente.'),
        ('MAYOR EMISOR', 'China', f'{data["leader"]} en 2023. Identifica quién encabeza el top cinco.'),
        ('MAYOR REDUCCIÓN', 'Curazao', f'{data["reduction"]} entre 2013 y 2023. Señala la mayor caída relativa elegible.'),
    ]
    for index, (name, value, description) in enumerate(summaries):
        x = MARGIN + index * (card_width + 10)
        report.box(x, 579, card_width, 118, WHITE, LINE, 8)
        report.label(x + 11, 590, name, 8.1, GREEN, BOLD)
        report.label(x + 11, 609, value, 23, FOREST, BOLD)
        report.par(x + 11, 644, card_width - 22, description, 9.25, MUTED)

    report.par(MARGIN, 718, w, 'Alcance: CO₂ territorial de combustibles fósiles y procesos industriales, sin cambio de uso del suelo. Periodo de diseño 2010-2023. Los ejemplos de las tarjetas provienen de la instantánea depurada del proyecto.', 9.6, MUTED)
    report.end(1)


def chart_choices(report):
    report.begin()
    y = report.title('01   /   DECISIONES DE VISUALIZACIÓN', 'Un gráfico para cada pregunta',
                     'La tarjeta entrega la cifra del año seleccionado. El gráfico asociado explica su evolución o permite compararla con otras observaciones.')
    w = report.width - 2 * MARGIN
    rows = [
        ('Emisiones mundiales\nPrincipal · Gt', 'Tarjeta destacada y línea mundial.',
         'Muestra el agregado World del año en Gt. La línea conserva el orden cronológico y permite ver cambios y tramos de crecimiento. Se consulta en la vista temporal.'),
        ('Variación mundial anual\nSecundario · %', 'Tarjeta con signo y columnas divergentes.',
         'Compara el total del año con el año previo: 100 × (actual / previo - 1). Un eje en cero distingue subidas y caídas. En 2010 se indica que falta el año previo.'),
        ('Mayor emisor\nSecundario · país y Mt/Gt', 'Tarjeta y top cinco de barras horizontales.',
         'Ordena países y territorios por CO₂ territorial total. Las barras con origen común permiten comparar magnitudes y leer nombres largos. Los agregados quedan fuera del ranking.'),
        ('Mayor reducción relativa\nSecundario · país y %', 'Tarjeta y ranking de reducciones con barras hacia la izquierda.',
         'Compara cada país con diez años atrás. Exige 11 observaciones anuales y al menos 1 Mt de base. Desde 2020, el eje en cero hace visible la magnitud de cada caída.'),
    ]
    y = report.table(MARGIN, y, [125, 128, w - 253], ['Indicador', 'Visualización', 'Por qué se elige'], rows)
    report.label(MARGIN, y + 17, 'Vistas para explorar el contexto', 17, FOREST, TITLE)
    extra = [
        ('CO₂ por habitante', 'Mapa coroplético con escala secuencial y leyenda en t/persona. El país se consulta también en la tabla.'),
        ('Trayectorias regionales', 'Líneas por continente con el mismo eje temporal. La leyenda permite alternar series y comparar países.'),
        ('PIB y emisiones', 'Dispersión logarítmica con un punto por país. Usa PIB y CO₂ del mismo año y muestra 2022 si se selecciona 2023.'),
        ('Composición', 'Barras apiladas para combustibles y procesos. Una porción «Sin desglose» indica la diferencia entre el total y los componentes publicados.'),
    ]
    y = report.table(MARGIN, y + 45, [125, w - 125], ['Tema', 'Diseño y justificación'], extra, 9.4)
    report.box(MARGIN, y + 15, w, 58, IVORY, LINE, 6)
    report.label(MARGIN + 11, y + 22, 'Alcance de la propuesta', 9.5, GREEN, BOLD)
    report.par(MARGIN + 11, y + 38, w - 22, 'El wireframe añade las vistas Mundo y Cambio % al panel temporal, y Reducciones al ranking. Son decisiones de diseño para la siguiente iteración del tablero.', 9.1, MUTED)
    report.end(2)


def visual_system(report):
    report.begin()
    y = report.title('02   /   SISTEMA VISUAL', 'Paleta y jerarquía',
                     'Los verdes conectan el tablero con sostenibilidad. Las superficies claras dejan espacio para leer cifras, leyendas y escalas.')
    w = report.width - 2 * MARGIN
    palette = [
        ('Bosque', FOREST, 'Encabezado, títulos y texto principal.'),
        ('Verde hoja', GREEN, 'Serie activa, barras y controles de énfasis.'),
        ('Lima suave', LIME, 'Acento para el KPI principal y el estado seleccionado.'),
        ('Marfil verde', IVORY, 'Fondo de trabajo y lectura prolongada.'),
    ]
    swatch_w = (w - 27) / 4
    for i, (name, color, use) in enumerate(palette):
        x = MARGIN + i * (swatch_w + 9)
        report.box(x, y, swatch_w, 105, WHITE, LINE, 7)
        report.box(x + 7, y + 7, swatch_w - 14, 29, color, radius=4)
        report.label(x + 8, y + 41, name, 10.4, INK, BOLD)
        report.label(x + 8, y + 58, color, 8.5, MUTED, 'Courier')
        report.par(x + 8, y + 73, swatch_w - 16, use, 8.1, MUTED)
    y += 124
    report.label(MARGIN, y, 'Contraste y lectura accesible', 17, FOREST, TITLE)
    pairs = [('Blanco sobre bosque', WHITE, FOREST), ('Bosque sobre lima', FOREST, LIME),
             ('Verde hoja sobre blanco', GREEN, WHITE), ('Bosque sobre marfil', FOREST, IVORY)]
    rows = [(label, f'{contrast(fg, bg):.2f}:1', 'Supera 4.5:1') for label, fg, bg in pairs]
    y = report.table(MARGIN, y + 27, [241, 117, w - 358], ['Texto y fondo', 'Contraste', 'Texto normal AA'], rows, 9.4)
    y = report.par(MARGIN, y + 12, w, 'Las combinaciones se calcularon con luminancia relativa según WCAG 2.2. Las tendencias usan etiquetas y patrones de trazo. La variación incluye signo y texto, y el mapa rotula el gris como «Sin datos». El foco de teclado tiene contorno visible.', 10, MUTED) + 18

    report.label(MARGIN, y, 'Prioridad de lectura', 17, FOREST, TITLE)
    y += 28
    levels = [
        ('01', 'Título y cifra mundial', 'Título en Georgia. Cifra principal en Segoe UI seminegrita, con fondo destacado y cuatro columnas de ancho.'),
        ('02', 'Gráficos principales', 'Encabezados de 18-24 px. El mapa y el top cinco abren el análisis; debajo aparecen las series y la dispersión.'),
        ('03', 'Detalle y metodología', 'Etiquetas, unidades, notas y tabla en Segoe UI. Las fuentes y las definiciones cierran la lectura.'),
    ]
    for index, heading, description in levels:
        report.box(MARGIN, y, 32, 29, IVORY, LINE, 5)
        report.label(MARGIN + 7, y + 5, index, 11, GREEN, BOLD)
        report.label(MARGIN + 44, y - 1, heading, 11, INK, BOLD)
        y = report.par(MARGIN + 44, y + 15, w - 44, description, 9.5, MUTED) + 12
    report.end(3)


def chart_axes(report, x, y, w, h):
    for dy in (0, h / 2, h):
        report.rule(x, y + dy, x + w, y + dy, LINE, .55)
    report.rule(x, y, x, y + h, '#92A99B', .65)


def map_sketch(report, x, y, scale):
    # Siluetas esquemáticas para mostrar el espacio y la codificación del mapa.
    silhouettes = [
        ([(0, 22), (20, 11), (40, 8), (53, 16), (68, 12), (73, 23), (59, 30), (51, 44), (36, 46), (30, 35), (13, 32)], 4),
        ([(55, 45), (71, 47), (84, 59), (78, 71), (69, 88), (62, 83), (58, 69), (49, 56)], 2),
        ([(69, 7), (89, 0), (98, 9), (86, 21), (73, 17)], 3),
        ([(104, 20), (118, 13), (129, 19), (125, 31), (108, 31), (98, 26)], 3),
        ([(106, 35), (125, 33), (138, 47), (131, 65), (119, 75), (112, 60), (101, 50)], 1),
        ([(129, 20), (143, 10), (166, 7), (184, 15), (213, 16), (227, 25), (212, 32), (201, 48), (180, 42), (166, 55), (151, 37), (137, 32)], 4),
        ([(184, 61), (197, 59), (211, 66), (213, 80), (196, 86), (182, 79)], 3),
    ]
    for points, color in silhouettes:
        path = report.c.beginPath()
        x0, y0 = points[0]
        path.moveTo(x + x0 * scale, report.height - y - y0 * scale)
        for px, py in points[1:]:
            path.lineTo(x + px * scale, report.height - y - py * scale)
        path.close()
        report.c.setFillColor(HexColor(MAP_COLORS[color]))
        report.c.setStrokeColor(HexColor(WHITE))
        report.c.setLineWidth(.8)
        report.c.drawPath(path, fill=1, stroke=1)


def wireframe(report, data):
    report.begin(wide=True)
    report.title('03   /   DISTRIBUCIÓN Y CUADRÍCULA', 'Wireframe de escritorio',
                 'Retícula de 12 columnas con módulos de ancho proporcional. Los trazos muestran la estructura de las vistas y las tarjetas ejemplifican 2023.')
    x0, top, width, gutter = 48, 147, 575, 5
    column = (width - 11 * gutter) / 12

    def position(start):
        return x0 + (start - 1) * (column + gutter)

    def span(count):
        return count * (column + gutter) - gutter

    def module(start, count, y, height, title=None, fill=WHITE):
        x, w = position(start), span(count)
        report.box(x, y, w, height, fill, LINE, 4)
        if title:
            report.label(x + 7, y + 4, title, 8.2, INK, BOLD)
        return x, w

    for i in range(1, 13):
        x = position(i)
        report.box(x, top - 17, column, 13, IVORY, radius=2)
        report.label(x + 4, top - 16, f'{i:02d}', 7, GREEN, 'Courier')
        report.c.setDash(2, 3)
        report.rule(x, top, x, 553, '#BCD0BF', .55)
        report.c.setDash()
    for row, y in enumerate((147, 193, 225, 280, 393, 478, 516), 1):
        report.label(x0 - 17, y + 2, f'{row:02d}', 6.7, GREEN, 'Courier')

    x, w = module(1, 12, 147, 41, fill=FOREST)
    report.label(x + 9, 151, 'TOTOSCLUB / HUELLA DE CARBONO', 8, LIME, BOLD)
    report.label(x + 9, 163, '¿Quién contamina más?', 14, WHITE, TITLE)
    report.label(x + w - 9, 163, 'Panorama   Tendencias   Datos   Metodología', 7.2, WHITE, right=True)

    x, _ = module(1, 12, 193, 27, fill=IVORY)
    for left, label in [(x + 8, 'Año  [2023]    2010 - 2023'), (position(5), 'Región  [Todas]'),
                        (position(8), 'Comparar  [Añadir país]'), (position(11), 'Restablecer')]:
        report.label(left, 201, label, 7.9, INK, BOLD)

    for start, count, label, value, detail in [
        (1, 4, 'Emisiones mundiales', data['world'], 'KPI PRINCIPAL · Gt'),
        (5, 2, 'Variación anual', data['annual'], 'vs. 2022'),
        (7, 3, 'Mayor emisor', 'China', data['leader']),
        (10, 3, 'Mayor reducción', 'Curazao', f'{data["reduction"]} · 2013-2023'),
    ]:
        x, _ = module(start, count, 225, 50, label, LIME if start == 1 else WHITE)
        report.label(x + 7, 240, value, 17 if start == 1 else 13, FOREST, BOLD)
        report.label(x + 7, 261, detail, 7, MUTED)

    x, w = module(1, 8, 280, 108, 'Mapa mundial · CO₂ por persona')
    report.label(x + w - 7, 285, '[ Por persona | Total ]', 7, GREEN, right=True)
    report.box(x + 8, 299, w - 16, 64, IVORY, radius=4)
    map_sketch(report, x + 110, 299, .7)
    for i, color in enumerate(MAP_COLORS):
        report.box(x + 8 + 21 * i, 368, 18, 4.5, color)
        report.label(x + 8 + 21 * i, 374, ('0', '0.5', '2', '5', '10', '20+')[i], 6.1, MUTED)
    report.box(x + 143, 368, 11, 4.5, GRAY)
    report.label(x + 158, 366, 'Sin datos', 6.9, MUTED)
    report.label(x + w - 8, 367, 't/persona · Elegir país', 7.1, MUTED, right=True)

    x, w = module(9, 4, 280, 108, 'Ranking global')
    report.label(x + 7, 297, '[ Top 5 | Reducciones ]', 7.4, GREEN)
    names = ['China', 'Estados Unidos', 'India', 'Rusia', 'Japón']
    maximum = data['top'][0][1]
    for i, ((_, value), name) in enumerate(zip(data['top'], names)):
        y = 310 + i * 13
        report.label(x + 7, y - 1, name, 7.1, INK)
        report.box(x + 67, y + 2, (w - 90) * value / maximum, 5.2, GREEN, radius=2)
    report.label(x + w - 7, 374, 'CO₂ total (Mt)', 6.9, MUTED, right=True)

    x, w = module(1, 6, 393, 80, 'Evolución de emisiones')
    report.label(x + 7, 407, '[ Mundo | Continentes | Países | Cambio % ]', 7.1, GREEN)
    chart_axes(report, x + 19, 423, w - 32, 30)
    report.label(x + 4, 420, 'Mt', 6.7, MUTED)
    for color, heights in [(GREEN, [26, 20, 16, 19, 10, 7]), (LAVENDER, [23, 24, 25, 26, 28, 29])]:
        for i in range(5):
            step = (w - 32) / 5
            report.rule(x + 19 + step * i, 423 + heights[i], x + 19 + step * (i + 1), 423 + heights[i + 1], color, 1.2)
    report.label(x + 19, 455, '2010', 6.8, MUTED)
    report.rule(x + 65, 460, x + 74, 460, GREEN, 1.1)
    report.label(x + 77, 455, 'Asia', 6.7, MUTED)
    report.rule(x + 106, 460, x + 115, 460, LAVENDER, 1.1)
    report.label(x + 118, 455, 'Europa', 6.7, MUTED)
    report.label(x + w - 12, 455, 'Año · 2023', 6.8, MUTED, right=True)

    x, w = module(7, 6, 393, 80, 'PIB frente a CO₂')
    report.label(x + 7, 407, '2022 · Misma fecha · Escalas logarítmicas', 7.1, GREEN)
    chart_axes(report, x + 19, 423, w - 32, 30)
    report.label(x + 4, 420, 'Mt', 6.7, MUTED)
    for px, py, color in [(34, 448, GREEN), (52, 444, LAVENDER), (68, 449, GOLD), (87, 437, GREEN),
                          (111, 440, LAVENDER), (132, 433, GREEN), (169, 430, GOLD), (218, 424, GREEN)]:
        report.dot(x + px, py, 2.1, color)
    for px, name, color in [(20, 'Asia', GREEN), (59, 'Europa', LAVENDER), (109, 'América del Norte', GOLD)]:
        report.dot(x + px, 460, 2, color)
        report.label(x + px + 5, 455, name, 6.7, MUTED)
    report.label(x + w - 12, 455, 'PIB (PPA)', 6.8, MUTED, right=True)

    x, w = module(1, 12, 478, 33, 'Composición por combustible y proceso')
    report.label(x + 7, 494, 'Carbón · Petróleo · Gas · Cemento · Otros · Sin desglose', 7.3, MUTED)
    for i, color in enumerate((FOREST, GREEN, '#90BE77', '#D6AD64', GRAY)):
        report.box(x + w - 153 + i * 28, 490, 27, 9, color)

    x, w = module(1, 12, 516, 36, 'Explorador de datos')
    report.label(x + 7, 532, 'País  |  CO₂ total  |  t/persona  |  Cambio %  |  PIB  |  kg CO₂/$', 7.3, MUTED)
    report.label(x + w - 7, 527, '[ Buscar ]   [ Descargar CSV ]', 7.6, GREEN, BOLD, right=True)

    side = 642
    report.label(side, 131, 'Guía de la retícula', 14.5, FOREST, TITLE)
    notes = [
        ('01 · Cabecera', '12 col. Título general y navegación.'),
        ('02 · Filtros', '12 col. Año, región y hasta tres países.'),
        ('03 · Indicadores', '4 / 2 / 3 / 3 col. La cifra mundial gana ancho, tamaño y fondo.'),
        ('04 · Panorama', '8 / 4 col. El mapa ocupa el área mayor y el ranking queda a la derecha.'),
        ('05 · Análisis', '6 / 6 col. Series temporales y dispersión alineadas.'),
        ('06-07 · Detalle', '12 col. Composición, tabla y acceso a metodología.'),
    ]
    y = 157
    for heading, detail in notes:
        report.label(side, y, heading, 9.4, INK, BOLD)
        y = report.par(side, y + 14, 154, detail, 8.5, MUTED) + 7
    report.rule(side, y + 2, 801, y + 2)
    report.label(side, y + 11, 'Proporción en pantalla', 9.5, GREEN, BOLD)
    report.par(side, y + 27, 153, 'Contenedor de hasta 1,320 px y separación de 16 px. Alturas orientativas: 150 px para tarjetas, 380 px para mapa y 300 px para gráficos de análisis. La tabla se desplaza horizontalmente en pantallas pequeñas.', 8.5, MUTED)
    report.end(4)


def interactions(report):
    report.begin()
    y = report.title('04   /   INTERACCIÓN Y REVISIÓN', 'Del panorama al detalle',
                     'La lectura empieza con el año de referencia y termina con los datos que respaldan cada comparación.')
    w = report.width - 2 * MARGIN
    rows = [
        ('01 · Cambiar el año', 'Actualiza tarjetas, ranking, mapa y tabla. El año elegido es el cierre del intervalo de la serie temporal. La etiqueta del gráfico económico indica su año efectivo.'),
        ('02 · Elegir una región', 'Acota el mapa, las tendencias regionales, la dispersión y la tabla. Los indicadores mundiales conservan su alcance global.'),
        ('03 · Comparar países', 'El selector, el mapa y el ranking permiten añadir hasta tres países. La selección pasa a la serie comparativa y a las barras de composición.'),
        ('04 · Consultar el dato', 'Las etiquetas muestran valor, año y unidad. La tabla se puede ordenar y buscar por nombre o código. Descargar CSV exporta el conjunto filtrado.'),
    ]
    y = report.table(MARGIN, y, [146, w - 146], ['Acción', 'Respuesta del dashboard'], rows)
    report.label(MARGIN, y + 17, 'Adaptación a pantallas pequeñas', 17, FOREST, TITLE)
    y = report.par(MARGIN, y + 44, w, 'El KPI principal ocupa todo el ancho. Los secundarios usan dos columnas cuando hay espacio. El mapa, el ranking y los gráficos se apilan siguiendo el orden de lectura. Los filtros se agrupan en varias filas y la tabla conserva sus columnas con desplazamiento horizontal.', 10.2, MUTED) + 16
    report.label(MARGIN, y, 'Correspondencia con la rúbrica', 17, FOREST, TITLE)
    y = report.table(MARGIN, y + 27, [250, w - 250], ['Criterio', 'Dónde se documenta'], [
        ('KPI principal y secundarios · 20 pts', 'Pregunta, cifras y justificación · pág. 1.'),
        ('Selección de gráficos · 20 pts', 'Matriz de indicadores y visualizaciones · pág. 2.'),
        ('Paleta y coherencia · 20 pts', 'Colores, contraste y jerarquía · pág. 3.'),
        ('Wireframe · 30 pts', 'Retícula, módulos, escalas y filtros · pág. 4.'),
        ('Claridad del documento · 10 pts', 'Estructura y referencias · págs. 1-5.'),
    ], 8.8)
    report.label(MARGIN, y + 14, 'Referencias', 12, FOREST, BOLD)
    report.par(MARGIN, y + 33, w, 'Indicaciones fase 2, consigna del curso, pp. 1-3. El diseño toma como referencia los datos y el estilo visual del proyecto TotosClub.', 9, MUTED)
    report.link(MARGIN, y + 64, 'Dashboard de TotosClub', DASHBOARD)
    report.link(MARGIN + 170, y + 64, 'Our World in Data', OWID)
    report.link(MARGIN + 310, y + 64, 'W3C · Contraste mínimo', WCAG)
    report.end(5)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = Report(OUT)
    data = sample_metrics()
    overview(report, data)
    chart_choices(report)
    visual_system(report)
    wireframe(report, data)
    interactions(report)
    report.c.save()
    print(OUT)


if __name__ == '__main__':
    main()

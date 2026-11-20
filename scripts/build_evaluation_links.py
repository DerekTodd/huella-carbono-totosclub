"""PDF de una página con los enlaces de acceso para la evaluación anónima."""
import argparse
from pathlib import Path
from urllib.parse import urlparse

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

from build_phase2_report import BODY, BOLD, TITLE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/Huella_de_carbono_Enlaces_Evaluacion.pdf'
DASHBOARD = 'https://derektodd.github.io/huella-carbono-totosclub/?evaluacion=1'
FOREST, GREEN, LIME, MUTED = '#132B25', '#2D775D', '#D2EC9E', '#53655B'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--form-url', required=True)
    args = parser.parse_args()
    parsed = urlparse(args.form_url)
    if parsed.scheme != 'https' or parsed.hostname not in {'docs.google.com', 'forms.gle'} or '/edit' in parsed.path:
        parser.error('Usa el enlace público para responder el formulario, no el enlace de edición.')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle('Huella de carbono: ¿quién contamina más? | Enlaces de evaluación')
    c.setAuthor('')
    c.setSubject('Acceso al dashboard público y al formulario de evaluación')
    width, height = A4

    def label(x, y, text, size=11, color=FOREST, font=BODY):
        c.setFillColor(HexColor(color)); c.setFont(font, size)
        c.drawString(x, height-y-size, text)

    def text(x, y, value, size=11.5, color=MUTED, box_width=475):
        paragraph = Paragraph(value, ParagraphStyle('body', fontName=BODY, fontSize=size, leading=size*1.5, textColor=HexColor(color)))
        _, measured = paragraph.wrap(box_width, height)
        paragraph.drawOn(c, x, height-y-measured)
        return y+measured

    c.setFillColor(HexColor(GREEN)); c.rect(0, height-7, width, 7, fill=1, stroke=0)
    label(48, 39, 'FASE 4  /  EVALUACIÓN DEL DASHBOARD', 9.5, GREEN, BOLD)
    label(48, 89, 'Huella de carbono:', 32, FOREST, TITLE)
    label(48, 132, '¿quién contamina más?', 29, FOREST, TITLE)
    label(48, 187, 'Medio ambiente y sostenibilidad · Datos 2010-2023', 11, GREEN, BOLD)
    text(48, 224, 'Explora las emisiones de CO₂ por país, su evolución y su relación con la población y la economía. Después comparte tu experiencia de uso.')

    def card(y, heading, description, caption, url):
        c.setFillColor(HexColor('#F3F6EF')); c.setStrokeColor(HexColor('#D4E1D4'))
        c.roundRect(48, height-y-155, width-96, 155, 11, fill=1, stroke=1)
        label(67, y+17, heading, 18, FOREST, TITLE)
        text(67, y+49, description, 11, box_width=width-134)
        c.setFillColor(HexColor(FOREST)); c.roundRect(67, height-y-132, 245, 37, 6, fill=1, stroke=0)
        label(81, y+105, caption, 10.3, LIME, BOLD)
        c.linkURL(url, (67, height-y-132, 312, height-y-95), relative=0)

    card(300, 'Dashboard interactivo', 'Acceso público. No requiere iniciar sesión. Consulta primero el dashboard y explora sus filtros y gráficos.', 'ABRIR EL DASHBOARD', DASHBOARD)
    card(474, 'Formulario de evaluación', 'Responde después de explorar el dashboard. La encuesta no solicita nombres ni recopila direcciones de correo.', 'RESPONDER LA EVALUACIÓN', args.form_url)
    text(48, 658, 'Los botones contienen enlaces clicables. La vista de evaluación omite los nombres del autor y del equipo para reducir el sesgo.', 10.5)
    c.setStrokeColor(HexColor('#D4E1D4')); c.line(48, 75, width-48, 75)
    label(48, 777, 'Acceso público verificado el 20 de noviembre de 2026.', 9, MUTED)
    c.save()
    print(OUT)


if __name__ == '__main__':
    main()

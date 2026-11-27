"""Analiza un CSV real de Google Forms y publica únicamente resultados anónimos."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
SHORT = ['Facilidad de comprensión', 'Colores informativos', 'Identificación del KPI principal',
         'Representación de los datos', 'Organización de la información', 'Claridad de textos y etiquetas',
         'Interactividad intuitiva', 'Atractivo visual', 'Obtención de conclusiones', 'Satisfacción general']
DIMENSIONS = [
    ('Usabilidad y organización', [0, 4]), ('Comprensión de la información', [3, 5]),
    ('KPIs: identificación del principal', [2]), ('Estética y coherencia visual', [1, 7]),
    ('Interactividad y navegación', [6]), ('Impacto y utilidad', [8]),
]
THEMES = [
    {'group':'Fortalezas', 'theme':'Diseño y colores valorados', 'participants':['P01','P02','P03','P04'],
     'interpretation':'Se valora el aspecto visual; la preferencia de P01 por otra paleta no invalida esa valoración.', 'quote':'El diseño minimalista de color verde', 'quote_id':'P03'},
    {'group':'Fortalezas', 'theme':'Organización y estructura', 'participants':['P01','P05'],
     'interpretation':'La estructura aparece de forma explícita en los comentarios positivos.', 'quote':'La organización', 'quote_id':'P05'},
    {'group':'Utilidad', 'theme':'Mapa de emisiones por persona', 'participants':['P02','P03'],
     'interpretation':'Dos personas nombran expresamente el mapa como el gráfico más útil.', 'quote':'El mapa de emisiones por persona', 'quote_id':'P02'},
    {'group':'Utilidad', 'theme':'Mayor emisor o mayor reducción', 'participants':['P04','P05'],
     'interpretation':'Los KPIs apoyan la comparación de países y años.', 'quote':'mayor emision/mayor reducción', 'quote_id':'P04'},
    {'group':'Problemas', 'theme':'Texto pequeño del explorador', 'participants':['P01'],
     'interpretation':'Aumentar el tamaño de los valores y encabezados de la tabla.', 'quote':'el explorador de datos podría tener los datos mas grandes', 'quote_id':'P01'},
    {'group':'Problemas', 'theme':'Líneas temporales difíciles de distinguir', 'participants':['P02'],
     'interpretation':'Explicar cómo ocultar series con la leyenda y reducir la carga visual.', 'quote':'algunas líneas son un poco complejas de visualizar', 'quote_id':'P02'},
    {'group':'Problemas', 'theme':'Lectura de la dispersión PIB-CO₂', 'participants':['P03'],
     'interpretation':'Explicar cada punto, la orientación de los ejes y la escala logarítmica.', 'quote':'el grafico del PIB frente a CO2', 'quote_id':'P03'},
    {'group':'Problemas', 'theme':'Alcance de los filtros poco claro', 'participants':['P04'],
     'interpretation':'Aclarar qué cambia con año, región, comparación y el intervalo Desde.', 'quote':'Algunos filtros dentro de filtros resultan confusos', 'quote_id':'P04'},
    {'group':'Recomendaciones', 'theme':'Comparar más países a la vez', 'participants':['P05'],
     'interpretation':'Evaluar una vista alternativa antes de ampliar el límite de tres países.', 'quote':'Poder agregar más países al mismo tiempo', 'quote_id':'P05'},
    {'group':'Recomendaciones', 'theme':'Hacer más compacta la página', 'participants':['P04'],
     'interpretation':'Probar una distribución más compacta manteniendo la lectura de gráficos y ayudas.', 'quote':'Reduciría un poco el tamaño de la página', 'quote_id':'P04'},
]


def analyze(path):
    raw = path.read_bytes()
    with path.open(encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames
        rows = list(reader)
    rating_headers = [key for key in headers if key.startswith('Evalúa tu experiencia con el dashboard [')]
    open_headers = [key for key in headers if key.startswith('¿')]
    if len(rating_headers) != 10 or len(open_headers) != 5 or not rows:
        raise ValueError('Se esperan diez afirmaciones, cinco preguntas abiertas y al menos una respuesta.')
    participants = []
    for index, row in enumerate(rows):
        scores = [int(row[key]) for key in rating_headers]
        if not all(1 <= value <= 5 for value in scores):
            raise ValueError('Una puntuación está fuera de la escala 1-5.')
        participants.append({'id':f'P{index+1:02d}', 'age':row['Rango de edad'].strip(),
            'education':'Universitario', 'experience':row['Experiencia previa con dashboards'].strip(),
            'scores':scores, 'mean':round(mean(scores), 2)})
    questions = []
    for index, key in enumerate(rating_headers):
        scores = [p['scores'][index] for p in participants]
        questions.append({'id':f'Q{index+1:02d}', 'text':re.search(r'\[(.*)\]$', key).group(1),
            'short':SHORT[index], 'n':len(scores), 'mean':round(mean(scores), 2), 'median':median(scores),
            'counts':{str(value):scores.count(value) for value in range(1,6)},
            'favorable':sum(value >= 4 for value in scores),
            'favorable_pct':round(100*sum(value >= 4 for value in scores)/len(scores), 1)})
    ratings = [value for p in participants for value in p['scores']]
    gender_key = next(key for key in headers if key.strip().lower().startswith('gener'))
    result = {
        'title':'Huella de carbono: ¿quién contamina más?', 'evaluation_date':'2026-11-26',
        'collection_dates':sorted({row['Marca temporal'].split()[0].replace('/','-') for row in rows}),
        'source':{'filename':path.name, 'sha256':hashlib.sha256(raw).hexdigest(), 'response_count':len(rows),
                  'closed_answers':len(ratings), 'open_answers':sum(bool(row[k].strip()) for row in rows for k in open_headers)},
        'confirmation':{'date':'2026-11-26', 'distinct_people':5, 'education':'Universitario',
            'source':'Confirmación del responsable del proyecto en la conversación: si, universidad.',
            'education_collected_by_form':False},
        'profile':{'age':dict(Counter(p['age'] for p in participants)),
                   'gender':dict(Counter(row[gender_key].strip() for row in rows)),
                   'experience':dict(Counter(p['experience'] for p in participants))},
        'participants':participants, 'questions':questions,
        'dimensions':[{'name':name, 'questions':[questions[i]['id'] for i in indices],
                       'mean':round(mean(p['scores'][i] for p in participants for i in indices),2)}
                      for name,indices in DIMENSIONS],
        'overall':{'mean':round(mean(ratings),2), 'counts':{str(v):ratings.count(v) for v in range(1,6)},
                   'favorable':sum(v>=4 for v in ratings), 'favorable_pct':100*sum(v>=4 for v in ratings)/len(ratings)},
        'open_questions':open_headers, 'qualitative':THEMES,
        'limitations':['Muestra de conveniencia pequeña, de nivel universitario y de 18 a 24 años.',
            'No incluye usuarios sin experiencia previa con dashboards.',
            'No se registraron tiempos de tareas, entrevistas ni observación directa.',
            'La encuesta recoge percepciones y no corresponde a la escala SUS estandarizada.',
            'Los resultados son anteriores a los ajustes del 26 de noviembre; no hay una segunda ronda de usuarios.'],
    }
    if len(participants) != result['confirmation']['distinct_people']:
        raise ValueError('La confirmación de personas debe actualizarse antes de analizar otra muestra.')
    # Las citas breves deben coincidir con los comentarios originales, respetando su redacción.
    for theme in THEMES:
        original = rows[int(theme['quote_id'][1:])-1]
        if not any(theme['quote'] in original[key] for key in open_headers):
            raise ValueError('Cita no localizada en la fuente: ' + theme['theme'])
        theme['n'] = len(theme['participants'])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=Path)
    args = parser.parse_args()
    result = analyze(args.csv)
    out = ROOT/'docs/evaluacion'
    out.mkdir(parents=True, exist_ok=True)
    (out/'resultados_fase4.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'resultados_por_pregunta.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['id','pregunta','n','promedio','mediana','valor_1','valor_2','valor_3','valor_4','valor_5','respuestas_4_o_5','porcentaje_4_o_5'])
        for q in result['questions']:
            writer.writerow([q['id'],q['text'],q['n'],q['mean'],q['median'],*[q['counts'][str(v)] for v in range(1,6)],q['favorable'],q['favorable_pct']])
    print(json.dumps({'n':result['source']['response_count'],'mean':result['overall']['mean'],
        'favorable_pct':result['overall']['favorable_pct'],'questions':[(q['id'],q['mean']) for q in result['questions']]},ensure_ascii=False))


if __name__ == '__main__':
    main()

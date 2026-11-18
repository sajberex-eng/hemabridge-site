"""Builds the partner questionnaire workbooks in ../docs from questionnaire.json (and questionnaire_en.json if present).
Run: python3 make_questionnaire.py   (needs openpyxl). The public file has one answer column and no internal columns."""
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
B = os.path.dirname(os.path.abspath(__file__)) + '/'
UI = {
 'ru': {'file': 'hemabridge-partner-questionnaire-ru.xlsx', 'head': ['№', 'Подраздел', 'Вопрос', 'Приоритет', 'Ответ клиники', 'Источник / дата'],
        'clinic': 'Клиника (название, город, страна):', 'filled': 'Кто заполнил (ФИО, должность, e-mail):', 'date': 'Дата заполнения:',
        'how_tab': 'Как заполнять', 'how_title': 'Опросник HemaBridge для клиник: как заполнять',
        'how': ['HemaBridge — программа ТОО «Центр гематологии» (Астана, Казахстан) по международной маршрутизации пациентов с заболеваниями крови. По этому опроснику наши врачи сравнивают центры по одним и тем же критериям.',
                'Закладки: 1 — медицинская информация; 2 — организационные вопросы; 3 — финансовая сторона; 4 — данные самой клиники о её сильных сторонах и ограничениях.',
                '1. Ответы вносятся в столбец «Ответ клиники» (ячейки с жёлтой заливкой).',
                '2. В столбце «Источник / дата» укажите, откуда взят ответ (отчёт, регистр, публикация) и на какую дату он актуален.',
                '3. Цифры по результатам лечения приводите по каждой нозологии, с указанием источника и периода.',
                '4. По стоимости укажите состав пакета, а не только сумму.',
                '5. Приоритет: «Критично» — без ответа мы не можем рекомендовать центр пациентам; «Важно» — влияет на выбор; «Справочно» — для полноты картины.',
                '6. Фильтр в строке заголовка позволяет показать один подраздел или только вопросы с приоритетом «Критично».',
                'Пример формата ответа (гаплоидентичные ТКМ): «2025 г. — 48 гапло-ТКМ, ПТЦф; 2024 г. — 41» (пример, не данные клиники).',
                'Не включайте в ответы персональные данные пациентов.',
                'Заполненный файл верните сотруднику программы, от которого вы его получили.']},
 'en': {'file': 'hemabridge-partner-questionnaire-en.xlsx', 'head': ['No.', 'Subsection', 'Question', 'Priority', "Clinic's answer", 'Source / date'],
        'clinic': 'Clinic (name, city, country):', 'filled': 'Completed by (name, position, e-mail):', 'date': 'Date completed:',
        'how_tab': 'How to complete', 'how_title': 'HemaBridge questionnaire for clinics: how to complete it',
        'how': ['HemaBridge is a program of Hematology Center LLP (Astana, Kazakhstan) for international routing of patients with blood diseases. Our physicians use this questionnaire to compare centers against the same criteria.',
                'Tabs: 1 — medical information; 2 — organizational questions; 3 — financial information; 4 — the clinic\'s own view of its strengths and limitations.',
                '1. Enter answers in the "Clinic\'s answer" column (yellow cells).',
                '2. In the "Source / date" column, state where the answer comes from (report, registry, publication) and the date it refers to.',
                '3. Give treatment outcome figures for each disease separately, with the source and the period.',
                '4. For costs, describe what the package includes, not only the amount.',
                '5. Priority: "Critical" — without an answer we cannot recommend the center to patients; "Important" — affects the choice; "For reference" — for completeness.',
                '6. Use the filter in the header row to show one subsection or only the "Critical" questions.',
                'Example of an answer format (haploidentical HSCT): "2025 — 48 haplo-HSCT, PTCy; 2024 — 41" (an example, not clinic data).',
                'Please do not include any patient personal data in your answers.',
                'Return the completed file to the program staff member who sent it to you.']},
 'kk': {'file': 'hemabridge-partner-questionnaire-kk.xlsx', 'head': ['№', 'Бөлімше', 'Сұрақ', 'Басымдық', 'Клиниканың жауабы', 'Дереккөз / күні'],
        'clinic': 'Клиника (атауы, қаласы, елі):', 'filled': 'Толтырған (аты-жөні, лауазымы, e-mail):', 'date': 'Толтырылған күні:',
        'how_tab': 'Қалай толтыру керек', 'how_title': 'Клиникаларға арналған HemaBridge сауалнамасы: қалай толтыру керек',
        'how': ['HemaBridge — «Гематология орталығы» ЖШС (Астана, Қазақстан) қан аурулары бар науқастарды халықаралық маршруттау бағдарламасы. Осы сауалнама бойынша дәрігерлеріміз орталықтарды бірдей өлшемдермен салыстырады.',
                'Қойындылар: 1 — медициналық ақпарат; 2 — ұйымдастыру мәселелері; 3 — қаржылық жағы; 4 — клиниканың өз күшті жақтары мен шектеулері туралы деректері.',
                '1. Жауаптар «Клиниканың жауабы» бағанына (сары түсті ұяшықтарға) енгізіледі.',
                '2. «Дереккөз / күні» бағанында жауаптың қайдан алынғанын (есеп, тіркелім, жарияланым) және қай күнге өзекті екенін көрсетіңіз.',
                '3. Емдеу нәтижелері бойынша сандарды әр нозология бойынша бөлек, дереккөзі мен кезеңін көрсетіп келтіріңіз.',
                '4. Құны бойынша тек соманы емес, пакеттің құрамын да көрсетіңіз.',
                '5. Басымдық: «Өте маңызды» — жауапсыз орталықты науқастарға ұсына алмаймыз; «Маңызды» — таңдауға әсер етеді; «Анықтама үшін» — толық көрініс үшін.',
                '6. Тақырып жолындағы сүзгі бір бөлімшені немесе тек «Өте маңызды» сұрақтарды көрсетуге мүмкіндік береді.',
                'Жауап пішімінің мысалы (гаплоидентті СКТ): «2025 ж. — 48 гапло-СКТ, ПТЦф; 2024 ж. — 41» (мысал, клиника дерегі емес).',
                'Жауаптарға науқастардың дербес деректерін қоспаңыз.',
                'Толтырылған файлды оны Сізге жіберген бағдарлама қызметкеріне қайтарыңыз.']},
}
def build(lang, data):
    ui = UI[lang]; wb = Workbook(); wb.remove(wb.active)
    thin = Side(style='thin', color='BFBFBF'); border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for sh in data['sheets']:
        ws = wb.create_sheet(sh['tab'][:31])
        ws['A1'] = sh['title']; ws['A1'].font = Font(bold=True, size=14)
        if sh is data['sheets'][0]:
            for i, k in enumerate(('clinic', 'filled', 'date')):
                ws.cell(row=2 + i, column=1, value=ui[k]).font = Font(bold=True)
                ws.merge_cells(start_row=2 + i, start_column=1, end_row=2 + i, end_column=3)
                c = ws.cell(row=2 + i, column=4); c.fill = PatternFill('solid', fgColor='FFF9E0'); c.border = border
                ws.merge_cells(start_row=2 + i, start_column=4, end_row=2 + i, end_column=6)
            hr = 6
        else:
            hr = 3
        for j, h in enumerate(ui['head'], 1):
            c = ws.cell(row=hr, column=j, value=h); c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='D9D9D9')
            c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = border
        for i, r in enumerate(sh['rows'], hr + 1):
            for j, v in enumerate((r['n'], r['sub'], r['q'], r['prio'], None, None), 1):
                c = ws.cell(row=i, column=j, value=v); c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = border
                if j <= 2: c.fill = PatternFill('solid', fgColor='DDEBF7')
                if j == 5: c.fill = PatternFill('solid', fgColor='FFF9E0')
        for col, w in zip('ABCDEF', (6, 24, 58, 13, 48, 24)): ws.column_dimensions[col].width = w
        ws.freeze_panes = ws.cell(row=hr + 1, column=1)
        ws.auto_filter.ref = 'A%d:F%d' % (hr, hr + len(sh['rows']))
    ws = wb.create_sheet(ui['how_tab'])
    ws['A1'] = ui['how_title']; ws['A1'].font = Font(bold=True, size=14); ws.column_dimensions['A'].width = 120
    for i, line in enumerate(ui['how'], 2):
        ws.cell(row=i, column=1, value=line).alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(B + '../docs/' + ui['file'])
build('ru', json.load(open(B + 'questionnaire.json', encoding='utf-8')))
for _l in ('en', 'kk'):
    if os.path.exists(B + 'questionnaire_%s.json' % _l):
        build(_l, json.load(open(B + 'questionnaire_%s.json' % _l, encoding='utf-8')))
print('questionnaires written')

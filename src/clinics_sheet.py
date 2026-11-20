"""The coordinator's clinics table <-> clinics.json.

  python clinics_sheet.py export [clinics.xlsx]        writes the table from clinics.json (dropdowns, hints, frozen header)
  python clinics_sheet.py import <file.xlsx | file.csv | https://…CSV link>   checks the table and rewrites clinics.json

A Google Sheet works too: upload clinics.xlsx to Google Drive, open it as a Google Sheet, and for import use
File → Share → Publish to web → the sheet «Клиники» → CSV, or the link
https://docs.google.com/spreadsheets/d/<ID>/export?format=csv&gid=<GID> (the sheet must be viewable by link).
export needs openpyxl; importing CSV does not. After import: cd src; python build.py.
"""
import csv, io, json, os, sys, urllib.request
B = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, B)
import clinics_lib as L

# column key, header, width, hint. Order = order in the table.
COLS = [
    ('id', 'id (латиницей)', 22, 'Короткий постоянный код клиники: латиница, цифры, дефис (florence-nightingale). Не меняйте у существующих клиник — на него ведут ссылки.'),
    ('name', 'Название', 30, 'Как клиника называет себя (латиницей, если так на её сайте).'),
    ('country', 'Страна', 14, 'Из списка. Новую страну добавляет разработчик (clinics_lib.py).'),
    ('city', 'Город', 20, 'Один или несколько городов через запятую.'),
    ('status', 'Статус', 22, 'Из списка.'),
    ('checked', 'Проверено (ГГГГ-ММ)', 14, 'Месяц последней сверки с официальным сайтом, например 2026-11. Старше 12 месяцев — на сайте пометка «требует перепроверки».'),
    ('profile', 'Профиль', 40, 'Что за учреждение: тип, с какого года, профиль центра.'),
    ('tkm.auto', 'ТКМ аутологичная', 12, 'да / нет / нет данных'),
    ('tkm.allo', 'ТКМ аллогенная', 12, 'да / нет / нет данных'),
    ('tkm.haplo', 'ТКМ гаплоидентичная', 12, 'да / нет / нет данных'),
    ('tkm_note', 'ТКМ: уточнение', 30, 'Необязательно: дети, неродственный донор и т.п.'),
    ('cart', 'CAR-T', 12, 'да / нет / нет данных'),
    ('cart_note', 'CAR-T: уточнение', 30, 'Необязательно: при каких диагнозах, своё производство клеток и т.п.'),
    ('accreditation', 'Аккредитации', 34, 'JCI, JACIE и т.п., с годом. Пусто — на сайте «нет данных».'),
    ('facilities', 'Оснащение и структура', 34, 'Отделения, лаборатории, палаты. Пусто — «нет данных».'),
    ('foreign', 'Иностранным пациентам', 34, 'Международный отдел, языки, визы, трансфер.'),
    ('clinic_said', 'Только по данным клиники', 24, 'Поля, сведения в которых взяты только с сайта клиники, через запятую: ' + ', '.join(L.SAID.values()) + '. На сайте у поля появится пометка «по данным клиники».'),
    ('sources', 'Источники', 46, 'По одному в строке: название | https://ссылка (Alt+Enter — новая строка в ячейке).'),
] + [('%s.%s' % (lang, f), '%s %s' % (h, lang.upper()), 30, 'Перевод (%s). Пусто — на сайте останется русский текст.' % ('английский' if lang == 'en' else 'казахский'))
     for lang in ('en', 'kk') for f, h in (('name', 'Название'), ('city', 'Город'), ('profile', 'Профиль'), ('tkm_note', 'ТКМ: уточнение'),
                                          ('cart_note', 'CAR-T: уточнение'), ('accreditation', 'Аккредитации'), ('facilities', 'Оснащение и структура'),
                                          ('foreign', 'Иностранным пациентам'))]
SHEET = 'Клиники'
STATUS_BY_LABEL = {v[0]: k for k, v in L.STATUS.items()}
TRI_BY_LABEL = {v: k for k, v in L.TRI.items()}
SAID_BY_LABEL = {v.lower(): k for k, v in L.SAID.items()}

def to_row(c):
    r = {'id': c['id'], 'name': c['name'], 'country': c['country'], 'city': c['city'], 'status': L.STATUS[c['status']][0],
         'checked': c['checked'], 'cart': L.TRI[c['cart']], 'clinic_said': ', '.join(L.SAID[f] for f in c.get('clinic_said', [])),
         'sources': '\n'.join('%s | %s' % (n, u) for n, u in c['sources'])}
    for k in ('auto', 'allo', 'haplo'): r['tkm.' + k] = L.TRI[c['tkm'][k]]
    for f in L.TEXT: r[f] = c.get(f, '')
    for lang in ('en', 'kk'):
        for f, v in (c.get(lang) or {}).items(): r['%s.%s' % (lang, f)] = v
    return r

def from_row(r, n, err):
    g = lambda k: str(r.get(k) if r.get(k) is not None else '').strip()
    def pick(table, k, label):
        v = g(k)
        return table.get(v, v)   # an unknown value stays as typed; validate() names it
    hdr = dict((k, h) for k, h, _, _ in COLS)
    c = {'id': g('id'), 'name': g('name'), 'country': g('country'), 'city': g('city'),
         'status': pick(STATUS_BY_LABEL, 'status', hdr['status']), 'checked': g('checked'),
         'profile': g('profile'),
         'tkm': {k: pick(TRI_BY_LABEL, 'tkm.' + k, hdr['tkm.' + k]) for k in ('auto', 'allo', 'haplo')},
         'tkm_note': g('tkm_note'), 'cart': pick(TRI_BY_LABEL, 'cart', 'CAR-T'), 'cart_note': g('cart_note'),
         'accreditation': g('accreditation'), 'facilities': g('facilities'), 'foreign': g('foreign'), 'clinic_said': [], 'sources': []}
    for x in filter(None, (s.strip() for s in g('clinic_said').replace(';', ',').split(','))):
        c['clinic_said'].append(SAID_BY_LABEL.get(x.lower(), x))
    for line in filter(None, (s.strip() for s in g('sources').splitlines())):
        name, _, url = line.partition('|')
        c['sources'].append([name.strip(), url.strip()])
    for lang in ('en', 'kk'):
        d = {f: g('%s.%s' % (lang, f)) for f in ('name', 'city') + L.TEXT if g('%s.%s' % (lang, f))}
        if d: c[lang] = d
    return c

def export(path):
    from openpyxl import Workbook
    from openpyxl.comments import Comment
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    data = json.load(open(B + 'clinics.json', encoding='utf-8'))
    wb = Workbook(); ws = wb.active; ws.title = SHEET
    for j, (k, h, w, hint) in enumerate(COLS, 1):
        cell = ws.cell(row=1, column=j, value=h)
        cell.font = Font(bold=True); cell.alignment = Alignment(wrap_text=True, vertical='center')
        cell.fill = PatternFill('solid', fgColor='DDEBF7' if '.' not in k or k.startswith('tkm.') else 'EDEDED')
        cell.comment = Comment(hint, 'HemaBridge'); ws.column_dimensions[get_column_letter(j)].width = w
    for i, c in enumerate(data['clinics'], 2):
        r = to_row(c)
        for j, (k, _, _, _) in enumerate(COLS, 1):
            ws.cell(row=i, column=j, value=r.get(k, '')).alignment = Alignment(wrap_text=True, vertical='top')
    last = 500
    def dv(values, keys):
        v = DataValidation(type='list', formula1='"%s"' % ','.join(values), allow_blank=False, showErrorMessage=True,
                           errorTitle='Значение не из списка', error='Выберите значение из списка.')
        ws.add_data_validation(v)
        for k in keys:
            col = get_column_letter([x[0] for x in COLS].index(k) + 1)
            v.add('%s2:%s%d' % (col, col, last))
    dv(L.COUNTRIES, ['country']); dv([v[0] for v in L.STATUS.values()], ['status'])
    dv(L.TRI.values(), ['tkm.auto', 'tkm.allo', 'tkm.haplo', 'cart'])
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = 'A1:%s%d' % (get_column_letter(len(COLS)), max(2, len(data['clinics']) + 1))
    ws.row_dimensions[1].height = 34
    how = wb.create_sheet('Как заполнять'); how.column_dimensions['A'].width = 34; how.column_dimensions['B'].width = 110
    how['A1'] = 'Таблица клиник HemaBridge: как заполнять'; how['A1'].font = Font(bold=True, size=14)
    rows = [('Одна строка — одна клиника.', 'Порядок строк = порядок на сайте; страны выводятся группами в порядке первого появления.'),
            ('Пустое поле', 'На сайте показывается как «нет данных» — так видно, что сведений нет, а не что строку забыли.'),
            ('Сведения', 'Только с официального сайта клиники или государственного портала; ссылку — в «Источники». Без цен и обещаний результата.'),
            ('Переводы', 'Серые столбцы EN/KK. Если пусто, на английской и казахской версии останется русский текст.'),
            ('Публикация', 'Готовую таблицу передайте разработчику (файл или ссылка на Google Таблицу). Сборка проверит её и назовёт строку и столбец с ошибкой.')]
    rows += [(h, hint) for _, h, _, hint in COLS]
    for i, (a, b) in enumerate(rows, 3):
        how.cell(row=i, column=1, value=a).font = Font(bold=True)
        how.cell(row=i, column=2, value=b).alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(path); print('written', path, len(data['clinics']), 'clinics')

def read_rows(src):
    by_header = {h: k for k, h, _, _ in COLS}
    if src.startswith('https://'):
        text = urllib.request.urlopen(src, timeout=30).read().decode('utf-8-sig'); src = None
    elif src.lower().endswith('.csv'):
        text = open(src, encoding='utf-8-sig').read(); src = None
    if src is None:
        table = list(csv.reader(io.StringIO(text)))
    else:
        from openpyxl import load_workbook
        ws = load_workbook(src, data_only=True)[SHEET]
        table = [[('' if v is None else str(v)) for v in row] for row in ws.iter_rows(values_only=True)]
    head = [by_header.get((h or '').strip()) for h in table[0]]
    missing = [h for k, h, _, _ in COLS if k not in head]
    if missing: sys.exit('В таблице нет столбцов: ' + ', '.join(missing))
    for n, row in enumerate(table[1:], 2):
        if any((x or '').strip() for x in row):
            yield n, {k: row[j] if j < len(row) else '' for j, k in enumerate(head) if k}

def do_import(src):
    err, clinics = [], []
    for n, r in read_rows(src):
        clinics.append(from_row(r, n, err))
    old = json.load(open(B + 'clinics.json', encoding='utf-8'))
    data = {'_note': old.get('_note', ''), 'clinics': clinics}
    e2, warn = L.validate(data, where='строка %d', first=2)
    for w in warn: print('предупреждение:', w)
    if err or e2:
        print('Ошибки, clinics.json не изменён:'); [print('  ' + x) for x in err + e2]; sys.exit(1)
    with open(B + 'clinics.json', 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    print('clinics.json: %d clinics. Теперь: python build.py' % len(clinics))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['export']: export(a[1] if len(a) > 1 else B + 'clinics.xlsx')
    elif a[:1] == ['import'] and len(a) == 2: do_import(a[1])
    else: sys.exit(__doc__)

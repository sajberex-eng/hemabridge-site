# Search-engine and link-preview metadata. exec'd by build.py on the assembled string `s`
# (shares `rep`, `re`, `B`). The page stays noindex until launch; this only prepares what robots will read.
import json as _json
SITE = 'https://bridge.hemcenter.kz/'
_title = 'HemaBridge — лечение заболеваний крови за рубежом с врачом в Казахстане'
_desc = ('Трансплантация костного мозга и CAR-T за рубежом для пациентов из Казахстана: оценка гематолога, '
         'подготовка дома, выбор клиники, ведение после возвращения.')
_og_desc = 'Сначала врачебное решение. Затем — лечение. Где бы оно ни проходило.'

# the logo was inlined twice as base64 (favicon + header mark): serve it as a file instead
s, _n = re.subn(r'data:image/png;base64,[A-Za-z0-9+/=]+', 'img/logo.png', s)
assert _n == 2, _n

s = rep(s, '<title>HemaBridge — программа Центра гематологии</title>',
        '<title>%s</title>\n<link rel="canonical" href="%s">' % (_title, SITE))
s, _n = re.subn(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % _desc, s)
assert _n == 1, _n
s = rep(s, '<meta property="og:title" content="HemaBridge — программа Центра гематологии">',
        '<meta property="og:title" content="%s">' % _title)
s = rep(s, '<meta property="og:type" content="website">',
        '<meta property="og:type" content="website">\n'
        '<meta property="og:site_name" content="HemaBridge">\n'
        '<meta property="og:url" content="%s">\n'
        '<meta property="og:image" content="%simg/og.jpg">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta property="og:image:alt" content="HemaBridge — программа Центра гематологии. %s">\n'
        '<meta name="twitter:card" content="summary_large_image">' % (SITE, SITE, _og_desc))

# Organization data: only facts already published on the page (footer and «О Центре гематологии»)
_org = {
    '@context': 'https://schema.org',
    '@type': 'MedicalOrganization',
    '@id': SITE + '#program',
    'name': 'HemaBridge',
    'alternateName': 'HemaBridge — программа Центра гематологии',
    'url': SITE,
    'logo': SITE + 'img/logo.png',
    'image': SITE + 'img/og.jpg',
    'description': 'Программа врачей-гематологов и онкогематологов Центра гематологии: международная маршрутизация '
                   'пациентов с заболеваниями крови — оценка, подготовка в Казахстане, лечение за рубежом, персональное ведение у гематолога после возвращения.',
    'medicalSpecialty': 'Hematologic',
    'areaServed': {'@type': 'Country', 'name': 'Казахстан'},
    'availableLanguage': ['ru', 'kk', 'en'],
    'telephone': '+77770793165',
    'email': 'info@hemcenter.kz',
    'address': {'@type': 'PostalAddress', 'streetAddress': 'ул. Кенесары, 4Б',
                'addressLocality': 'Астана', 'addressCountry': 'KZ'},
    'parentOrganization': {'@type': 'MedicalClinic', 'name': 'ТОО «Центр гематологии»',
                           'url': 'https://hemcenter.kz/', 'sameAs': 'https://hemcenter.kz/'},
}
_a = s.index('<script type="application/ld+json">') + len('<script type="application/ld+json">')
_b = s.index('</script>', _a)
s = s[:_a] + '\n' + _json.dumps(_org, ensure_ascii=False) + '\n' + s[_b:]

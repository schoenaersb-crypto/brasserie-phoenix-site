#!/usr/bin/env python3
"""Pages statiques lisibles par Google ET par les IA (ChatGPT, Claude, Gemini, Perplexity).

Le site principal (docs/index.html) affiche son contenu en JavaScript : un robot qui ne
l'exécute pas ne voit presque rien. Ce script génère, à partir des mêmes fichiers data/*.json,
une page complète en HTML pur par langue (fr, es, en, nl), avec données structurées
schema.org (Restaurant, Menu, FAQ), liens hreflang, llms.txt et sitemap.

Relancer après chaque modification de la carte :  python3 scripts/build_seo.py
"""
import json, html, os, datetime

ROOT = os.path.join(os.path.dirname(__file__), '..', 'docs')
BASE = 'https://schoenaersb-crypto.github.io/brasserie-phoenix-site/'
LANGS = ['fr', 'es', 'en', 'nl']
D = lambda f: json.load(open(os.path.join(ROOT, 'data', f), encoding='utf-8'))
infos, carte, menu, esprit, sig = D('infos.json'), D('carte.json'), D('menu-degustation.json'), D('esprit.json'), D('signature.json')
e = html.escape

T = {
 'title': {'fr': 'Brasserie Phoenix — Restaurant face à la mer à Torrevieja | Viandes sur pierre, fruits de mer, Pâtes Maison',
           'es': 'Brasserie Phoenix — Restaurante frente al mar en Torrevieja | Carne a la piedra, marisco y pasta fresca',
           'en': 'Brasserie Phoenix — Seafront restaurant in Torrevieja | Stone-grilled meat, seafood & fresh pasta',
           'nl': 'Brasserie Phoenix — Restaurant aan zee in Torrevieja | Vlees op steen, zeevruchten & verse pasta'},
 'desc': {'fr': 'Brasserie franco-belge bistronomique face à la Méditerranée à Torrevieja (Alicante) : viandes grillées sur pierre de lave, fruits de mer, Pâtes Maison, Menu Dégustation 5 temps à 37,50 €. Ouvert du jeudi au mardi, midi et soir.',
          'es': 'Brasserie franco-belga bistronómica frente al Mediterráneo en Torrevieja (Alicante): carne a la piedra volcánica, marisco, pasta fresca casera y Menú Degustación de 5 tiempos por 37,50 €. Abierto de jueves a martes, mediodía y noche.',
          'en': 'French-Belgian bistronomic brasserie facing the Mediterranean in Torrevieja (Alicante): meat grilled on lava stone, seafood, homemade fresh pasta and a 5-course Tasting Menu at €37.50. Open Thursday to Tuesday, lunch and dinner.',
          'nl': 'Frans-Belgische bistronomische brasserie aan de Middellandse Zee in Torrevieja (Alicante): vlees op lavasteen, zeevruchten, huisgemaakte verse pasta en een 5-gangen degustatiemenu voor € 37,50. Open van donderdag tot dinsdag, lunch en diner.'},
 'h1': {'fr': 'Brasserie Phoenix, restaurant face à la mer à Torrevieja',
        'es': 'Brasserie Phoenix, restaurante frente al mar en Torrevieja',
        'en': 'Brasserie Phoenix, seafront restaurant in Torrevieja',
        'nl': 'Brasserie Phoenix, restaurant aan zee in Torrevieja'},
 'intro': {'fr': 'Une brasserie franco-belge bistronomique posée face à la Méditerranée : viandes grillées à votre table sur pierre de lave, fruits de mer, Pâtes Maison et un Menu Dégustation en 5 temps. Terrasse vitrée avec vue sur la mer et couchers de soleil.',
           'es': 'Una brasserie franco-belga bistronómica frente al Mediterráneo: carnes a la piedra volcánica en su mesa, marisco, pasta fresca casera y un Menú Degustación en 5 tiempos. Terraza acristalada con vistas al mar y puestas de sol.',
           'en': 'A French-Belgian bistronomic brasserie facing the Mediterranean: meat grilled at your table on lava stone, seafood, homemade fresh pasta and a 5-course Tasting Menu. Glass-walled terrace with sea views and sunsets.',
           'nl': 'Een Frans-Belgische bistronomische brasserie aan de Middellandse Zee: vlees aan tafel gegrild op lavasteen, zeevruchten, huisgemaakte verse pasta en een degustatiemenu in 5 gangen. Overdekt terras met zeezicht en zonsondergangen.'},
 'book': {'fr': 'Réserver une table', 'es': 'Reservar mesa', 'en': 'Book a table', 'nl': 'Tafel reserveren'},
 'call': {'fr': 'Appeler', 'es': 'Llamar', 'en': 'Call', 'nl': 'Bellen'},
 'full': {'fr': 'Voir le site complet', 'es': 'Ver la web completa', 'en': 'See the full website', 'nl': 'Volledige website'},
 'carte': {'fr': 'La carte', 'es': 'La carta', 'en': 'The menu', 'nl': 'De kaart'},
 'hours': {'fr': 'Horaires', 'es': 'Horario', 'en': 'Opening hours', 'nl': 'Openingstijden'},
 'where': {'fr': 'Adresse et accès', 'es': 'Dirección y acceso', 'en': 'Address & directions', 'nl': 'Adres en route'},
 'faq': {'fr': 'Questions fréquentes', 'es': 'Preguntas frecuentes', 'en': 'Frequently asked questions', 'nl': 'Veelgestelde vragen'},
 'sign': {'fr': 'Nos plats signature', 'es': 'Nuestros platos estrella', 'en': 'Signature dishes', 'nl': 'Signatuurgerechten'},
 'map': {'fr': 'Itinéraire Google Maps', 'es': 'Cómo llegar (Google Maps)', 'en': 'Directions (Google Maps)', 'nl': 'Route (Google Maps)'},
 'cdc': {'fr': 'Coup de cœur', 'es': 'Nuestro favorito', 'en': "Chef's Favourite", 'nl': 'Favoriet van de chef'},
}
FAQ = {
 'fr': [('Où se trouve la Brasserie Phoenix ?', "Av. Desiderio Rodríguez 37, local 10, 03185 Torrevieja (Alicante, Espagne), en bord de mer, avec une terrasse vitrée face à la Méditerranée."),
        ("Quels sont les horaires ?", "Du jeudi au mardi, midi et soir ; fermé le mercredi. Cuisine de 12 h à 15 h et de 18 h à 22 h ; bar et salle de 11 h à minuit."),
        ("Quel type de cuisine ?", "Une cuisine franco-belge bistronomique : viandes grillées sur pierre de lave (bœuf galicien, argentin, belge, porc Duroc), fruits de mer, poissons, Pâtes Maison et desserts maison."),
        ("Y a-t-il un menu dégustation ?", "Oui : le Menu Dégustation en 5 temps à 37,50 € (Saint-Jacques snackées à la Tripel Karmeliet, demi foie gras poêlé, salade fraîcheur, bar entier ou demi magret, poire au vin), avec accords vins en 3 ou 5 verres."),
        ("Comment réserver ?", "Par téléphone ou WhatsApp au +34 744 62 29 75, ou depuis notre site."),
        ("Y a-t-il un menu enfant ?", "Oui, des plats enfants à 12 € (burger, nuggets, pâtes)."),
        ("Que se passe-t-il le mardi soir ?", "Soirée spéciale avec DJ Kavari, avec la carte complète.")],
 'es': [('¿Dónde está la Brasserie Phoenix?', 'En la Av. Desiderio Rodríguez 37, local 10, 03185 Torrevieja (Alicante), en primera línea de mar, con terraza acristalada frente al Mediterráneo.'),
        ('¿Cuál es el horario?', 'De jueves a martes, mediodía y noche; cerrado los miércoles. Cocina de 12:00 a 15:00 y de 18:00 a 22:00; bar y sala de 11:00 a 00:00.'),
        ('¿Qué tipo de cocina tienen?', 'Cocina franco-belga bistronómica: carnes a la piedra volcánica (ternera gallega, argentina, belga, cerdo Duroc), marisco, pescado, pasta fresca casera y postres caseros.'),
        ('¿Tienen menú degustación?', 'Sí: Menú Degustación de 5 tiempos por 37,50 € (vieiras con reducción de Tripel Karmeliet, medio foie gras a la plancha, ensalada fresca, lubina entera o medio magret, pera al vino), con maridaje de 3 o 5 copas.'),
        ('¿Cómo reservar?', 'Por teléfono o WhatsApp al +34 744 62 29 75, o desde nuestra web.'),
        ('¿Hay menú infantil?', 'Sí, platos infantiles a 12 € (hamburguesa, nuggets, pasta).'),
        ('¿Qué pasa los martes por la noche?', 'Velada especial con DJ Kavari, con la carta completa.')],
 'en': [('Where is Brasserie Phoenix?', 'Av. Desiderio Rodríguez 37, local 10, 03185 Torrevieja (Alicante, Spain), right on the seafront, with a glass-walled terrace facing the Mediterranean.'),
        ('What are the opening hours?', 'Thursday to Tuesday, lunch and dinner; closed on Wednesdays. Kitchen 12:00–15:00 and 18:00–22:00; bar and dining room 11:00–midnight.'),
        ('What kind of food do you serve?', 'French-Belgian bistronomic cooking: meat grilled on lava stone (Galician, Argentinian and Belgian beef, Duroc pork), seafood, fish, homemade fresh pasta and homemade desserts.'),
        ('Do you have a tasting menu?', 'Yes: a 5-course Tasting Menu at €37.50 (seared scallops with Tripel Karmeliet reduction, pan-fried half foie gras, fresh salad, whole sea bass or half duck breast, pear in wine), with 3 or 5 glass wine pairings.'),
        ('How do I book?', 'By phone or WhatsApp on +34 744 62 29 75, or through our website.'),
        ("Is there a children's menu?", "Yes, children's dishes at €12 (burger, nuggets, pasta)."),
        ('What happens on Tuesday evenings?', 'A special night with DJ Kavari, with the full menu available.')],
 'nl': [('Waar ligt Brasserie Phoenix?', 'Av. Desiderio Rodríguez 37, local 10, 03185 Torrevieja (Alicante, Spanje), direct aan zee, met een overdekt terras aan de Middellandse Zee.'),
        ('Wat zijn de openingstijden?', 'Van donderdag tot dinsdag, lunch en diner; gesloten op woensdag. Keuken 12:00–15:00 en 18:00–22:00; bar en zaal 11:00–00:00.'),
        ('Welke keuken?', 'Frans-Belgische bistronomische keuken: vlees op lavasteen (Galicisch, Argentijns en Belgisch rundvlees, Duroc-varken), zeevruchten, vis, huisgemaakte verse pasta en desserts.'),
        ('Is er een degustatiemenu?', 'Ja: een degustatiemenu in 5 gangen voor € 37,50 (Sint-Jakobsvruchten met Tripel Karmeliet-reductie, gebakken halve foie gras, frisse salade, hele zeebaars of halve eendenborst, peer in wijn), met wijnarrangement van 3 of 5 glazen.'),
        ('Hoe reserveren?', 'Telefonisch of via WhatsApp op +34 744 62 29 75, of via onze website.'),
        ('Is er een kindermenu?', 'Ja, kindergerechten voor € 12 (burger, nuggets, pasta).'),
        ('Wat gebeurt er op dinsdagavond?', 'Een speciale avond met DJ Kavari, met de volledige kaart.')],
}

def price(it):
    if it.get('prix'): return it['prix']
    pt = it.get('prix_texte'); return pt if isinstance(pt, str) else (pt or {}).get('fr', '')

def L(x, lg):
    if isinstance(x, dict): return x.get(lg) or x.get('fr') or ''
    return x or ''

def num(p):
    try: return float(str(p).replace('€', '').replace(',', '.').strip())
    except Exception: return None

def jsonld(lg):
    url = f'{BASE}{lg}/'
    sections = []
    for c in carte['categories']:
        items = []
        for it in c['items']:
            m = {'@type': 'MenuItem', 'name': L(it['nom'], lg)}
            d = L(it.get('desc'), lg)
            if d: m['description'] = d
            n = num(it.get('prix'))
            if n: m['offers'] = {'@type': 'Offer', 'price': f'{n:.2f}', 'priceCurrency': 'EUR'}
            items.append(m)
        sections.append({'@type': 'MenuSection', 'name': L(c['nom'], lg), 'hasMenuItem': items})
    sections.append({'@type': 'MenuSection', 'name': L(menu['titre'], lg),
                     'hasMenuItem': [{'@type': 'MenuItem', 'name': L(menu['titre'], lg) + ' — ' + L(menu['sous_titre'], lg),
                                      'offers': {'@type': 'Offer', 'price': '37.50', 'priceCurrency': 'EUR'}}]})
    rest = {
        '@context': 'https://schema.org', '@type': 'Restaurant', '@id': BASE + '#restaurant',
        'name': 'Brasserie Phoenix', 'url': BASE, 'mainEntityOfPage': url,
        'image': [BASE + 'assets/img/hero/hero-facade-coucher-soleil.jpg', BASE + esprit['image']],
        'logo': BASE + 'assets/img/phoenix-logo.png',
        'description': T['desc'][lg],
        'servesCuisine': ['French', 'Belgian', 'Mediterranean', 'Seafood', 'Steakhouse', 'Italian (fresh pasta)', 'Bistronomy'],
        'priceRange': '€€', 'telephone': '+34 744 62 29 75', 'email': 'brasseriephoenixrestaurant@gmail.com',
        'acceptsReservations': True, 'currenciesAccepted': 'EUR', 'inLanguage': lg,
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Av. Desiderio Rodríguez, 37, local 10', 'addressLocality': 'Torrevieja',
                    'addressRegion': 'Alicante', 'postalCode': '03185', 'addressCountry': 'ES'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': 37.9772, 'longitude': -0.6785},
        'hasMap': infos['maps'],
        'areaServed': ['Torrevieja', 'Orihuela Costa', 'La Mata', 'Guardamar del Segura', 'Costa Blanca'],
        'amenityFeature': [{'@type': 'LocationFeatureSpecification', 'name': n, 'value': True} for n in ('Sea view', 'Terrace', 'Glass-walled terrace')],
        'sameAs': list(infos['reseaux'].values()),
        'openingHoursSpecification': [
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday'], 'opens': '12:00', 'closes': '15:00'},
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday'], 'opens': '18:00', 'closes': '22:00'}],
        'hasMenu': {'@type': 'Menu', 'name': T['carte'][lg], 'inLanguage': lg, 'hasMenuSection': sections},
    }
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage',
           'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ[lg]]}
    return [rest, faq]

CSS = """body{margin:0;font-family:Jost,Arial,'Liberation Sans',sans-serif;background:#F6F0E4;color:#16364A;line-height:1.55}
header{background:#16364A;color:#F6F0E4;padding:28px 20px;text-align:center}header img{height:84px}
h1{font-family:'Cormorant Garamond',Georgia,serif;font-weight:600;font-size:2rem;margin:.4em 0}
h2{font-family:'Cormorant Garamond',Georgia,serif;color:#16364A;border-bottom:2px solid #D4A843;padding-bottom:4px;margin-top:2em}
h3{color:#B98D55;margin:1.4em 0 .4em}main{max-width:820px;margin:auto;padding:10px 20px 40px}
.cta{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin:16px 0}.cta a{background:#D4A843;color:#16364A;padding:12px 18px;border-radius:999px;text-decoration:none;font-weight:600}
.cta a.sec{background:transparent;color:#F6F0E4;border:1px solid #D4A843}nav.lg a{color:#D4A843;margin:0 6px}
.it{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid #e3d9c4}.it small{display:block;color:#5b6b75}
.tag{font-size:.75rem;color:#B98D55;margin-left:6px}img.hero{width:100%;border-radius:12px;margin-top:16px}footer{text-align:center;color:#5b6b75;font-size:.9rem;padding:30px}"""

def page(lg):
    url = f'{BASE}{lg}/'; o = []
    alt = ''.join(f'<link rel="alternate" hreflang="{x}" href="{BASE}{x}/">' for x in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{BASE}es/">'
    o.append(f'<!DOCTYPE html><html lang="{lg}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
             f'<title>{e(T["title"][lg])}</title><meta name="description" content="{e(T["desc"][lg])}"><link rel="canonical" href="{url}">{alt}'
             f'<meta property="og:type" content="restaurant"><meta property="og:title" content="{e(T["title"][lg])}"><meta property="og:description" content="{e(T["desc"][lg])}">'
             f'<meta property="og:image" content="{BASE}assets/img/hero/hero-facade-coucher-soleil.jpg"><meta property="og:url" content="{url}">'
             f'<meta name="geo.region" content="ES-A"><meta name="geo.placename" content="Torrevieja"><meta name="geo.position" content="37.9772;-0.6785">'
             f'<link rel="icon" href="../assets/img/phoenix-logo.png"><style>{CSS}</style>')
    for j in jsonld(lg): o.append('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False) + '</script>')
    o.append('</head><body><header>')
    o.append(f'<img src="../assets/img/phoenix-logo.png" alt="Logo Brasserie Phoenix"><h1>{e(T["h1"][lg])}</h1>')
    o.append('<nav class="lg">' + ' '.join(f'<a href="../{x}/" hreflang="{x}">{x.upper()}</a>' for x in LANGS) + '</nav>')
    o.append(f'<div class="cta"><a href="https://wa.me/{infos["telephone_wa"]}">{T["book"][lg]} · WhatsApp</a><a class="sec" href="tel:+34744622975">{T["call"][lg]} +34 744 62 29 75</a><a class="sec" href="../">{T["full"][lg]}</a></div></header><main>')
    o.append(f'<p>{e(T["intro"][lg])}</p><img class="hero" src="../{e(esprit["image"])}" alt="{e(L(esprit["image_alt"], lg))}" loading="lazy">')
    o.append(f'<h2>{e(L(esprit["titre"], lg))}</h2>' + ''.join(f'<p>{e(L(p, lg))}</p>' for p in esprit['paragraphes']))
    o.append(f'<h2>{T["sign"][lg]}</h2>')
    for p in sig['plats']:
        o.append(f'<div class="it"><div><strong>{e(L(p["nom"], lg))}</strong><small>{e(L(p.get("desc"), lg))}</small></div><span>{e(p.get("prix") or L(p.get("prix_texte"), lg))}</span></div>')
    o.append(f'<h2>{e(L(menu["titre"], lg))} — {e(L(menu["prix"], lg))}</h2><p>{e(L(menu["sous_titre"], lg))} · {e(L(menu.get("prix_note"), lg))}</p>')
    for t in menu['temps']:
        if t.get('choix'):
            opts = f' {L(menu["choix_ou"], lg)} '.join(f'{L(c["nom"], lg)} ({L(c.get("desc"), lg)})' for c in t['items'])
            o.append(f'<div class="it"><div><strong>{t["num"]}. {e(L(t["label"], lg))}</strong><small>{e(opts)}</small></div></div>')
        else:
            o.append(f'<div class="it"><div><strong>{t["num"]}. {e(L(t["nom"], lg))}</strong><small>{e(L(t.get("desc"), lg))}</small></div></div>')
    o.append(f'<h2>{T["carte"][lg]}</h2>')
    for c in carte['categories']:
        o.append(f'<h3>{e(L(c["nom"], lg))}</h3>')
        if c.get('note'): o.append(f'<p><small>{e(L(c["note"], lg))}</small></p>')
        for it in c['items']:
            tag = f'<span class="tag">◆ {T["cdc"][lg]}</span>' if it.get('coup_de_coeur') else ''
            sub = ' · '.join(x for x in (L(it.get('desc'), lg), L(it.get('origine'), lg)) if x)
            pr = it.get('prix') or L(it.get('prix_texte'), lg)
            o.append(f'<div class="it"><div><strong>{e(L(it["nom"], lg))}</strong>{tag}<small>{e(sub)}</small></div><span>{e(pr)}</span></div>')
    o.append(f'<h2>{T["hours"][lg]}</h2><p>{e(L(infos["horaires"]["note"], lg))}</p>')
    for b in infos['horaires']['blocs']:
        o.append(f'<h3>{e(L(b["titre"], lg))}</h3>' + ''.join(f'<div class="it"><span>{e(L(r["jours"], lg))}</span><span>{e(L(r["heures"], lg))}</span></div>' for r in b['lignes']))
    o.append(f'<h2>{T["where"][lg]}</h2><p>Brasserie Phoenix<br>{e(infos["adresse"])}<br>+34 744 62 29 75 · {e(infos["email"])}</p><p><a href="{e(infos["maps"])}">{T["map"][lg]}</a></p>')
    o.append(f'<h2>{T["faq"][lg]}</h2>' + ''.join(f'<h3>{e(q)}</h3><p>{e(a)}</p>' for q, a in FAQ[lg]))
    o.append(f'</main><footer>© Brasserie Phoenix S.L. · Torrevieja · ' + ' · '.join(f'<a href="{e(u)}">{k.capitalize()}</a>' for k, u in infos['reseaux'].items()) + '</footer></body></html>')
    return ''.join(o)

def llms():
    out = ['# Brasserie Phoenix — Torrevieja (Costa Blanca, Spain)', '',
           '> French-Belgian bistronomic brasserie on the seafront in Torrevieja (Alicante, Spain): meat grilled at the table on lava stone, seafood, homemade fresh pasta, 5-course Tasting Menu at €37.50, glass-walled terrace facing the Mediterranean.', '',
           '- Address: Av. Desiderio Rodríguez 37, local 10, 03185 Torrevieja, Alicante, Spain',
           '- Phone / WhatsApp (reservations): +34 744 62 29 75', f'- Email: {infos["email"]}',
           '- Open: Thursday to Tuesday, lunch (kitchen 12:00–15:00) and dinner (kitchen 18:00–22:00); closed Wednesday. Bar 11:00–00:00.',
           '- Tuesday evening: special night with DJ Kavari (full menu).',
           '- Languages of the website: French, Spanish, English, Dutch.', '- Price range: €€ (starters €10–21, mains €18–41, desserts €8–13).', '',
           '## Pages', ''] + [f'- [{lg.upper()}]({BASE}{lg}/): {T["title"][lg]}' for lg in LANGS] + ['', '## Menu (prices in EUR)', '']
    for c in carte['categories']:
        out.append(f'### {L(c["nom"], "en")}')
        for it in c['items']:
            out.append(f'- {L(it["nom"], "en")} — {it.get("prix") or L(it.get("prix_texte"), "en")}' + (f' — {L(it.get("desc"), "en")}' if L(it.get('desc'), 'en') else ''))
        out.append('')
    out += ['## Good to know', ''] + [f'- {q} {a}' for q, a in FAQ['en']] + ['', f'Updated: {datetime.date.today().isoformat()}']
    return '\n'.join(out) + '\n'

def sitemap():
    today = datetime.date.today().isoformat()
    xs = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{BASE}{x}/"/>' for x in LANGS)
    xs.append(f'<url><loc>{BASE}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority><image:image><image:loc>{BASE}assets/img/hero/hero-facade-coucher-soleil.jpg</image:loc></image:image></url>')
    for lg in LANGS: xs.append(f'<url><loc>{BASE}{lg}/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority>{alts}</url>')
    xs.append('</urlset>'); return '\n'.join(xs) + '\n'

if __name__ == '__main__':
    for lg in LANGS:
        os.makedirs(os.path.join(ROOT, lg), exist_ok=True)
        open(os.path.join(ROOT, lg, 'index.html'), 'w', encoding='utf-8').write(page(lg))
    open(os.path.join(ROOT, 'llms.txt'), 'w', encoding='utf-8').write(llms())
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(sitemap())
    print('ok', [os.path.getsize(os.path.join(ROOT, lg, 'index.html')) for lg in LANGS])

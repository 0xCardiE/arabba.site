#!/usr/bin/env python3
"""Apply brand-page upgrades: content, JSON-LD, og:image, contact strip, messengers."""
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://arabba.hr"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=Crn%C4%8Di%C4%87eva+4,+51000+Rijeka"
WORKING_HOURS = "Pon–Pet 8:00–16:00"

MESSENGER_LINKS = (
    '<span class="messenger-links">'
    '<a href="https://wa.me/38598257032" class="messenger-link messenger-whatsapp" '
    'aria-label="Pošaljite WhatsApp poruku">'
    '<img src="images/icon-whatsapp.svg" width="28" height="28" alt="">'
    '<span>WhatsApp</span></a>'
    '<a href="viber://chat?number=38598257032" class="messenger-link messenger-viber" '
    'aria-label="Pošaljite Viber poruku">'
    '<img src="images/icon-viber.svg" width="28" height="28" alt="">'
    '<span>Viber</span></a>'
    "</span>"
)

STICKY_CALL = (
    '<a href="tel:+38598257032" class="sticky-call-btn" aria-label="Nazovite nas">'
    '<span class="sticky-call-label">Nazovite</span>'
    '<span class="sticky-call-number">098 257 032</span>'
    "</a>"
)

COMMON_REPAIRS = """<ul>
<li>Čišćenje ventilatora i zamjena termalne paste (pregrijavanje, bučni ventilatori)</li>
<li>Zamjena ekrana, tipkovnice, baterije i šarki</li>
<li>Popravak punjenja i zamjena DC konektora</li>
<li>Nadogradnja SSD-a i RAM-a</li>
<li>Instalacija ili reinstalacija operativnog sustava</li>
<li>Spašavanje podataka s oštećenog diska</li>
</ul>"""

COMMON_PROCESS = """<ol>
<li><strong>Donesete uređaj</strong> u servis na Crnčićevoj 4 ili nas nazovete za savjet.</li>
<li><strong>Dijagnostika</strong>: utvrdimo kvar i javimo procjenu cijene.</li>
<li><strong>Popravak</strong>: nakon vašeg odobrenja zamjenjujemo dijelove ili čistimo sustav.</li>
<li><strong>Testiranje i predaja</strong>: provjerimo da sve radi prije vraćanja uređaja.</li>
</ol>"""

BRAND_PAGES = {
    "msi-servis-laptopa-rijeka.html": {
        "og_image": "images/msi_servis.jpeg",
        "og_width": "480",
        "og_height": "384",
        "service_name": "Servis MSI laptopa",
        "breadcrumb": "MSI",
        "hero_message": "MSI laptop vam se pregrijava, ne pali se ili trebate zamjenu dijela? Javite nam se, servisiramo gaming i poslovne modele u Rijeci.",
        "intro": (
            "<p>MSI (Micro-Star International) poznat je po gaming laptopovima i kvalitetnim "
            "matičnim pločama. Arabba nudi kompletan servis MSI laptopa u Rijeci: od čišćenja "
            "pregrijavanja do zamjene ekrana, tipkovnice i SSD-a.</p>"
        ),
        "models": (
            "<p>Servisiramo popularne serije: <strong>Katana</strong>, <strong>Cyborg</strong>, "
            "<strong>Raider</strong>, <strong>Modern</strong>, <strong>Prestige</strong> i druge "
            "MSI modele. Gaming laptopi često zahtijevaju temeljito čišćenje rashladnog sustava, "
            "to je jedan od najčešćih razloga zašto nas korisnici kontaktiraju.</p>"
        ),
        "faq": [
            ("Koliko traje servis MSI laptopa?", "Jednostavno čišćenje i manji popravci često isti dan. Zamjena ekrana ili matične ploče obično traje 2–5 radnih dana, ovisno o dostupnosti dijela."),
            ("Zašto se MSI laptop pregrijava?", "Najčešći uzrok je zaprljanje ventilatora i stara termalna pasta. Redovito čišćenje produžuje vijek trajanja i vraća performanse."),
            ("Servisirate li MSI gaming laptope?", "Da, imamo iskustvo s gaming modelima koji rade pod opterećenjem i brzo se pregrijavaju bez održavanja."),
            ("Hoćete li sačuvati moje podatke?", "Da, podatke čuvamo koliko god je tehnički moguće. Pri spašavanju podataka s oštećenog diska prvo procjenjujemo stanje."),
        ],
    },
    "apple-servis-rijeka.html": {
        "og_image": "images/mac-line-up1.jpg",
        "og_width": "480",
        "og_height": "283",
        "service_name": "Apple servis",
        "breadcrumb": "Apple",
        "hero_message": "MacBook, iMac ili Mac mini ne radi kako treba? Nudimo dijagnostiku, zamjenu dijelova, čišćenje i spašavanje podataka za Apple uređaje u Rijeci.",
        "intro": (
            "<p>Nudimo servis Apple računala, MacBook Pro, MacBook Air, iMac, Mac mini i Mac Pro. "
            "Obavljamo dijagnostiku, zamjenu komponenti, čišćenje rashladnog sustava, instalaciju "
            "macOS-a te backup i spašavanje podataka.</p>"
        ),
        "models": (
            "<p>Radimo na svim generacijama MacBook Pro i Air, iMac stolnim računalima te Mac mini "
            "modelima. Bilo da je riječ o sporom Macu, punjenju koje ne radi ili oštećenom ekranu, "
            "prvo utvrdimo kvar, pa predložimo najisplativije rješenje.</p>"
        ),
        "faq": [
            ("Servisirate li MacBook Pro i Air?", "Da, servisiramo sve generacije MacBook Pro i MacBook Air, uključujući modele s Retina ekranom."),
            ("Možete li instalirati macOS?", "Da, obavljamo čistu instalaciju macOS-a, migraciju podataka i nadogradnju SSD-a za brži rad."),
            ("Koliko traje Apple servis?", "Dijagnostika je brza, a jednostavniji popravci često isti dan. Složeniji hardverski zahvati traju nekoliko radnih dana."),
            ("Hoćete li sačuvati moje podatke?", "Da, prije svakog zahvata dogovorimo backup. Spašavanje podataka s oštećenog diska također nudimo."),
        ],
    },
    "servis-hp-laptopa-rijeka.html": {
        "og_image": "images/hp_servis.jpg",
        "og_width": "480",
        "og_height": "339",
        "service_name": "Servis HP laptopa",
        "breadcrumb": "HP",
        "hero_message": "HP laptop se pregrijava, ne pali se ili trebate zamjenu dijela? Servisiramo Pavilion, ProBook i EliteBook modele u Rijeci.",
        "intro": (
            "<p>HP (Hewlett-Packard) jedna je od najzastupljenijih marki laptopa u regiji. "
            "Servisiramo serije Pavilion, ProBook i EliteBook, od dijagnostike do zamjene "
            "komponenti i čišćenja rashladnog sustava.</p>"
        ),
        "models": (
            "<p>HP laptopi često imaju problem s pregrijavanjem zbog zaprljanih ventilatora. "
            "Višegodišnje iskustvo s HP modelima omogućuje nam brzu dijagnostiku i popravak. "
            "Uslugu možete zatražiti u Rijeci i okolici.</p>"
        ),
        "faq": [
            ("Zašto se HP laptop pregrijava?", "Najčešće zbog prašine u ventilatorima i stare termalne paste. Temeljito čišćenje obično riješi problem."),
            ("Servisirate li HP ProBook i EliteBook?", "Da, radimo na poslovnim i kućnim HP modelima, uključujući zamjenu ekrana, tipkovnica i baterija."),
            ("Koliko traje popravak?", "Manji popravci isti dan, složeniji 2–5 radnih dana ovisno o dijelovima."),
            ("Dajete li garanciju na popravak?", "Da, na ugrađene dijelove i obavljeni rad dajemo garanciju."),
        ],
    },
    "servis-lenovo-laptopa-rijeka.html": {
        "og_image": "images/lenovo_servis.jpg",
        "og_width": "480",
        "og_height": "360",
        "service_name": "Servis Lenovo laptopa",
        "breadcrumb": "Lenovo",
        "hero_message": "Lenovo ThinkPad ili drugi model ne radi kako treba? Nudimo dijagnostiku, čišćenje i popravak Lenovo laptopa u Rijeci.",
        "intro": (
            "<p>Lenovo, posebno ThinkPad serija, poznat je po izdržljivosti i kvaliteti tipkovnice. "
            "Arabba godinama servisira Lenovo laptope, pronalazi i otklanja kvarove, čisti "
            "sustav i popravlja oštećene dijelove.</p>"
        ),
        "models": (
            "<p>Radimo na ThinkPad, IdeaPad, Legion i ostalim Lenovo serijama. Bilo da je "
            "tipkovnica odbila službu, ekran pukao ili laptop spor, pronaći ćemo rješenje.</p>"
        ),
        "faq": [
            ("Servisirate li ThinkPad laptope?", "Da, ThinkPad je jedna od najčešćih serija koje servisiramo, uključujući poslovne modele."),
            ("Možete li zamijeniti ThinkPad tipkovnicu?", "Da, zamjena tipkovnice i ekrana redovit je posao u našem servisu."),
            ("Koliko traje dijagnostika?", "Dijagnostiku obavljamo odmah po primitku uređaja, a cijenu popravka dogovaramo prije rada."),
            ("Radite li u Rijeci i okolici?", "Da, servis je u Rijeci na Crnčićevoj 4, a po dogovoru dolazimo i u okolna mjesta."),
        ],
    },
    "servis-asus-laptopa-rijeka.html": {
        "og_image": "images/asus_servis.jpg",
        "og_width": "480",
        "og_height": "276",
        "service_name": "Servis ASUS laptopa",
        "breadcrumb": "ASUS",
        "hero_message": "ASUS laptop treba servis, čišćenje ili nadogradnju? Radimo na serijama N, VivoBook, ZenBook i ROG modelima u Rijeci.",
        "intro": (
            "<p>Asus nudi laptope svih cjenovnih razreda, od multimedijskih N serija do "
            "ROG gaming modela. U servisu obavljamo dijagnostiku, čišćenje, nadogradnju "
            "i popravak svih ASUS dijelova.</p>"
        ),
        "models": (
            "<p>Servisiramo serije N, S, K, G, U, X, VivoBook, ZenBook i ROG. Kao i kod "
            "drugih marki, redovito čišćenje sprječava pregrijavanje i produžuje vijek trajanja.</p>"
        ),
        "faq": [
            ("Servisirate li ASUS ROG gaming laptope?", "Da, imamo iskustvo s gaming modelima koji zahtijevaju redovito čišćenje rashladnog sustava."),
            ("Možete li nadograditi ASUS laptop?", "Da, nudimo nadogradnju SSD-a i RAM-a za brži rad."),
            ("Koliko košta dijagnostika?", "Procjenu cijene dajemo nakon pregleda uređaja, prije početka popravka."),
            ("Hoćete li sačuvati moje podatke?", "Da, podatke čuvamo koliko god je moguće pri svakom zahvatu."),
        ],
    },
    "servis-acer-laptopa-rijeka.html": {
        "og_image": "images/acer_servis.jpg",
        "og_width": "400",
        "og_height": "300",
        "service_name": "Servis Acer laptopa",
        "breadcrumb": "Acer",
        "hero_message": "Acer laptop ne radi kako treba? Servisiramo Aspire, TravelMate, Extensa i druge modele u Rijeci.",
        "intro": (
            "<p>Acer nudi širok spektar laptopa, od Aspire i Iconia serija za svakodnevnu "
            "upotrebu do TravelMate i Extensa poslovnih modela. U našem servisu riješit ćemo "
            "sve probleme u radu vašeg Acer laptopa.</p>"
        ),
        "models": (
            "<p>Radimo na Aspire, TravelMate, Extensa, Nitro gaming seriji i ostalim Acer "
            "modelima. Uslugu je moguće dobiti u Rijeci i okolici.</p>"
        ),
        "faq": [
            ("Servisirate li Acer Aspire laptope?", "Da, Aspire je jedna od najzastupljenijih serija koje servisiramo."),
            ("Što ako se laptop ne pali?", "Prvo provjerimo napajanje, bateriju i matičnu ploču, dijagnostika otkriva stvarni uzrok."),
            ("Koliko traje popravak?", "Manji kvarovi isti dan, zamjena dijelova obično nekoliko radnih dana."),
            ("Dajete li garanciju?", "Da, na ugrađene dijelove i obavljeni rad."),
        ],
    },
    "servis-toshiba-laptopa-rijeka.html": {
        "og_image": "images/toshiba_servis.jpg",
        "og_width": "480",
        "og_height": "313",
        "service_name": "Servis Toshiba laptopa",
        "breadcrumb": "Toshiba",
        "hero_message": "Toshiba laptop treba popravak ili čišćenje? Servisiramo Satellite, Portégé, Tecra i Qosmio modele u Rijeci.",
        "intro": (
            "<p>Toshiba je poznata po Satellite, Portégé, Tecra i Qosmio serijama. "
            "Nudimo brz i efikasan servis Toshiba laptopa, dijagnostiku, zamjenu dijelova "
            "i spašavanje podataka.</p>"
        ),
        "models": (
            "<p>Radimo na Satellite modelima za svakodnevnu upotrebu, Portégé ultraportabilima "
            "te Tecra poslovnim serijama. Kontaktirajte nas za bilo koji kvar.</p>"
        ),
        "faq": [
            ("Servisirate li Toshiba Satellite?", "Da, Satellite je jedna od serija koju redovito servisiramo."),
            ("Možete li spašiti podatke?", "Da, nudimo spašavanje podataka s oštećenih diskova prije ili tijekom popravka."),
            ("Koliko traje servis?", "Ovisi o kvaru, jednostavni popravci isti dan, složeniji nekoliko dana."),
            ("Radite li zamjenu ekrana?", "Da, zamjena ekrana, tipkovnice i baterije uobičajeni su popravci."),
        ],
    },
    "servis-i-popravak-laptopa-rijeka.html": {
        "og_image": "images/shutterstock_104383757.jpg",
        "og_width": "480",
        "og_height": "322",
        "service_name": "Servis i popravak laptopa",
        "breadcrumb": "Servis laptopa",
        "hero_message": "Imate razbijen laptop, trebate dijelove ili spašavanje podataka. Obratite nam se, servisiramo PC i Mac laptope u Rijeci.",
        "intro": (
            "<p>Vršimo dijagnostiku kvarova svih vrsta laptopa: zamjenu dijelova, nadogradnju, "
            "instalaciju operativnih sustava i spašavanje podataka. Ako je popravak isplativ, "
            "nabavljamo dijelove i zamjenjujemo ih u najkraćem roku.</p>"
        ),
        "models": (
            "<p>Servisiramo HP, Lenovo, ASUS, Acer, Toshiba, MSI, Apple MacBook i ostale marke. "
            "Ako vam laptop radi sporo i pregrijava se, nazovite, naći ćemo rješenje. "
            "Radimo na području Rijeke i okolice.</p>"
        ),
        "faq": [
            ("Servisirate li sve marke laptopa?", "Da, radimo na PC i Mac laptopovima svih proizvođača."),
            ("Koliko traje popravak laptopa?", "Jednostavni popravci isti dan, složeniji 2–5 radnih dana."),
            ("Možete li spašiti podatke?", "Da, spašavanje podataka s oštećenog diska jedna je od naših standardnih usluga."),
            ("Koliko košta dijagnostika?", "Procjenu dajemo nakon pregleda, prije početka popravka."),
        ],
    },
}


def nfc(name):
    return unicodedata.normalize("NFC", name)


def build_faq_html(faq_items):
    parts = ['<section class="service-faq">', "<h2>Često postavljana pitanja</h2>"]
    for question, answer in faq_items:
        parts.append(f"<h3>{question}</h3>")
        parts.append(f"<p>{answer}</p>")
    parts.append("</section>")
    return "\n".join(parts)


def build_body(config):
    return (
        f'<article class="node node-page service-page clearfix">\n'
        f'  <div class="content clearfix">\n'
        f'    <div class="field field-name-field-top-icon field-type-image field-label-hidden">'
        f'<div class="field-items"><div class="field-item even">'
        f'<img src="{config["og_image"]}" width="{config["og_width"]}" height="{config["og_height"]}" '
        f'alt="{config["service_name"]} u Rijeci"></div></div></div>\n'
        f'    <div class="field field-name-body field-type-text-with-summary field-label-hidden">'
        f'<div class="field-items"><div class="field-item even">\n'
        f'      <div class="service-intro">\n'
        f'        {config["intro"]}\n'
        f'        {config["models"]}\n'
        f"      </div>\n"
        f'      <div class="service-details">\n'
        f"        <h2>Najčešći kvarovi koje popravljamo</h2>\n"
        f"        {COMMON_REPAIRS}\n"
        f"        <h2>Kako izgleda postupak</h2>\n"
        f"        {COMMON_PROCESS}\n"
        f"        {build_faq_html(config['faq'])}\n"
        f"      </div>\n"
        f"    </div></div></div>\n"
        f"  </div>\n"
        f"</article>"
    )


def build_json_ld(config, basename):
    page_url = f"{SITE_URL}/{basename}"
    faq_entities = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in config["faq"]
    ]
    graph = [
        {
            "@type": "Service",
            "name": config["service_name"],
            "description": config["hero_message"],
            "url": page_url,
            "image": f"{SITE_URL}/{config['og_image']}",
            "provider": {
                "@type": "ComputerRepair",
                "name": "ARABBA d.o.o.",
                "url": f"{SITE_URL}/index.html",
                "telephone": ["+38551642291", "+38598257032"],
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Crnčićeva 4",
                    "addressLocality": "Rijeka",
                    "postalCode": "51000",
                    "addressCountry": "HR",
                },
            },
            "areaServed": {"@type": "City", "name": "Rijeka"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Naslovnica",
                    "item": f"{SITE_URL}/index.html",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Servis laptopa",
                    "item": f"{SITE_URL}/servis-i-popravak-laptopa-rijeka.html",
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": config["breadcrumb"],
                    "item": page_url,
                },
            ],
        },
        {"@type": "FAQPage", "mainEntity": faq_entities},
    ]
    payload = {"@context": "https://schema.org", "@graph": graph}
    return (
        '  <script type="application/ld+json">\n'
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n  </script>"
    )


def update_og_image(content, config):
    image_url = f"{SITE_URL}/{config['og_image']}"
    content = re.sub(
        r'<meta property="og:image" content="[^"]*">',
        f'<meta property="og:image" content="{image_url}">',
        content,
    )
    content = re.sub(
        r'<meta property="og:image:secure_url" content="[^"]*">',
        f'<meta property="og:image:secure_url" content="{image_url}">',
        content,
    )
    content = re.sub(
        r'<meta property="og:image:alt" content="[^"]*">',
        f'<meta property="og:image:alt" content="{config["service_name"]} u Rijeci, ARABBA d.o.o.">',
        content,
    )
    content = re.sub(
        r'<meta property="og:image:width" content="[^"]*">',
        f'<meta property="og:image:width" content="{config["og_width"]}">',
        content,
    )
    content = re.sub(
        r'<meta property="og:image:height" content="[^"]*">',
        f'<meta property="og:image:height" content="{config["og_height"]}">',
        content,
    )
    content = re.sub(
        r'<meta name="twitter:image" content="[^"]*">',
        f'<meta name="twitter:image" content="{image_url}">',
        content,
    )
    content = re.sub(
        r'<meta name="twitter:image:alt" content="[^"]*">',
        f'<meta name="twitter:image:alt" content="{config["service_name"]} u Rijeci, ARABBA d.o.o.">',
        content,
    )
    return content


def add_json_ld(content, config, basename):
    block = build_json_ld(config, basename)
    if "application/ld+json" in content:
        return re.sub(
            r"  <script type=\"application/ld\+json\">.*?</script>",
            block,
            content,
            count=1,
            flags=re.DOTALL,
        )
    return content.replace(
        '  <link rel="stylesheet" href="css/site.css">',
        block + '\n  <link rel="stylesheet" href="css/site.css">',
    )


def update_hero_message(content, message):
    return re.sub(
        r'(<span class="message">)[^<]*(</span>)',
        rf"\1{message}\2",
        content,
        count=1,
    )


def fix_h2_rijeka(content):
    return re.sub(
        r"(<h2 class=\"field-content\">[^<]*?)u Rijeki(</h2>)",
        r"\1u Rijeci\2",
        content,
        count=1,
    )


def replace_article_body(content, new_body):
    pattern = re.compile(
        r'<article class="node node-page[^"]*" id="node-page-\d+">.*?</article>',
        re.DOTALL,
    )
    return pattern.sub(new_body, content, count=1)


def add_messengers(content):
    if "messenger-links" in content:
        return content
    return content.replace(
        "</span></span></p>",
        f"</span></span> {MESSENGER_LINKS}</p>",
        1,
    )


def add_sticky_call(content):
    if "sticky-call-btn" in content:
        return content
    if '  <script src="js/testimonials.js" defer></script>' in content:
        return content.replace(
            '  <script src="js/testimonials.js" defer></script>',
            STICKY_CALL + '\n  <script src="js/testimonials.js" defer></script>',
        )
    return content.replace("</body>", STICKY_CALL + "\n</body>")


def update_contact_strip(content):
    phone_block = (
        '      <div class="contact-strip-item contact-strip-phone">\n'
        "        <strong>Telefon</strong>\n"
        '        <span class="contact-strip-phones">'
        '<a href="tel:+38551642291">051 642 291</a><br>'
        '<a href="tel:+38598257032">098 257 032</a></span>\n'
        '        <span class="contact-strip-messengers">\n'
        '          <a href="https://wa.me/38598257032" class="messenger-link messenger-whatsapp" '
        'aria-label="WhatsApp poruka">'
        '<img src="images/icon-whatsapp.svg" width="20" height="20" alt="">'
        "<span>WhatsApp</span></a>\n"
        '          <a href="viber://chat?number=38598257032" class="messenger-link messenger-viber" '
        'aria-label="Viber poruka">'
        '<img src="images/icon-viber.svg" width="20" height="20" alt="">'
        "<span>Viber</span></a>\n"
        "        </span>\n"
        "      </div>"
    )
    content = content.replace(
        '      <div class="contact-strip-item">\n'
        "        <strong>Telefon</strong><br>\n"
        '        <a href="tel:+38551642291">051 642 291</a> / '
        '<a href="tel:+38598257032">098 257 032</a>\n'
        "      </div>",
        phone_block,
    )
    content = content.replace(
        '<a href="gdje-smo.html">Crnčićeva 4, 51000 Rijeka</a>',
        f'<a href="{MAPS_URL}" target="_blank" rel="noopener noreferrer">Crnčićeva 4, 51000 Rijeka</a>',
    )
    if "Radno vrijeme" in content:
        return content
    return content.replace(
        '      <div class="contact-strip-item">\n'
        "        <strong>Područje rada</strong><br>\n"
        "        Rijeka i okolica\n"
        "      </div>",
        '      <div class="contact-strip-item">\n'
        "        <strong>Radno vrijeme</strong><br>\n"
        f"        {WORKING_HOURS}\n"
        "      </div>\n"
        '      <div class="contact-strip-item">\n'
        "        <strong>Područje rada</strong><br>\n"
        "        Rijeka i okolica\n"
        "      </div>",
    )


def fix_header_typos(content):
    content = content.replace("Fizički poparavak", "Fizički popravak")
    content = content.replace("čiščenje od virusa", "čišćenje od virusa")
    return content


def process_brand_page(path, config):
    basename = nfc(os.path.basename(path))
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = fix_header_typos(content)
    content = fix_h2_rijeka(content)
    content = update_hero_message(content, config["hero_message"])
    content = update_og_image(content, config)
    content = add_json_ld(content, config, basename)
    content = replace_article_body(content, build_body(config))
    content = add_messengers(content)
    content = add_sticky_call(content)
    content = update_contact_strip(content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK brand page: {basename}")


def process_other_page(path):
    basename = nfc(os.path.basename(path))
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = fix_header_typos(content)
    content = add_messengers(content)
    content = add_sticky_call(content)
    content = update_contact_strip(content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK shared updates: {basename}")


def update_index_json_ld(content):
    opening_hours = [
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "08:00",
            "closes": "16:00",
        }
    ]
    if '"openingHoursSpecification"' in content:
        return content
    content = content.replace(
        '"priceRange": "$$"\n  }',
        '"priceRange": "$$",\n'
        f'    "openingHoursSpecification": {json.dumps(opening_hours, ensure_ascii=False)}\n'
        "  }",
    )
    content = content.replace(
        '<a href="gdje-smo.html">Crnčićeva 4, 51000 Rijeka</a>',
        f'<a href="{MAPS_URL}" target="_blank" rel="noopener noreferrer">Crnčićeva 4, 51000 Rijeka</a>',
    )
    return content


def main():
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        basename = nfc(os.path.basename(path))
        if basename in BRAND_PAGES:
            process_brand_page(path, BRAND_PAGES[basename])
        else:
            process_other_page(path)

    index_path = os.path.join(ROOT, "index.html")
    with open(index_path, encoding="utf-8") as f:
        index_content = f.read()
    index_content = update_index_json_ld(index_content)
    if "messenger-links" not in index_content:
        index_content = index_content.replace(
            "</span></span></p>",
            f"</span></span> {MESSENGER_LINKS}</p>",
            1,
        )
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print("OK index.html JSON-LD + messengers")


if __name__ == "__main__":
    main()

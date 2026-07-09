#!/usr/bin/env python3
"""Expand non-brand service pages, fix heroes, typos, skip links, sitemap."""
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://arabba.hr"
SITEMAP_DATE = "2026-07-10"

SKIP_LINK = re.compile(
    r'\s*<div id="skip-link">\s*'
    r'<a href="#main-content" class="element-invisible element-focusable">Skip to main content</a>\s*'
    r"</div>",
    re.MULTILINE,
)

COMMON_PROCESS = """<ol>
<li><strong>Kontakt</strong> — nazovite, pošaljite poruku ili donesite uređaj u servis.</li>
<li><strong>Dijagnostika</strong> — utvrdimo problem i javimo procjenu cijene.</li>
<li><strong>Popravak ili optimizacija</strong> — nakon vašeg odobrenja obavljamo dogovoreni rad.</li>
<li><strong>Testiranje i predaja</strong> — provjerimo da sve radi prije vraćanja uređaja.</li>
</ol>"""


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
        f'        {config.get("details", "")}\n'
        f"      </div>\n"
        f'      <div class="service-details">\n'
        f"        <h2>{config['problems_title']}</h2>\n"
        f"        {config['problems']}\n"
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
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
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
                {"@type": "ListItem", "position": 1, "name": "Naslovnica", "item": f"{SITE_URL}/index.html"},
                {"@type": "ListItem", "position": 2, "name": config["breadcrumb"], "item": page_url},
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


SERVICE_PAGES = {
    "servis-računala.html": {
        "og_image": "images/shutterstock_111626318_0_0.jpg",
        "og_width": "480",
        "og_height": "321",
        "service_name": "Servis računala",
        "breadcrumb": "Servis računala",
        "hero_message": "Računalo ne pali se, radi sporo ili trebate zamjenu komponente? Nudimo dijagnostiku i popravak PC i Mac računala u Rijeci.",
        "problems_title": "Najčešći problemi koje rješavamo",
        "intro": (
            "<p>Usluge servisiranja, održavanja i popravka računala naša su specijalnost. "
            "Nakon servisa vaše računalo radi brže i stabilnije — pokrivamo PC i Mac modele "
            "na području Rijeke i okolice.</p>"
        ),
        "details": (
            "<p>Nudimo pronalaženje kvara, testiranje software-skim alatima, fizički popravak, "
            "zamjenu komponenti te instalaciju hardvera i softvera.</p>"
        ),
        "problems": """<ul>
<li>Računalo se ne pali ili se iznenada gasi</li>
<li>Spor rad, zaglavljivanje i plavi ekran</li>
<li>Zamjena SSD-a, RAM-a, napajanja i grafičke kartice</li>
<li>Instalacija Windowsa, Linuxa ili macOS-a</li>
<li>Uklanjanje virusa i malwarea</li>
<li>Spašavanje podataka s oštećenog diska</li>
</ul>""",
        "faq": [
            ("Servisirate li Mac računala?", "Da — radimo na iMac, Mac mini i Mac Pro modelima uz dijagnostiku i nadogradnju."),
            ("Koliko traje popravak računala?", "Dijagnostika je brza, a jednostavni popravci često isti dan. Složeniji zahvati traju nekoliko radnih dana."),
            ("Možete li nadograditi staro računalo?", "Da — SSD i RAM nadogradnja najčešći su načini da starije računalo opet brzo radi."),
            ("Hoćete li sačuvati moje podatke?", "Da — podatke čuvamo koliko god je tehnički moguće pri svakom zahvatu."),
        ],
    },
    "ugovorno-održavanje-računala.html": {
        "og_image": "images/shutterstock_113353828.jpg",
        "og_width": "480",
        "og_height": "360",
        "service_name": "Ugovorno održavanje računala",
        "breadcrumb": "Ugovorno održavanje",
        "hero_message": "Vaše poslovanje ne smije stati zbog kvara. Ugovorite održavanje računala i servera s redovitim pregledima i nadzorom na daljinu u Rijeci.",
        "problems_title": "Što uključuje ugovorno održavanje",
        "intro": (
            "<p>Kad se nenadano pokvari računalo od kojeg ovisi poslovanje, gubi se vrijeme i novac. "
            "Ugovorom s Arabba servisom brinemo se o vašem radnom alatu — redoviti pregledi i stručni "
            "nadzor smanjuju iznenadne kvarove i gubitak podataka.</p>"
        ),
        "details": (
            "<p>Vršimo instalaciju sustava i servera te održavanje na licu mjesta i na daljinu. "
            "Po potrebi se povezujemo udaljeno i brzo rješavamo hitne situacije. "
            "Uslugu pružamo na području Rijeke i okolice.</p>"
        ),
        "problems": """<ul>
<li>Redoviti pregledi opreme i ažuriranja sustava</li>
<li>Nadzor rada računala i servera na daljinu</li>
<li>Brza intervencija kad nešto prestane raditi</li>
<li>Preventivno održavanje prije nego nastane kvar</li>
<li>Telefonske konzultacije i podrška korisnicima</li>
<li>Instalacija i održavanje poslovnih mreža</li>
</ul>""",
        "faq": [
            ("Za koga je ugovorno održavanje?", "Za tvrtke, obrte i urede koji ne mogu priuštiti zastoj rada zbog kvara na računalu ili serveru."),
            ("Možete li raditi na daljinu?", "Da — osim dolaska na licu mjesta, nudimo udaljeni nadzor i brzu intervenciju putem interneta."),
            ("Koliko često dolazite na pregled?", "Učestalost dogovaramo prema veličini sustava — mjesečno, kvartalno ili po potrebi."),
            ("Radite li i na serverima?", "Da — instaliramo i održavamo poslovne sustave i servere."),
        ],
    },
    "čiščenje-optimiziranje-i-ubrzavanje-računala.html": {
        "og_image": "images/shutterstock_111626318_0_0.jpg",
        "og_width": "480",
        "og_height": "321",
        "service_name": "Čišćenje i optimizacija računala",
        "breadcrumb": "Ubrzavanje računala",
        "hero_message": "Računalo radi sporo, dugo se pali ili se pregrijava? Temeljito čistimo, optimiziramo i ubrzavamo PC i Mac računala u Rijeci.",
        "problems_title": "Kada je optimizacija potrebna",
        "intro": (
            "<p>Sporo računalo ne mora biti razlog za kupnju novog. Često je dovoljno temeljito "
            "čišćenje, uklanjanje nepotrebnih programa i nadogradnja SSD-a ili RAM-a da "
            "sustav opet radi brzo i stabilno.</p>"
        ),
        "details": (
            "<p>Nakon dijagnostike predlažemo način optimizacije, preporučujemo nadogradnju "
            "(SSD, RAM) i po potrebi reinstalaciju operativnog sustava. "
            "Radimo na području Rijeke i okolice.</p>"
        ),
        "problems": """<ul>
<li>Sporo pokretanje i dugo učitavanje programa</li>
<li>Pregrijavanje zbog prašine u kućištu i ventilatorima</li>
<li>Puno nepotrebnih programa i datoteka</li>
<li>Stari mehanički disk umjesto SSD-a</li>
<li>Premalo RAM-a za svakodnevni rad</li>
<li>Reinstalacija Windowsa ili macOS-a bez gubitka podataka</li>
</ul>""",
        "faq": [
            ("Koliko brže će raditi nakon optimizacije?", "Često osjetno — posebno nakon SSD nadogradnje i čišćenja sustava. Točan učinak ovisi o stanju računala."),
            ("Hoćete li sačuvati moje programe i podatke?", "Da — prije reinstalacije dogovorimo backup važnih podataka."),
            ("Koliko traje čišćenje i optimizacija?", "Većina poslova traje nekoliko sati do jednog radnog dana, ovisno o opsegu."),
            ("Radite li i na Mac računalima?", "Da — čistimo i optimiziramo i Mac modele."),
        ],
    },
    "zaštita-računala-antivirusna-antidialer-antispyware-antispam.html": {
        "og_image": "images/shutterstock_111626318_3.jpg",
        "og_width": "480",
        "og_height": "321",
        "service_name": "Zaštita računala",
        "breadcrumb": "Zaštita računala",
        "hero_message": "Sumnjate na virus, spyware ili trebate pouzdan antivirus i backup? Štitimo vaše računalo i podatke u Rijeci.",
        "problems_title": "Usluge zaštite koje nudimo",
        "intro": (
            "<p>Virus, spyware ili zaboravljeni backup mogu koštati više od samog popravka. "
            "Instaliramo i konfiguriramo zaštitu prilagođenu vašem načinu rada — od antivirusa "
            "do enkripcije i sigurnosnih kopija.</p>"
        ),
        "details": (
            "<p>Instaliramo antivirus, antispyware, firewall te po potrebi antidialer. "
            "Nudimo i programe za backup, enkripciju i upravljanje lozinkama uz kratke upute "
            "za korištenje.</p>"
        ),
        "problems": """<ul>
<li>Instalacija i podešavanje antivirusa</li>
<li>Uklanjanje spywarea, adwarea i dialera</li>
<li>Postavljanje firewalla i sigurnosnih pravila</li>
<li>Backup rješenja za važne podatke</li>
<li>Enkripcija osjetljivih datoteka</li>
<li>Password manager i savjeti za sigurno korištenje</li>
</ul>""",
        "faq": [
            ("Računalo mi je sporo — je li to virus?", "Ne uvijek, ali provjeravamo i virus i ostale uzroke. Dijagnostika otkriva stvarni problem."),
            ("Koji antivirus preporučujete?", "Preporuka ovisi o vašem sustavu i navikama — dogovorimo rješenje koje ne usporava računalo."),
            ("Možete li ukloniti postojeći virus?", "Da — čistimo zaražena računala i po potrebi reinstaliramo sustav uz spašavanje podataka."),
            ("Pomažete li s backupom?", "Da — postavljamo programe za automatsku sigurnosnu kopiju važnih datoteka."),
        ],
    },
}

HERO_MESSAGES = {
    "gdje-smo.html": "Nalazimo se u Crnčićevoj 4 u Rijeci, iznad Kauflanda na Krnjevu. Lako nas pronađete — javite se prije dolaska.",
}


def nfc(name):
    return unicodedata.normalize("NFC", name)


def replace_article_body(content, new_body):
    pattern = re.compile(
        r'<article class="node node-page[^"]*" id="node-page-\d+">.*?</article>',
        re.DOTALL,
    )
    return pattern.sub(new_body, content, count=1)


def update_hero_message(content, message):
    for pattern in (
        r'(<span class="message">)[^<]*(</span>)',
        r'(<p class="message">)[^<]*(</p>)',
    ):
        new_content, count = re.subn(pattern, rf"\1{message}\2", content, count=1)
        if count:
            return new_content
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


def update_og_image(content, config):
    image_url = f"{SITE_URL}/{config['og_image']}"
    for prop, val in [
        ("og:image", image_url),
        ("og:image:secure_url", image_url),
        ("twitter:image", image_url),
        ("og:image:width", config["og_width"]),
        ("og:image:height", config["og_height"]),
    ]:
        if prop.startswith("og:"):
            content = re.sub(
                rf'<meta property="{re.escape(prop)}" content="[^"]*">',
                f'<meta property="{prop}" content="{val}">',
                content,
            )
        else:
            content = re.sub(
                rf'<meta name="{re.escape(prop)}" content="[^"]*">',
                f'<meta name="{prop}" content="{val}">',
                content,
            )
    alt = f'{config["service_name"]} u Rijeci — ARABBA d.o.o.'
    content = re.sub(
        r'<meta property="og:image:alt" content="[^"]*">',
        f'<meta property="og:image:alt" content="{alt}">',
        content,
    )
    content = re.sub(
        r'<meta name="twitter:image:alt" content="[^"]*">',
        f'<meta name="twitter:image:alt" content="{alt}">',
        content,
    )
    return content


def fix_rijeki_typos(content):
    content = content.replace("u Rijeki", "u Rijeci")
    content = content.replace("u Rijeci i", "u Rijeci i")  # no-op safety
    return content


def remove_skip_link(content):
    return SKIP_LINK.sub("", content)


def update_sitemap():
    path = os.path.join(ROOT, "sitemap.xml")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>",
        f"<lastmod>{SITEMAP_DATE}</lastmod>",
        content,
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def process_service_page(path, config):
    basename = nfc(os.path.basename(path))
    with open(path, encoding="utf-8") as f:
        content = f.read()
    content = fix_rijeki_typos(content)
    content = remove_skip_link(content)
    content = update_hero_message(content, config["hero_message"])
    content = update_og_image(content, config)
    content = add_json_ld(content, config, basename)
    content = replace_article_body(content, build_body(config))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK service page: {basename}")


def process_all_html():
    lookup = {nfc(k): v for k, v in SERVICE_PAGES.items()}
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        basename = nfc(os.path.basename(path))
        if basename in lookup:
            process_service_page(path, lookup[basename])
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        changed = False
        new_content = fix_rijeki_typos(content)
        if new_content != content:
            content = new_content
            changed = True
        new_content = remove_skip_link(content)
        if new_content != content:
            content = new_content
            changed = True
        if basename in HERO_MESSAGES:
            new_content = update_hero_message(content, HERO_MESSAGES[basename])
            if new_content != content:
                content = new_content
                changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"OK fixes: {basename}")


def trim_css():
    path = os.path.join(ROOT, "css", "site.css")
    with open(path, encoding="utf-8") as f:
        css = f.read()

    # Drop legacy Drupal module bundles (lines before Omega reset).
    css = re.sub(
        r"^/\* --- css/css_xE-rWrJf.*?(?=/\* --- css/css_dLja2qgEMLX2S25NvkCUPFdc5rdI4FWcUYDzgHt6qDs.css --- \*/)",
        "",
        css,
        flags=re.DOTALL,
    )

    css = css.replace(
        "#skip-link{left:50%;margin-left:-5.25em;margin-top:0;position:absolute;width:auto;z-index:50;}"
        "#skip-link a,#skip-link a:link,#skip-link a:visited{background:#444;background:rgba(0,0,0,0.6);"
        "color:#fff;display:block;padding:1px 10px 2px 10px;text-decoration:none;-khtml-border-radius:0 0 10px 10px;"
        "-moz-border-radius:0 0 10px 10px;-o-border-radius:0 0 10px 10px;-webkit-border-top-left-radius:0;"
        "-webkit-border-top-right-radius:0;-webkit-border-bottom-left-radius:10px;-webkit-border-bottom-right-radius:10px;"
        "border-radius:0 0 10px 10px;}#skip-link a:hover,#skip-link a:active,#skip-link a:focus{outline:0;}",
        "",
    )

    dead_blocks = [
        r"\.view-id-portfolio\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-title\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-field-subtitle\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-body\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-taxonomy-vocabulary-1\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-taxonomy-vocabulary-1  a\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-field-za\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-field-za p\{[^}]*\}",
        r"\.view-id-portfolio \.views-label-field-za\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-field-za \.field-content a\{[^}]*\}",
        r"\.view-id-portfolio \.views-field-field-za \.field-content\{[^}]*\}",
        r"\.view-id-portfolio  \.item-list\{[^}]*\}",
        r"\.view-id-portfolio ul\.pager\{[^}]*\}",
        r"\.view-id-portfolio ul\.pager a\{[^}]*\}",
        r"\.view-id-portfolio ul\.pager li\{[^}]*\}",
        r"\.views-field-field-portfolio-image\{[^}]*\}",
        r"#cboxNode \.node label\{[^}]*\}",
        r"#cboxNode \.node\.form-submit\{[^}]*\}",
        r"#cboxNode \.node \.form-email\{[^}]*\}",
        r"#cboxNode\{[^}]*\}",
        r"#cboxNode \.node-title a\{[^}]*\}",
        r"#cboxNode input\{[^}]*\}",
        r"#cboxNode textarea\{[^}]*\}",
        r"\.view-bottom-icons\{[^}]*\}",
        r"\.view-bottom-icons \.views-row\{[^}]*\}",
        r"#webform-client-form-7029\{[^}]*\}",
        r"textarea#edit-submitted-poruka\{[^}]*\}",
        r"#block-webform-client-block-7029 input\{[^}]*\}",
        r"#block-webform-client-block-7029 input#edit-submitted-email\{[^}]*\}",
        r"#block-webform-client-block-7029 textarea\{[^}]*\}",
        r"#block-webform-client-block-7029 \.compact-form-label\{[^}]*\}",
        r"#block-webform-client-block-7029 input\.form-submit,#cboxNode #node-webform-7029 input\.form-submit\{[^}]*\}",
        r"#block-webform-client-block-7029 #webform-component-poruka,#block-webform-client-block-7029 #webform-component-email\{[^}]*\}",
        r"#block-system-main-menu\{\}",
        r"\.page-node-253 #block-views-testimonial-block\{[^}]*\}",
        r"\.page-node-252  #block-views-testimonial-block\{[^}]*\}",
    ]
    for pattern in dead_blocks:
        css = re.sub(pattern, "", css)

    # Remove first duplicate Omega grid block; keep the second (944px container).
    css = re.sub(
        r"/\* --- css/css_1CaoCuqGe4B4ITWBXcfNXrKntc5Mh6q6YRluVwAyNgg.css --- \*/\n"
        r"@media all and \(min-width:980px\).*?\.container-12 \.pull-11\{left:-880px;\}\}\n",
        "",
        css,
        count=1,
        flags=re.DOTALL,
    )
    css = re.sub(
        r"@media all and \(min-width:980px\).*?\(orientation:landscape\)\{\}\n?",
        "",
        css,
        flags=re.DOTALL,
    )

    css = re.sub(r"\n{3,}", "\n\n", css).strip() + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"OK trimmed css/site.css ({len(css)} bytes)")


def fix_apply_seo():
    path = os.path.join(ROOT, "scripts", "apply-seo.py")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    content = content.replace("u Rijeki", "u Rijeci")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("OK scripts/apply-seo.py typos")


def main():
    process_all_html()
    update_sitemap()
    trim_css()
    fix_apply_seo()
    print(f"OK sitemap lastmod -> {SITEMAP_DATE}")


if __name__ == "__main__":
    main()

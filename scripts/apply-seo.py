#!/usr/bin/env python3
"""Apply SEO and social-sharing meta tags across all HTML pages.

Edit PAGE_SEO (and SITE_* / OG_* constants below), then run:

    python3 scripts/apply-seo.py
"""
import glob
import os
import re
import unicodedata
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Site-wide social / SEO settings (single place to update)
SITE_URL = "https://arabba.hr"
SITE_NAME = "ARABBA d.o.o."
OG_LOCALE = "hr_HR"
OG_IMAGE = "images/og-share.png"
OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630
OG_IMAGE_ALT = "ARABBA d.o.o., servis računala i laptopa, Rijeka"
TWITTER_CARD = "summary_large_image"
LOGO_ALT = "ARABBA d.o.o., servis računala Rijeka"


def absolute_page_url(basename):
    return f"{SITE_URL}/{quote(basename, safe='')}"


def absolute_asset_url(path):
    return f"{SITE_URL}/{path.lstrip('/')}"


def build_social_head(seo, basename, is_index):
    """Render canonical, Open Graph, title, and Twitter Card tags for one page."""
    page_url = absolute_page_url(basename)
    og_image_path = seo.get("og_image", OG_IMAGE)
    og_image_url = absolute_asset_url(og_image_path)
    og_image_alt = seo.get("og_image_alt", OG_IMAGE_ALT)
    og_type = "website" if is_index else "article"
    og_title = seo["og_title"]
    desc = seo["desc"]
    title = seo["title"]

    return f"""  <link rel="canonical" href="{page_url}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:locale" content="{OG_LOCALE}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:url" content="{page_url}">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{og_image_url}">
  <meta property="og:image:secure_url" content="{og_image_url}">
  <meta property="og:image:alt" content="{og_image_alt}">
  <meta property="og:image:width" content="{OG_IMAGE_WIDTH}">
  <meta property="og:image:height" content="{OG_IMAGE_HEIGHT}">
  <title>{title}</title>
  <meta name="twitter:card" content="{TWITTER_CARD}">
  <meta name="twitter:title" content="{og_title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{og_image_url}">
  <meta name="twitter:image:alt" content="{og_image_alt}">"""


SOCIAL_HEAD_RE = re.compile(
    r"  <link rel=\"canonical\" href=\"[^\"]*\">\n"
    r"(?:  <meta (?:property=\"og:[^\"]*\"|name=\"twitter:[^\"]*\") content=\"[^\"]*\">\n)*"
    r"  <title>[^<]*</title>\n"
    r"(?:  <meta (?:property=\"og:[^\"]*\"|name=\"twitter:[^\"]*\") content=\"[^\"]*\">\n)*"
)

LOCAL_BUSINESS_JSON = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "ComputerRepair",
    "name": "ARABBA d.o.o.",
    "description": "Servis računala i laptopa u Rijeci: PC i Mac. Dijagnostika, popravak, čišćenje virusa i spašavanje podataka.",
    "url": "{absolute_page_url("index.html")}",
    "logo": "{absolute_asset_url("images/logo.png")}",
    "image": "{absolute_asset_url("images/logo.png")}",
    "telephone": ["+38551642291", "+38598257032"],
    "email": "nenad@arabba.hr",
    "address": {{
      "@type": "PostalAddress",
      "streetAddress": "Crnčićeva 4",
      "addressLocality": "Rijeka",
      "postalCode": "51000",
      "addressCountry": "HR"
    }},
    "geo": {{
      "@type": "GeoCoordinates",
      "latitude": 45.342448,
      "longitude": 14.399686
    }},
    "areaServed": {{
      "@type": "City",
      "name": "Rijeka"
    }},
    "foundingDate": "1995",
    "priceRange": "$$"
  }}
  </script>"""

BRAND_LINKS = """<p><strong>Servis laptopa po markama:</strong> <a href="servis-hp-laptopa-rijeka.html">HP</a>, <a href="servis-lenovo-laptopa-rijeka.html">Lenovo</a>, <a href="servis-asus-laptopa-rijeka.html">ASUS</a>, <a href="servis-acer-laptopa-rijeka.html">Acer</a>, <a href="servis-toshiba-laptopa-rijeka.html">Toshiba</a>, <a href="msi-servis-laptopa-rijeka.html">MSI</a>, <a href="apple-servis-rijeka.html">Apple MacBook</a>.</p>"""

FOOTER_BRAND_LINKS_RE = re.compile(
    r'<div class="block block-block block-brand-links block-block-brand-links even block-without-title" id="block-brand-links">'
    r"\s*<div class=\"block-inner clearfix\">\s*"
    r'<div class="content clearfix">\s*'
    r'<p class="brand-links"><strong>Servis laptopa po markama:</strong>.*?</p>\s*'
    r"</div>\s*</div>\s*</div>",
    re.DOTALL,
)

# Match files by basename prefix / exact name
PAGE_SEO = {
    "index.html": {
        "title": "Servis Računala i Laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis računala i laptopa u Rijeci: PC i Mac. Dijagnostika, popravak, čišćenje virusa i spašavanje podataka. ARABBA d.o.o. od 1995. Nazovite!",
        "og_title": "Servis Računala i Laptopa - Rijeka | ARABBA d.o.o.",
        "h2": None,
    },
    "servis-računala.html": {
        "title": "Servis računala - Rijeka | ARABBA d.o.o.",
        "desc": "Servis računala u Rijeci: dijagnostika, zamjena komponenti i instalacija softvera. PC i Mac. Brza procjena i popravak. Tel: 051 642 291.",
        "og_title": "Servis računala - Rijeka",
        "h2": "Servis računala u Rijeci, brzo i pouzdano",
        "hero_alt": "Servis računala u Rijeci",
    },
    "servis-i-popravak-laptopa-rijeka.html": {
        "title": "Servis i popravak Laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis i popravak laptopa u Rijeci: zamjena dijelova, čišćenje, reinstalacija OS-a i spašavanje podataka. PC i Mac. Zatražite procjenu!",
        "og_title": "Servis i popravak Laptopa - Rijeka",
        "h2": "Servis laptopa u Rijeci, svi modeli",
        "hero_alt": "Servis laptopa u Rijeci",
        "add_brand_links": True,
    },
    "ugovorno-održavanje-računala.html": {
        "title": "Ugovorno održavanje računala Rijeka | ARABBA d.o.o.",
        "desc": "Ugovorno održavanje računala i servera u Rijeci: redoviti pregledi, nadzor na daljinu i brza intervencija. Smanjite rizik od kvarova.",
        "og_title": "Ugovorno održavanje računala Rijeka",
        "h2": "Ugovorno održavanje računala u Rijeci",
        "hero_alt": "Ugovorno održavanje računala u Rijeci",
    },
    "čišćenje-optimiziranje-i-ubrzavanje-računala.html": {
        "title": "Čiščenje, optimiziranje i ubrzavanje računala | ARABBA d.o.o.",
        "desc": "Čišćenje i optimiziranje računala u Rijeci: ubrzanje sporog PC-a, otprašivanje, nadogradnja i reinstalacija Windowsa. Zatražite procjenu!",
        "og_title": "Čiščenje, optimiziranje i ubrzavanje računala",
        "h2": "Ubrzavanje i optimizacija računala u Rijeci",
        "hero_alt": "Optimiziranje i ubrzavanje računala u Rijeci",
    },
    "zaštita-računala-antivirusna-antidialer-antispyware-antispam.html": {
        "title": "Zaštita računala Rijeka | ARABBA d.o.o.",
        "desc": "Zaštita računala u Rijeci: instalacija antivirusa, antispywarea, firewalla i backup rješenja. Sigurnost vaših podataka. Nazovite nas!",
        "og_title": "Zaštita računala Rijeka",
        "h2": "Zaštita računala u Rijeci, antivirus i firewall",
        "hero_alt": "Zaštita računala od virusa u Rijeci",
    },
    "servis-hp-laptopa-rijeka.html": {
        "title": "Servis HP laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis HP laptopa u Rijeci: Pavilion, ProBook, EliteBook. Dijagnostika, čišćenje pregrijavanja, zamjena dijelova. Tel: 051 642 291.",
        "og_title": "Servis HP laptopa - Rijeka",
        "h2": "Servis HP laptopa u Rijeci",
        "hero_alt": "Servis HP laptopa u Rijeci",
    },
    "servis-asus-laptopa-rijeka.html": {
        "title": "Servis ASUS laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis ASUS laptopa u Rijeci: serije N, S, K, G, U i X. Dijagnostika, čišćenje, nadogradnja i popravak. Zatražite besplatnu procjenu!",
        "og_title": "Servis ASUS laptopa - Rijeka",
        "h2": "Servis ASUS laptopa u Rijeci",
        "hero_alt": "Servis ASUS laptopa u Rijeci",
    },
    "servis-acer-laptopa-rijeka.html": {
        "title": "Servis Acer Laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis Acer laptopa u Rijeci: Aspire, TravelMate, Extensa i Iconia. Dijagnostika, zamjena dijelova i spašavanje podataka. Nazovite nas!",
        "og_title": "Servis Acer Laptopa - Rijeka",
        "h2": "Servis Acer laptopa u Rijeci",
        "hero_alt": "Servis Acer laptopa u Rijeci",
    },
    "servis-lenovo-laptopa-rijeka.html": {
        "title": "Servis Lenovo laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis Lenovo laptopa u Rijeci: ThinkPad i ostali modeli. Dijagnostika, čišćenje, zamjena dijelova i spašavanje podataka. Tel: 051 642 291.",
        "og_title": "Servis Lenovo laptopa - Rijeka",
        "h2": "Servis Lenovo laptopa u Rijeci",
        "hero_alt": "Servis Lenovo laptopa u Rijeci",
    },
    "servis-toshiba-laptopa-rijeka.html": {
        "title": "Servis Toshiba laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis Toshiba laptopa u Rijeci: Satellite, Portégé, Tecra i Qosmio. Brza dijagnostika, popravak i zamjena dijelova. Zatražite procjenu!",
        "og_title": "Servis Toshiba laptopa - Rijeka",
        "h2": "Servis Toshiba laptopa u Rijeci",
        "hero_alt": "Servis Toshiba laptopa u Rijeci",
    },
    "msi-servis-laptopa-rijeka.html": {
        "title": "MSI servis laptopa - Rijeka | ARABBA d.o.o.",
        "desc": "Servis MSI laptopa u Rijeci: dijagnostika, čišćenje, zamjena dijelova i spašavanje podataka. Gaming i poslovni modeli. Nazovite 051 642 291.",
        "og_title": "MSI servis laptopa - Rijeka",
        "h2": "Servis MSI laptopa u Rijeci",
        "hero_alt": "Servis MSI laptopa u Rijeci",
    },
    "apple-servis-rijeka.html": {
        "title": "Apple servis Rijeka | ARABBA d.o.o.",
        "desc": "Apple servis u Rijeci: MacBook Pro, MacBook Air, iMac i Mac mini. Dijagnostika, zamjena dijelova, čišćenje i spašavanje podataka. Nazovite!",
        "og_title": "Apple servis Rijeka",
        "h2": "Apple servis u Rijeci, MacBook i iMac",
        "hero_alt": "Apple MacBook servis u Rijeci",
    },
    "o-nama.html": {
        "title": "O nama | ARABBA d.o.o.",
        "desc": "ARABBA d.o.o., servis računala i laptopa u Rijeci od 1995. Precizna dijagnostika, kvalitetni popravci i izvrsna usluga korisnicima.",
        "og_title": "O nama",
        "h2": None,
    },
    "gdje-smo.html": {
        "title": "Gdje smo | ARABBA d.o.o.",
        "desc": "Gdje nas naći: Crnčićeva 4, Rijeka (iznad Kauflanda na Krnjevu). ARABBA d.o.o. servis računala. Nazovite 051 642 291.",
        "og_title": "Gdje smo",
        "h2": "Pronađite nas u Rijeci, Crnčićeva 4",
    },
    "podaci-o-firmi.html": {
        "title": "Podaci o firmi | ARABBA d.o.o.",
        "desc": "Podaci o tvrtki ARABBA d.o.o., sjedište u Rijeci, Trgovački sud u Rijeci. Kontakt, OIB i poslovne informacije.",
        "og_title": "Podaci o firmi",
        "h2": None,
    },
}

INDEX_IMAGE_ALTS = {
    "images/rijeka_okolica.png": "Rijeka i okolica, područje servisa ARABBA",
    "images/HP-Pavilion-Elite-Desktop-Computer_0.jpg": "Servis računala u Rijeci",
    "images/34-laptop1_0.png": "Servis laptopa u Rijeci",
    "images/windows-7-compatible-antivirus_0.jpg": "Zaštita računala od virusa u Rijeci",
    "images/os.png": "Instalacija operativnih sustava Windows, Linux i Mac OS",
    "images/ugovor.jpg": "Ugovorno održavanje računala u Rijeci",
    "images/comp-arrow.png": "Gdje smo, lokacija servisa ARABBA u Rijeci",
}


def replace_meta(content, name, value):
    pattern = rf'<meta name="{re.escape(name)}" content="[^"]*">'
    replacement = f'<meta name="{name}" content="{value}">'
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content, count=1)
    return content


def apply_social_head(content, seo, basename, is_index):
    """Replace canonical + Open Graph + Twitter block with the current template."""
    social_block = build_social_head(seo, basename, is_index)
    if SOCIAL_HEAD_RE.search(content):
        return SOCIAL_HEAD_RE.sub(social_block + "\n", content, count=1)

    # First run on a page that only has partial tags, insert after keywords meta.
    anchor = re.search(r'<meta name="keywords" content="[^"]*">', content)
    if anchor:
        insert_at = anchor.end()
        return content[:insert_at] + "\n" + social_block + content[insert_at:]

    return content


def add_json_ld(content):
    if "application/ld+json" in content:
        return re.sub(
            r'  <script type="application/ld\+json">.*?</script>',
            LOCAL_BUSINESS_JSON,
            content,
            count=1,
            flags=re.DOTALL,
        )
    return content.replace(
        '  <link rel="stylesheet" href="css/site.css">',
        LOCAL_BUSINESS_JSON + '\n  <link rel="stylesheet" href="css/site.css">',
    )


def fix_common_alts(content):
    content = content.replace(
        '<img src="images/logo.png" alt id="logo">',
        f'<img src="images/logo.png" alt="{LOGO_ALT}" id="logo">',
    )
    content = re.sub(
        r'(<a href="servis-ra%C4%8Dunala\.html"><img src="images/icon1\.png" width="27" height="23" )alt>',
        r'\1alt="Servis računala">',
        content,
    )
    content = re.sub(
        r'(<a href="servis-i-popravak-laptopa-rijeka\.html"><img src="images/icon2\.png" width="27" height="23" )alt>',
        r'\1alt="Servis laptopa">',
        content,
    )
    content = re.sub(
        r'(<a href="ugovorno-odr%C5%BEavanje-ra%C4%8Dunala\.html"><img src="images/icon3\.png" width="21" height="27" )alt>',
        r'\1alt="Održavanje računala">',
        content,
    )
    return content


def fix_hero_alt(content, alt_text):
    if not alt_text:
        return content

    pattern = (
        r'(<div class="field field-name-field-top-icon field-type-image field-label-hidden">'
        r'<div class="field-items"><div class="field-item even"><img src="images/[^"]+" '
        r'width="[^"]+" height="[^"]+" )alt(?:="[^"]*")?(>)'
    )
    return re.sub(pattern, rf'\1alt="{alt_text}"\2', content, count=1)


def fix_index_image_alts(content):
    for src, alt in INDEX_IMAGE_ALTS.items():
        content = re.sub(
            rf'(<img src="{re.escape(src)}"[^>]*?) alt(?:="[^"]*")?(>)',
            rf'\1 alt="{alt}"\2',
            content,
        )
    content = re.sub(
        r'<img alt src="images/comp-arrow\.png"([^>]*)>',
        rf'<img src="images/comp-arrow.png" alt="{INDEX_IMAGE_ALTS["images/comp-arrow.png"]}"\1>',
        content,
    )
    return content


def fix_h2(content, h2_text):
    if not h2_text:
        return content
    return re.sub(
        r'(<div class="views-field views-field-title">\s*)<h2 class="field-content">[^<]*</h2>',
        rf'\1<h2 class="field-content">{h2_text}</h2>',
        content,
        count=1,
    )


def fix_homepage_hero(content):
    """Keep the homepage hero as real HTML text matching the original design."""
    hero_block = """        <h1 class="node-title">Trebate pouzdan servis računala ili laptopa?</h1>
    
  
  <div class="content">
    <div class="field field-name-body field-type-text-with-summary field-label-hidden"><div class="field-items"><div class="field-item even"><p>Usluge popravka računala i laptopa su naša specijalnost. Vaše računalo će raditi brzo i stabilno.</p>
<p class="hero-mail-label"><strong>Pošaljite nam mail na</strong></p>
<p class="hero-mail"><!--email_off--><a href="mailto:nenad@arabba.hr">nenad@arabba.hr</a><!--/email_off--></p>
</div></div></div>  </div>"""

    pattern = re.compile(
        r"        <h1 class=\"node-title\">[^<]*</h1>\s*"
        r"(?:\n\s*)?"
        r"<div class=\"content\">\s*"
        r"<div class=\"field field-name-body field-type-text-with-summary field-label-hidden\">"
        r"<div class=\"field-items\"><div class=\"field-item even\">.*?"
        r"</div></div></div>  </div>",
        re.DOTALL,
    )
    if pattern.search(content):
        return pattern.sub(hero_block, content, count=1)
    return content


def add_brand_links_body(content):
    if BRAND_LINKS in content:
        return content
    pattern = r'(Servisiramo PC i Mac laptope\.</p>)'
    return re.sub(pattern, r'\1\n' + BRAND_LINKS, content, count=1)


def remove_footer_brand_links(content):
    return FOOTER_BRAND_LINKS_RE.sub("", content)


def nfc(name):
    return unicodedata.normalize("NFC", name)


PAGE_SEO_LOOKUP = {nfc(k): v for k, v in PAGE_SEO.items()}

# Fallback slugs for filenames with alternate Unicode spellings
PAGE_SEO_BY_SLUG = {
    "optimiziranje-i-ubrzavanje": PAGE_SEO["čišćenje-optimiziranje-i-ubrzavanje-računala.html"],
}


def lookup_seo(basename):
    seo = PAGE_SEO_LOOKUP.get(basename)
    if seo:
        return seo
    for slug, data in PAGE_SEO_BY_SLUG.items():
        if slug in basename:
            return data
    return None


def process_file(path):
    basename = nfc(os.path.basename(path))
    seo = lookup_seo(basename)
    if not seo:
        print(f"SKIP (no SEO config): {basename!r}")
        return

    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = replace_meta(content, "description", seo["desc"])
    content = apply_social_head(content, seo, basename, is_index=basename == "index.html")
    content = fix_common_alts(content)
    content = fix_hero_alt(content, seo.get("hero_alt"))
    content = fix_h2(content, seo.get("h2"))
    content = remove_footer_brand_links(content)

    if basename == "index.html":
        content = fix_homepage_hero(content)
        content = fix_index_image_alts(content)
        content = add_json_ld(content)

    if seo.get("add_brand_links"):
        content = add_brand_links_body(content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    desc_len = len(seo["desc"])
    print(f"OK {basename} (desc={desc_len}, title={len(seo['title'])})")


def main():
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        process_file(path)


if __name__ == "__main__":
    main()

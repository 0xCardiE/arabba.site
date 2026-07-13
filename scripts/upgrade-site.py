#!/usr/bin/env python3
"""Apply site-wide UX, contact, accessibility, and performance upgrades.

Run after editing HTML or site-shared.py:

    python3 scripts/upgrade-site.py
    python3 scripts/apply-seo.py
"""
import glob
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_shared import (
    MOBILE_DISPLAY,
    MOBILE_TEL,
    SKIP_LINK,
    SITE_SCRIPTS,
    SITE_SCRIPTS_SITE_ONLY,
    build_contact_block,
    build_footer_phones,
    build_homepage_hero_body,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Patterns ---

OLD_SERVICE_CONTACT_RE = re.compile(
    r'<span class="form-button"><!--email_off-->.*?</span>\s*'
    r'<span class="form-second-row">[^<]*</span>\s*'
    r'<span class="form-third-row phone-numbers">.*?</span>\s*'
    r'<span class="messenger-links">.*?</span>',
    re.DOTALL,
)

SERVICE_HERO_P_RE = re.compile(
    r'(<div class="views-field views-field-body">\s*<div class="field-content">)'
    r'<p><span class="message">([^<]*)</span>\s*'
    r'.*?'
    r'(</div>\s*</div>\s*</div>)',
    re.DOTALL,
)


def update_service_hero_contact(content):
    contact = build_contact_block(mailto_subject="Zatra%C5%BEi%20procjenu")

    def repl_hero(m):
        return (
            f'{m.group(1)}<p><span class="message">{m.group(2)}</span> '
            f"{contact}</p>{m.group(3)}"
        )

    if "block-views-contact-block-block" in content:
        if SERVICE_HERO_P_RE.search(content):
            return SERVICE_HERO_P_RE.sub(repl_hero, content, count=1)
    if OLD_SERVICE_CONTACT_RE.search(content):
        return OLD_SERVICE_CONTACT_RE.sub(contact, content, count=1)
    return content

OLD_HOMEPAGE_BLOCK6_RE = re.compile(
    r'<div class="block block-block block-6 block-block-6 odd block-without-title" id="block-block-6">'
    r".*?</div>\s*</div>\s*</div>",
    re.DOTALL,
)

HOMEPAGE_HERO_BODY_RE = re.compile(
    r'(<div class="field field-name-body field-type-text-with-summary field-label-hidden">'
    r"<div class=\"field-items\"><div class=\"field-item even\">).*?(</div></div></div>\s*</div>)",
    re.DOTALL,
)

FOOTER_PHONES_RE = re.compile(
    r'<span class="contact-strip-phones">.*?</span>',
    re.DOTALL,
)

LANDLINE_PATTERNS = [
    (re.compile(r"051\s*642\s*291"), MOBILE_DISPLAY),
    (re.compile(r"\+38551642291"), MOBILE_TEL),
    (re.compile(r"Tel:\s*051 642 291"), f"Tel: {MOBILE_DISPLAY}"),
    (re.compile(r"Nazovite 051 642 291"), f"Nazovite {MOBILE_DISPLAY}"),
    (re.compile(r'"\s*\+38551642291"\s*,?\s*'), f'"{MOBILE_TEL}"'),
    (re.compile(r'"telephone":\s*\[\s*"\+38551642291",\s*"\+38598257032"\s*\]'), f'"telephone": "{MOBILE_TEL}"'),
]

HERO_H2_RE = re.compile(
    r'(<div class="views-field views-field-title">\s*)<h2 class="field-content">([^<]+)</h2>',
)

IFRAME_SRC_RE = re.compile(
    r'(<iframe\b)(?![^>]*\bdata-src=)([^>]*?\bsrc=")([^"]+)(")',
)

FRONT_PROOF_SECTION = """
<section class="front-proof-strip" aria-labelledby="front-proof-heading">
  <div class="front-proof-inner container-12">
    <h2 id="front-proof-heading" class="front-proof-title">Iskustva korisnika</h2>
    <div class="google-reviews-badge" id="google-reviews-badge" hidden></div>
    <div class="front-testimonial-wrap">
      <div class="block block-views block-views-testimonial-block-front" id="block-views-testimonial-block-front">
        <div class="block-inner clearfix">
          <div class="content clearfix">
            <div class="view view-testimonial view-id-testimonial">
              <div class="view-content">
                <div class="views-row">
                  <div class="views-field views-field-body"><div class="field-content"><p></p></div></div>
                  <div class="views-field views-field-title"><span class="field-content"></span></div>
                  <div class="views-field views-field-field-company-link"><div class="field-content"></div></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>"""

WINDOWS_OLD = (
    "Usluga se sastoji od instalacije operativnog sustava Windows (Win 8, Win7, Vista,XP i serverskih "
    "operativnih sustava: Win Server 2003, Win Server 2008) na vaše računalo,"
)

WINDOWS_NEW = (
    "Usluga uključuje instalaciju ili reinstalaciju Windowsa (Windows 10 i 11) na vaše računalo,"
)

O_NAMA_OLD = "postojimo već 20 godina"
O_NAMA_NEW = "djelujemo u Rijeci od 1995."


def nfc(name):
    return unicodedata.normalize("NFC", name)


def add_skip_link(content):
    if 'id="skip-link"' in content:
        # Ensure skip link is inside body, not before it
        content = re.sub(
            r'<div id="skip-link">.*?</div>\s*(?=<body)',
            "",
            content,
            flags=re.DOTALL,
        )
    return re.sub(
        r"(<body[^>]*>)",
        r"\1\n" + SKIP_LINK,
        content,
        count=1,
    )


def ensure_scripts(content, *, testimonials=False):
    if "js/site.js" in content:
        snippet = SITE_SCRIPTS if testimonials else SITE_SCRIPTS_SITE_ONLY
        if testimonials and "js/testimonials.js" not in content:
            content = content.replace("</body>", snippet + "\n</body>", 1)
        return content
    snippet = SITE_SCRIPTS if testimonials else SITE_SCRIPTS_SITE_ONLY
    return content.replace("</body>", snippet + "\n</body>", 1)


def hero_h2_to_subtitle(content):
    return HERO_H2_RE.sub(r'\1<p class="hero-subtitle field-content">\2</p>', content, count=1)


def update_homepage(content):
    content = HOMEPAGE_HERO_BODY_RE.sub(
        r"\1\n" + build_homepage_hero_body() + r"\n  \2",
        content,
        count=1,
    )
    content = OLD_HOMEPAGE_BLOCK6_RE.sub("", content)
    if "front-proof-strip" not in content:
        content = content.replace(
            "</section>    \n  \n      <footer id=\"section-footer\"",
            "</section>    \n" + FRONT_PROOF_SECTION + "\n      <footer id=\"section-footer\"",
            1,
        )
    return content


def update_footer_phones(content):
    return FOOTER_PHONES_RE.sub(
        f'<span class="contact-strip-phones">{build_footer_phones()}</span>',
        content,
    )


def fix_schema_telephone(content):
    return re.sub(
        r'"telephone":\s*\[[^\]]*\]',
        f'"telephone": "{MOBILE_TEL}"',
        content,
    )


def remove_landline_refs(content):
    for pattern, repl in LANDLINE_PATTERNS:
        content = pattern.sub(repl, content)
    content = re.sub(
        r'<span class="phone-line"><span class="phone-label">Fiksni:</span>\s*'
        r'<a href="tel:\+38551642291">051 642 291</a></span>\s*',
        "",
        content,
    )
    content = re.sub(
        r'<span class="phone-line"><span class="phone-label">Mobitel:</span>\s*',
        "",
        content,
    )
    return content


def lazy_load_iframes(content):
    def repl(m):
        tag, before, url, after = m.groups()
        if "data-src" in m.group(0):
            return m.group(0)
        return f'{tag}{before}{url}{after}'.replace(f'src="{url}"', f'data-src="{url}" loading="lazy"')

    return IFRAME_SRC_RE.sub(repl, content)


def fix_content(content, basename):
    if WINDOWS_OLD in content:
        content = content.replace(WINDOWS_OLD, WINDOWS_NEW)
    if basename == "o-nama.html":
        content = content.replace("djelujemo u Rijeci od 1995..", "djelujemo u Rijeci od 1995.")
        if O_NAMA_OLD in content:
            content = content.replace(O_NAMA_OLD, O_NAMA_NEW + ".")
    return content


def process_file(path):
    basename = nfc(os.path.basename(path))
    with open(path, encoding="utf-8") as f:
        content = f.read()

    content = add_skip_link(content)
    content = remove_landline_refs(content)
    content = fix_schema_telephone(content)
    content = update_footer_phones(content)
    content = lazy_load_iframes(content)
    content = fix_content(content, basename)

    has_testimonials = "block-views-testimonial-block" in content or basename == "index.html"
    if basename != "index.html" and "block-views-contact-block-block" in content:
        content = update_service_hero_contact(content)
        content = hero_h2_to_subtitle(content)

    if basename == "index.html":
        content = update_homepage(content)

    content = ensure_scripts(content, testimonials=has_testimonials)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK {basename}")


def main():
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        process_file(path)


if __name__ == "__main__":
    main()

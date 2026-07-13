"""Shared constants and HTML snippets for site upgrade scripts."""

SITE_URL = "https://arabba.hr"
MOBILE_DISPLAY = "098 257 032"
MOBILE_TEL = "+38598257032"
EMAIL = "nenad@arabba.hr"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=Crn%C4%8Di%C4%87eva+4,+51000+Rijeka"
LINKEDIN_URL = "https://www.linkedin.com/in/nenad-blazekovic-814390123/"

OPENING_HOURS = [
    {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "08:00",
        "closes": "16:00",
    }
]

MESSENGER_LINKS = (
    '<span class="messenger-links">'
    '<a href="https://wa.me/38598257032" class="messenger-link messenger-whatsapp" data-track="whatsapp" '
    'aria-label="Pošaljite WhatsApp poruku">'
    '<img src="images/icon-whatsapp.svg" width="28" height="28" alt="" role="presentation"><span>WhatsApp</span></a>'
    '<a href="viber://chat?number=38598257032" class="messenger-link messenger-viber" data-track="viber" '
    'aria-label="Pošaljite Viber poruku">'
    '<img src="images/icon-viber.svg" width="28" height="28" alt="" role="presentation"><span>Viber</span></a>'
    "</span>"
)

FOOTER_MESSENGER_LINKS = MESSENGER_LINKS.replace('width="28" height="28"', 'width="20" height="20"')

SKIP_LINK = (
    '<div id="skip-link">'
    '<a href="#main-content" class="element-invisible element-focusable">Preskoči na sadržaj</a>'
    "</div>"
)

SITE_SCRIPTS = (
    '  <script src="js/site.js" defer></script>\n'
    '  <script src="js/testimonials.js" defer></script>'
)

SITE_SCRIPTS_SITE_ONLY = '  <script src="js/site.js" defer></script>'


def build_contact_block(*, mailto_subject=None, email_label=None):
    """Primary phone, messengers, secondary email — hero / service page CTA block."""
    mailto = f"mailto:{EMAIL}"
    if mailto_subject:
        mailto += f"?subject={mailto_subject}"
    label = email_label or ("Pošaljite mail za procjenu" if mailto_subject else EMAIL)
    return (
        f'<a href="tel:{MOBILE_TEL}" class="hero-phone-primary" data-track="phone">{MOBILE_DISPLAY}</a>\n'
        f"{MESSENGER_LINKS}\n"
        f'<span class="hero-email-secondary"><!--email_off-->'
        f'<a href="{mailto}" data-track="email">{label}</a>'
        f"<!--/email_off--></span>"
    )


def build_homepage_hero_body():
    return (
        "<p>Usluge popravka računala i laptopa su naša specijalnost. "
        "Vaše računalo će raditi brzo i stabilno.</p>\n"
        + build_contact_block(email_label=EMAIL)
    )


def build_footer_phones():
    return f'<a href="tel:{MOBILE_TEL}">{MOBILE_DISPLAY}</a>'


def render_stars_html(rating):
    full = min(5, max(0, int(round(float(rating)))))
    html = '<span class="star star-full" aria-hidden="true">★</span>' * full
    html += '<span class="star star-empty" aria-hidden="true">☆</span>' * (5 - full)
    return html


def build_google_reviews_badge(reviews, *, compact=False):
    rating = reviews.get("rating")
    count = reviews.get("reviewCount")
    if rating is None or count is None:
        return ""
    url = reviews.get("googleMapsUrl") or MAPS_URL
    rating_str = f"{float(rating):.1f}".replace(".", ",")
    stars = render_stars_html(float(rating))
    label = f"<strong>{rating_str}/5</strong> · {count} Google recenzija"
    if compact:
        return (
            f'<p class="hero-google-rating">'
            f'<a href="{url}" target="_blank" rel="noopener noreferrer" data-track="google_reviews">'
            f'<span class="google-reviews-stars" aria-hidden="true">{stars}</span> '
            f"{label}</a></p>"
        )
    return (
        f'<div class="google-reviews-badge" id="google-reviews-badge">\n'
        f'  <a class="google-reviews-link" href="{url}" target="_blank" rel="noopener noreferrer" '
        f'data-track="google_reviews">\n'
        f'    <span class="google-reviews-stars" aria-hidden="true">{stars}</span>\n'
        f'    <span class="google-reviews-text">{label}</span>\n'
        f"  </a>\n"
        f"</div>"
    )

# arabba.site

Static website source for [ARABBA d.o.o.](https://arabba.hr/), a computer repair and IT services company based in Rijeka, Croatia.

**Live site:** [https://arabba.hr/](https://arabba.hr/)

## About ARABBA

ARABBA d.o.o. has provided electronics repair and computer services in Rijeka since 1995. The company specializes in diagnosing and repairing PC and Mac desktops and laptops, with a focus on thorough diagnostics, high-quality repairs, and clear customer communication throughout the service process.

**Founder & director:** Nenad Blažeković

**Address:** Crnčićeva 4, 51000 Rijeka, Croatia  
**Phone:** [098 257 032](tel:+38598257032)  
**Email:** [nenad@arabba.hr](mailto:nenad@arabba.hr)  
**Service area:** Rijeka and surrounding area

## Services

- Computer repair and diagnostics
- Laptop repair (HP, ASUS, MSI, Apple, Acer, Toshiba, Lenovo, and others)
- Contract system maintenance
- Computer cleaning, optimization, and performance tuning
- Antivirus, antispyware, and security protection
- Network system installation and maintenance
- Virus and spyware removal
- Data backup and recovery

## Repository

Static HTML site for [arabba.hr](https://arabba.hr/). No build step required, deploy the files as-is to any static host.

```
.
├── index.html          # Homepage
├── o-nama.html         # About us
├── gdje-smo.html       # Location / contact map
├── podaci-o-firmi.html # Company details
├── servis-*.html       # Service pages
├── css/site.css        # All styles (single bundle)
├── js/testimonials.js  # Testimonial carousel on service pages
├── js/site.js          # Analytics, Google reviews badge, lazy media
├── data/google-reviews.json  # Cached Google rating (see scripts below)
└── images/             # Logos, photos, icons
```

**Site maintenance scripts** (run from repo root):

```bash
python3 scripts/upgrade-site.py   # Contact CTAs, a11y, performance
python3 scripts/apply-seo.py      # Meta tags, schema, GA4

# Google reviews badge (needs Places API key, or manual values):
GOOGLE_PLACES_API_KEY=... python3 scripts/fetch-google-reviews.py
python3 scripts/fetch-google-reviews.py --rating 4.9 --count 38
python3 scripts/apply-seo.py      # Re-apply schema with AggregateRating
```

To preview locally:

```bash
python3 -m http.server 8000
```

Then visit [http://localhost:8000](http://localhost:8000).

### Deployment notes

Pages use `.html` URLs (e.g. `/servis-racunala.html`). Deploy the files as-is to any static host, no URL rewriting or redirects required.

## License

© ARABBA d.o.o. 1995–2026. All rights reserved.

#!/usr/bin/env python3
"""Build the four single-language pages from src/template.html.

The template holds every string four times as
<span data-lang="et|fi|sv|en">…</span>. For each language this script keeps
only that language's span, unwraps it, swaps in per-language <head> metadata,
hreflang, JSON-LD and a real <a> language switcher, and writes the page.

    python3 tools/build.py          # build everything
    python3 tools/build.py --check  # parse only, write nothing
"""

import json, re, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "src" / "template.html"
SITE = "https://www.dsonordic.com"
LANGS = ("et", "fi", "sv", "en")
PATHS = {"et": "/", "fi": "/fi/", "sv": "/sv/", "en": "/en/"}
OUT = {"et": ROOT / "index.html", "fi": ROOT / "fi" / "index.html",
       "sv": ROOT / "sv" / "index.html", "en": ROOT / "en" / "index.html"}
OG_LOCALE = {"et": "et_EE", "fi": "fi_FI", "sv": "sv_SE", "en": "en_GB"}
LANG_NAME = {"et": "Eesti", "fi": "Suomi", "sv": "Svenska", "en": "English"}
FLAG = {"et": "eestilipp.png", "fi": "soomelipp.png",
        "sv": "rootsilipp.png", "en": "uklipp.png"}

META = {
    "et": dict(
        title="Sõidukite desinfitseerimisvärav farmidele | DSO Nordic",
        desc="Automaatne sõidukite desinfitseerimisvärav farmidele. Töötab −20 °C kuni +40 °C, tsükkel kuni 60 sekundit. Projekteeritud ja toodetud Eestis.",
        ogtitle="DSO Nordic — sõidukite desinfitseerimisvärav farmidele"),
    "fi": dict(
        title="Ajoneuvojen desinfiointiportti tiloille | DSO Nordic",
        desc="Automaattinen ajoneuvojen desinfiointiportti maatiloille. Toimii −20 °C…+40 °C, sykli enintään 60 sekuntia. Suunniteltu ja valmistettu Virossa.",
        ogtitle="DSO Nordic — ajoneuvojen desinfiointiportti tiloille"),
    "sv": dict(
        title="Desinfektionsport för fordon till gårdar | DSO Nordic",
        desc="Automatisk desinfektionsport för fordon till lantgårdar. Fungerar −20 °C till +40 °C, cykel upp till 60 sekunder. Konstruerad och tillverkad i Estland.",
        ogtitle="DSO Nordic — desinfektionsport för fordon till gårdar"),
    "en": dict(
        title="Vehicle Disinfection Gate for Farms | DSO Nordic",
        desc="Automated vehicle disinfection gate for farms. Operates from −20 °C to +40 °C with a cycle of up to 60 seconds. Designed and manufactured in Estonia.",
        ogtitle="DSO Nordic — vehicle disinfection gate for farms"),
}

# FAQ lives in template groups 104..119 as Q,A,Q,A…
FAQ_FIRST, FAQ_PAIRS = 104, 8

GROUP_RE = re.compile(
    r'<span data-lang="et"[^>]*>(.*?)</span>\s*'
    r'<span data-lang="fi"[^>]*>(.*?)</span>\s*'
    r'<span data-lang="sv"[^>]*>(.*?)</span>\s*'
    r'<span data-lang="en"[^>]*>(.*?)</span>', re.S)


def text(x: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x))).strip()


def head_block(lang: str) -> str:
    m = META[lang]
    url = SITE + PATHS[lang]
    alts = "\n".join(
        f'  <link rel="alternate" hreflang="{l}" href="{SITE}{PATHS[l]}" />' for l in LANGS)
    alt_locales = "\n".join(
        f'  <meta property="og:locale:alternate" content="{OG_LOCALE[l]}" />'
        for l in LANGS if l != lang)
    return f"""  <title>{m['title']}</title>
  <meta name="description" content="{m['desc']}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta name="author" content="FerWorks OÜ / DSO Nordic" />
  <link rel="canonical" href="{url}" />
{alts}
  <link rel="alternate" hreflang="x-default" href="{SITE}/" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="DSO Nordic" />
  <meta property="og:locale" content="{OG_LOCALE[lang]}" />
{alt_locales}
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{m['ogtitle']}" />
  <meta property="og:description" content="{m['desc']}" />
  <meta property="og:image" content="{SITE}/image/og-dso-nordic.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="DSO Nordic vehicle disinfection gate" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{m['ogtitle']}" />
  <meta name="twitter:description" content="{m['desc']}" />
  <meta name="twitter:image" content="{SITE}/image/og-dso-nordic.jpg" />
  <meta name="twitter:image:alt" content="DSO Nordic vehicle disinfection gate" />"""


def jsonld(lang: str, groups) -> str:
    url = SITE + PATHS[lang]
    i = LANGS.index(lang)
    faq = []
    for p in range(FAQ_PAIRS):
        q = text(groups[FAQ_FIRST + p * 2][i])
        a = text(groups[FAQ_FIRST + p * 2 + 1][i])
        if q and a:
            faq.append({"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}})
    graph = [
        {"@type": "Organization", "@id": f"{SITE}/#org",
         "name": "FerWorks OÜ", "legalName": "FerWorks OÜ",
         "url": "https://ferworks.eu/", "email": "mail@ferworks.eu",
         "telephone": "+372 511 6641",
         "vatID": "EE101830645",
         "taxID": "12525392",
         "identifier": [
             {"@type": "PropertyValue", "name": "Estonian business registry code",
              "propertyID": "EE-registrikood", "value": "12525392"},
             {"@type": "PropertyValue", "name": "VAT number",
              "propertyID": "EU-VAT", "value": "EE101830645"},
         ],
         "address": {"@type": "PostalAddress",
                     "streetAddress": "Kuremäe-Tuuleveski",
                     "addressLocality": "Kihlevere",
                     "addressRegion": "Lääne-Viru maakond",
                     "postalCode": "45215",
                     "addressCountry": "EE"},
         "sameAs": ["https://ferworks.eu/",
                    "https://www.teatmik.ee/et/personlegal/12525392-FerWorks-O%C3%9C",
                    "https://share.google/dui6Gz2p7v0u2OCfx"],
         "brand": {"@type": "Brand", "name": "DSO Nordic", "@id": f"{SITE}/#brand"}},
        {"@type": "Brand", "@id": f"{SITE}/#brand", "name": "DSO Nordic",
         "url": SITE + "/", "logo": f"{SITE}/image/og-dso-nordic.jpg"},
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": SITE + "/",
         "name": "DSO Nordic", "inLanguage": lang,
         "publisher": {"@id": f"{SITE}/#org"}},
        {"@type": "WebPage", "@id": url + "#webpage", "url": url,
         "name": META[lang]["title"], "inLanguage": lang,
         "isPartOf": {"@id": f"{SITE}/#website"},
         "about": {"@id": f"{SITE}/#product"},
         "primaryImageOfPage": f"{SITE}/image/og-dso-nordic.jpg"},
        {"@type": "Product", "@id": f"{SITE}/#product", "name": "DSO Nordic",
         "description": META[lang]["desc"],
         "image": [f"{SITE}/image/og-dso-nordic.jpg",
                   f"{SITE}/image/dso-nordic-gate.webp"],
         "brand": {"@id": f"{SITE}/#brand"},
         "manufacturer": {"@id": f"{SITE}/#org"},
         "countryOfOrigin": {"@type": "Country", "name": "Estonia"},
         "category": "Agricultural biosecurity equipment",
         "additionalProperty": [
             {"@type": "PropertyValue", "name": "Operating temperature", "value": "−20 °C to +40 °C"},
             {"@type": "PropertyValue", "name": "Cycle duration", "value": "Up to 60 s"},
             {"@type": "PropertyValue", "name": "Spray rate", "value": "100 L/min"},
             {"@type": "PropertyValue", "name": "Spray pressure", "value": "approx. 4 bar"},
             {"@type": "PropertyValue", "name": "Internal dimensions", "value": "4.0 m × 4.8 m"},
             {"@type": "PropertyValue", "name": "External dimensions", "value": "5.4 m × 5.1 m"},
             {"@type": "PropertyValue", "name": "Material", "value": "Galvanised and stainless steel"},
             {"@type": "PropertyValue", "name": "Tank", "value": "1000 L IBC (PE)"},
             {"@type": "PropertyValue", "name": "Power supply", "value": "380 V / IP66 · CEE 16A three-phase"},
             {"@type": "PropertyValue", "name": "Noise level", "value": "≤ 70 dB(A)"},
             {"@type": "PropertyValue", "name": "Installation area", "value": "7 m × 3 m"},
             {"@type": "PropertyValue", "name": "Max vehicle height", "value": "4 m"},
             {"@type": "PropertyValue", "name": "Min ground clearance", "value": "120 mm"},
             {"@type": "PropertyValue", "name": "Lead time", "value": "6–8 weeks"},
         ],
         "offers": {"@type": "Offer", "availability": "https://schema.org/InStock",
                    "priceCurrency": "EUR", "url": url,
                    "seller": {"@id": f"{SITE}/#org"},
                    "areaServed": [{"@type": "Country", "name": n}
                                   for n in ("Estonia", "Finland", "Sweden", "Latvia", "Lithuania")]}},
    ]
    if faq:
        graph.append({"@type": "FAQPage", "@id": url + "#faq",
                      "inLanguage": lang, "mainEntity": faq})
    doc = {"@context": "https://schema.org", "@graph": graph}
    return ('  <script type="application/ld+json">\n'
            + json.dumps(doc, ensure_ascii=False, indent=2)
            + "\n  </script>")


def switcher(lang: str) -> str:
    out = ['<div class="lang-switcher" role="group" aria-label="Language">']
    for l in LANGS:
        cur = ' aria-current="true"' if l == lang else ""
        style = ("display:inline-block;width:32px;height:24px;padding:0;margin:0 4px;"
                 "opacity:" + ("1" if l == lang else ".55") + ";")
        out.append(
            f'        <a class="lang-flag" href="{PATHS[l]}" hreflang="{l}" lang="{l}" '
            f'title="{LANG_NAME[l]}" aria-label="{LANG_NAME[l]}"{cur} style="{style}">'
            f'<img src="/image/{FLAG[l]}" alt="" width="32" height="24" loading="lazy" '
            f'decoding="async" style="width:100%;height:100%;object-fit:cover;border-radius:2px;"></a>')
    out.append("      </div>")
    return "\n".join(out)


def build(lang: str, tpl: str, groups) -> str:
    s = tpl
    # 1. head
    s = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', s, count=1)
    start = s.find("  <title>")
    end = s.find("\n", s.find('rel="canonical"'))
    s = s[:start] + head_block(lang) + "\n" + jsonld(lang, groups) + s[end:]
    # 2. keep only this language, unwrap
    others = [l for l in LANGS if l != lang]
    s = re.sub(r'<span data-lang="(?:%s)"[^>]*>.*?</span>\s*' % "|".join(others),
               "", s, flags=re.S)
    s = re.sub(r'<span data-lang="%s"[^>]*>(.*?)</span>' % lang, r"\1", s, flags=re.S)
    # 3. real links instead of JS buttons
    s = re.sub(r'<div class="lang-switcher".*?</div>', switcher(lang), s, count=1, flags=re.S)
    # 4. drop the language JS (no longer needed)
    s = re.sub(r'\n\s*function setLanguage\(lang\).*?\}\)\(\);', "", s, flags=re.S)
    # 5. hero image -> optimised, responsive, explicit box
    s = re.sub(
        r'src="Image/IMG_9338\.JPG"',
        'src="/image/dso-nordic-gate.webp" '
        'srcset="/image/dso-nordic-gate-960.webp 675w, /image/dso-nordic-gate.webp 1050w" '
        'sizes="(max-width: 900px) 90vw, 1050px" '
        'width="1050" height="1400" fetchpriority="high" decoding="async"',
        s)
    # any remaining uppercase asset path
    s = s.replace("Image/", "image/")
    if "IMG_9338" in s:
        raise SystemExit("unreplaced reference to the original hero file")
    return s


def main() -> None:
    tpl = TEMPLATE.read_text()
    groups = GROUP_RE.findall(tpl)
    if len(groups) != 129:
        sys.exit(f"expected 129 translation groups, found {len(groups)}")
    check = "--check" in sys.argv
    for lang in LANGS:
        page = build(lang, tpl, groups)
        leftover = len(re.findall(r'data-lang="', page))
        if leftover:
            sys.exit(f"{lang}: {leftover} data-lang attributes left behind")
        json.loads(re.search(r'application/ld\+json">\s*(\{.*?\})\s*</script>',
                             page, re.S).group(1))
        if not check:
            OUT[lang].parent.mkdir(parents=True, exist_ok=True)
            OUT[lang].write_text(page)
        print(f"  {lang}: {len(page)/1024:6.1f} KB  ->  {OUT[lang].relative_to(ROOT)}")
    print("  check only, nothing written" if check else "  built 4 pages")


if __name__ == "__main__":
    main()

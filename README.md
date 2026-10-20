# DSO Nordic

Static marketing site for the DSO Nordic vehicle disinfection gate, manufactured
by FerWorks OÜ. Hosted on Vercel.

## Structure

The four language versions are **generated**, not edited by hand.

```
src/template.html   single source — every string four times as
                    <span data-lang="et|fi|sv|en">…</span>
tools/build.py      generates the four pages from the template
index.html          generated — Estonian  (/)
fi/ sv/ en/         generated — Finnish, Swedish, English
```

Edit `src/template.html`, then rebuild:

```bash
python3 tools/build.py --check   # parse and validate, write nothing
python3 tools/build.py           # write the four pages
```

The build fails loudly if a translation group is missing, if any `data-lang`
attribute survives into output, or if the JSON-LD does not parse.

## What the build adds per language

Canonical, full `hreflang` cluster (including `x-default`), localised title,
description and Open Graph, `og:locale` plus alternates, and JSON-LD
(`Organization`, `Brand`, `WebSite`, `WebPage`, `Product` with the full spec
table, `FAQPage` built from the page's own questions).

## Images

`image/` holds only what the site uses. The hero is served as WebP at two
widths through `srcset`. Originals are not kept in the repo — keep them
somewhere else and re-export if they change.

## Other files

`robots.txt`, `sitemap.xml` (with hreflang alternates), `llms.txt` (for AI
answer engines), `vercel.json` (redirects for the retired URLs, long cache on
`/image/`).

The tool:

- map: url = "https://docs.document360.com/sitemap-en.xml" # sitemap defining job scope (all links)
- nav: url # page to gather navigation, uses first sitemap link if not provided
- dir: str | Path # work folder, defaults to cwd + domain of map url (e.g., "./site.document360.com") 
- css: str | Path # path to CSS file for site.html, defaults to `d361_offline`
- effort: bool = False # attempt to mirror all map links in navigation

## prep phase

- Read the `map` and build a flat list of target URLs

- Visit the `nav` page and extract navigation structure. Map page URLs between the sitemap and navigation. If `effort` is True, aggressively match all sitemap links.

- FIXME: Write `nav.json`, `nav.md`, and `nav.html` files to `dir`

## fetch phase

- Create `html` and `md` folders in `dir`

- Mirror all pages from `map` into `html` folder, storing only H1 and article elements. Use `map` as it's flat and authoritative.

- Convert each HTML file to markdown and save in `md` folder

## build phase

- With all pages and navigation data collected, build final output files

- Create single `site.html` and `site.md` files combining all content
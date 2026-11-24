#!/usr/bin/env python3
"""Builds the English version of the site in en/ from the Russian pages.

Usage (from the site root):  python scripts/build-en.py

- Translations live in scripts/i18n/en.json as {"Russian text": "English text"}.
  If a Russian page changes, the script lists the new phrases that have no
  translation yet; add them to en.json and run the script again.
- Adds the RU/EN switcher and hreflang tags to every Russian and English page.
- BASE is the path the site is served from: "/matrixlab" on
  haritoilya.github.io/matrixlab/, "" on the matrixlab.pro domain.
  SITE_URL is the full address used in hreflang tags.
"""
import json, os, re, sys, glob

BASE = ""
SITE_URL = "https://matrixlab.pro"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CYR = re.compile('[А-Яа-яЁё]')
BLOCK = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->)', re.S | re.I)
TEXT = re.compile(r'>([^<]+)<')
ATTR = re.compile(r'\b(alt|title|content|placeholder|aria-label|value)="([^"]*)"')
SWITCH = re.compile(r'\s*<!--lang-switch-->.*?<!--/lang-switch-->', re.S)
HREFLANG = re.compile(r'\s*<!--hreflang-->.*?<!--/hreflang-->', re.S)
# the old builder's "EN" header item: an empty link in white text
OLD_EN = re.compile(r'<li class="[^"]*link-item[^"]*"><a href="" class="[^"]*" style="color: #FFFFFF;">\s*EN\s*</a></li>')


def split_ws(s):
    m = re.match(r'^(\s*)(.*?)(\s*)$', s, re.S)
    return m.group(1), m.group(2), m.group(3)


def translate(html, fn):
    parts = BLOCK.split(html)
    for i in range(0, len(parts), 2):
        p = parts[i]

        def text(m):
            a, b, c = split_ws(m.group(1))
            if b and CYR.search(b):
                return '>' + a + fn(b) + c + '<'
            return m.group(0)

        def attr(m):
            a, b, c = split_ws(m.group(2))
            if b and CYR.search(b):
                return '%s="%s%s%s"' % (m.group(1), a, fn(b).replace('"', '&quot;'), c)
            return m.group(0)

        p = TEXT.sub(text, p)
        p = re.sub(r'<[a-zA-Z][^>]*>', lambda t: ATTR.sub(attr, t.group(0)), p)
        parts[i] = p
    return ''.join(parts)


def page_path(rel):
    """'product/index.html' -> 'product', 'index.html' -> ''"""
    d = os.path.dirname(rel)
    return d.replace(os.sep, '/')


def url(lang, path):
    prefix = BASE + ('/en' if lang == 'en' else '')
    return prefix + '/' + path if path else prefix + '/'


def decorate(html, lang, path):
    html = SWITCH.sub('', html)
    html = HREFLANG.sub('', html)
    html = OLD_EN.sub('', html)
    ru, en = url('ru', path), url('en', path)
    tags = ('\n<!--hreflang--><link rel="alternate" hreflang="ru" href="%s%s">'
            '<link rel="alternate" hreflang="en" href="%s%s"><!--/hreflang-->'
            % (SITE_URL, ru[len(BASE):], SITE_URL, en[len(BASE):]))
    html = html.replace('</head>', tags + '\n</head>', 1)
    switch = ('\n<!--lang-switch--><nav class="ml-lang" aria-label="%s">'
              '<a href="%s" hreflang="ru" lang="ru"%s>RU</a>'
              '<a href="%s" hreflang="en" lang="en"%s>EN</a></nav><!--/lang-switch-->'
              % ('Language' if lang == 'en' else 'Язык',
                 ru, ' aria-current="true"' if lang == 'ru' else '',
                 en, ' aria-current="true"' if lang == 'en' else ''))
    return html.replace('</body>', switch + '\n</body>', 1)


def main():
    tr = json.load(open(os.path.join(ROOT, 'scripts/i18n/en.json'), encoding='utf-8'))
    pages = sorted(os.path.relpath(f, ROOT) for f in glob.glob(os.path.join(ROOT, '**/index.html'), recursive=True)
                   if not os.path.relpath(f, ROOT).startswith('en' + os.sep))
    missing = []

    def fn(s):
        if s in tr:
            return tr[s]
        missing.append(s)
        return s

    page_re = re.compile(r'href="%s/(?!assets/|files/|en/)' % re.escape(BASE))
    for rel in pages:
        src = os.path.join(ROOT, rel)
        ru_html = open(src, encoding='utf-8').read()
        path = page_path(rel)
        en_html = translate(SWITCH.sub('', HREFLANG.sub('', ru_html)), fn)
        en_html = en_html.replace('<html lang="ru"', '<html lang="en"', 1)
        en_html = page_re.sub('href="%s/en/' % BASE, en_html)
        en_html = decorate(en_html, 'en', path)
        out = os.path.join(ROOT, 'en', rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8', newline='\n').write(en_html)
        open(src, 'w', encoding='utf-8', newline='\n').write(decorate(ru_html, 'ru', path))

    if missing:
        print('No translation for %d phrase(s); add them to scripts/i18n/en.json:' % len(set(missing)))
        for s in dict.fromkeys(missing):
            print('  ' + json.dumps(s, ensure_ascii=False))
        sys.exit(1)
    print('Built %d English pages in en/' % len(pages))


if __name__ == '__main__':
    main()

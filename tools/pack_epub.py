# -*- coding: utf-8 -*-
"""Доводит каталог out_epub до EPUB 3 и собирает архив."""
from paths import EPUB_OUT
import os, re, html, zipfile, datetime, json, shutil
OUT = "out_epub"
DEST = EPUB_OUT

def nav_from_ncx(ncx):
    items = re.findall(r'<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*'
                       r'<content src="(.*?)"\s*/>', ncx, re.S)
    li = "\n".join(f'      <li><a href="{src}">{html.escape(re.sub(r"\s+"," ",t).strip())}</a></li>'
                   for t, src in items)
    li += '\n      <li><a href="notes.xhtml">Комментарии и примечания</a></li>'
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
            '<head><meta charset="utf-8"/><title>Оглавление</title></head>\n<body>\n'
            '  <nav epub:type="toc" id="toc"><h1>Оглавление</h1>\n    <ol>\n'
            + li + '\n    </ol>\n  </nav>\n</body>\n</html>\n')

TITLE = "Гарри Поттер и методы рационального мышления (с комментариями)"
COVER = "fb2__0.jpg"          # «общая» обложка, извлечённая из fb2

def main():
    im_w, im_h = __import__("PIL.Image", fromlist=["Image"]).open(COVER).size
    shutil.copyfile(COVER, os.path.join(OUT, "cover.jpg"))
    tp = open(os.path.join(OUT, "titlepage.xhtml"), encoding="utf-8").read()
    tp = re.sub(r'viewBox="0 0 \d+ \d+"', f'viewBox="0 0 {im_w} {im_h}"', tp)
    tp = re.sub(r'width="\d+" height="\d+"', f'width="{im_w}" height="{im_h}"', tp)
    open(os.path.join(OUT, "titlepage.xhtml"), "w", encoding="utf-8").write(tp)

    ncx = open(os.path.join(OUT, "toc.ncx"), encoding="utf-8").read()
    open(os.path.join(OUT, "nav.xhtml"), "w", encoding="utf-8").write(nav_from_ncx(ncx))

    opf = open(os.path.join(OUT, "content.opf"), encoding="utf-8").read()
    opf = opf.replace('<package version="2.0"', '<package version="3.0"')
    opf = re.sub(r'\s+opf:(file-as|role|event|scheme)="[^"]*"', '', opf)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = opf.replace('</metadata>',
                      f'    <meta property="dcterms:modified">{now}</meta>\n  </metadata>')
    opf = opf.replace('<manifest>',
                      '<manifest>\n'
                      '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>\n'
                      '    <item id="notes" href="notes.xhtml" media-type="application/xhtml+xml"/>')
    opf = re.sub(r'<dc:title>.*?</dc:title>', f'<dc:title>{html.escape(TITLE)}</dc:title>', opf)
    opf = opf.replace('<item id="cover.jpg" href="cover.jpg" media-type="image/jpeg"/>',
                      '<item id="cover.jpg" href="cover.jpg" media-type="image/jpeg" '
                      'properties="cover-image"/>')
    opf = opf.replace('</spine>', '    <itemref idref="notes"/>\n  </spine>')
    open(os.path.join(OUT, "content.opf"), "w", encoding="utf-8").write(opf)
    ncx2 = re.sub(r'<text>[^<]*</text>', f'<text>{html.escape(TITLE)}</text>', ncx, count=1)
    open(os.path.join(OUT, "toc.ncx"), "w", encoding="utf-8").write(ncx2)

    if os.path.exists(DEST): os.remove(DEST)
    with zipfile.ZipFile(DEST, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        for root, _, files in os.walk(OUT):
            for fn in sorted(files):
                if fn == "mimetype": continue
                p = os.path.join(root, fn)
                z.write(p, os.path.relpath(p, OUT), compress_type=zipfile.ZIP_DEFLATED)
    print(f"{DEST}  {os.path.getsize(DEST)/1e6:.2f} МБ")

if __name__ == "__main__":
    main()

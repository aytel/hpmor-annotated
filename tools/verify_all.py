# -*- coding: utf-8 -*-
from paths import FB2_OUT
import re, glob, os, json, html
from lxml import etree
ok = True
def say(t, good=True):
    global ok
    ok &= good
    print(("  ✔ " if good else "  ✘ ") + t)

print("EPUB")
bad = []
for f in glob.glob("out_epub/*.*html") + ["out_epub/content.opf", "out_epub/toc.ncx"]:
    try: etree.parse(f)
    except Exception as e: bad.append((f, str(e)[:70]))
say(f"XML корректен во всех {len(glob.glob('out_epub/*.*html'))+2} файлах", not bad)
for b in bad: print("     ", b)
ids = set(re.findall(r'<aside[^>]*id="(n\d+)"', open("out_epub/notes.xhtml", encoding="utf-8").read()))
refs = []
for f in glob.glob("out_epub/*.html"):
    refs += re.findall(r'href="notes\.xhtml#(n\d+)"', open(f, encoding="utf-8").read())
say(f"маркеров {len(refs)}, сносок {len(ids)}, все ссылки разрешаются",
    len(refs) == len(ids) == 339 and not set(refs) - ids and not ids - set(refs))
nt = open("out_epub/notes.xhtml", encoding="utf-8").read()
xr = re.findall(r'<a href="#(n\d+)">', nt)
say(f"перекрёстных ссылок между сносками: {len(xr)}, все целы", all(x in ids for x in xr))
opf = open("out_epub/content.opf", encoding="utf-8").read()
say("пакет объявлен как EPUB 3.0", '<package version="3.0"' in opf)
say("есть nav и страница примечаний в spine",
    'properties="nav"' in opf and 'idref="notes"' in opf)

print("\nFB2")
P = FB2_OUT
try:
    t = etree.parse(P); say("XML корректен")
except Exception as e:
    say(f"XML сломан: {e}", False); raise SystemExit
NS = "{http://www.gribuser.ru/xml/fictionbook/2.0}"
r = t.getroot()
notes_body = [b for b in r.findall(NS + "body") if b.get("name") == "notes"]
say("есть <body name=\"notes\">", len(notes_body) == 1)
nid = {s.get("id") for s in notes_body[0].findall(NS + "section")}
mk = [a.get("{http://www.w3.org/1999/xlink}href").lstrip("#")
      for a in r.iter(NS + "a") if a.get("type") == "note"]
say(f"маркеров {len(mk)}, сносок {len(nid)}, все ссылки разрешаются",
    len(nid) == 339 and not set(mk) - nid)
print("\nИТОГ:", "всё сошлось" if ok else "ЕСТЬ ПРОБЛЕМЫ")

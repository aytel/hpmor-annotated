# -*- coding: utf-8 -*-
from paths import FB2_IN
import re, glob, os, bisect
import xmlindex
from norm import norm_map
EPUB_DIR = "ep"

def epub_chapters():
    """{номер главы: (путь, сырой текст, plain, offs, ntext, nidx)}"""
    out = {}
    for f in sorted(glob.glob(os.path.join(EPUB_DIR, "index-*.html"))):
        raw = open(f, encoding="utf-8").read()
        b = raw.find("<body")
        if b < 0: continue
        plain, offs, ends = xmlindex.build(raw, raw.index(">", b) + 1)
        m = re.search(r'Глава\s+(\d+)\.', plain[:200])
        if not m: continue
        ntext, nidx = norm_map(plain)
        out[int(m.group(1))] = dict(path=f, raw=raw, plain=plain, offs=offs, ends=ends, ntext=ntext, nidx=nidx)
    return out

def fb2_chapters(path=None):
    """Одним проходом строим плоский текст всего файла, затем режем по <section>."""
    raw = open(path or FB2_IN, encoding="utf-8").read()
    body = raw.index("<body")
    plain, offs, ends = xmlindex.build(raw, raw.index(">", body) + 1)
    out = {}
    for m in re.finditer(r"<section>", raw):
        s_raw, e_raw = m.end(), raw.find("</section>", m.end())
        i = bisect.bisect_left(offs, s_raw); j = bisect.bisect_left(offs, e_raw)
        seg, segoffs, segends = plain[i:j], offs[i:j], ends[i:j]
        mm = re.search(r"Глава\s+(\d+)\.", seg[:200])
        if not mm: continue
        ntext, nidx = norm_map(seg)
        out[int(mm.group(1))] = dict(path=path, raw=raw, plain=seg, offs=segoffs, ends=segends,
                                     ntext=ntext, nidx=nidx)
    return raw, out

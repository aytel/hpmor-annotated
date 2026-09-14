# -*- coding: utf-8 -*-
"""Контроль: кроме задуманных правок, текст книги не должен измениться."""
import re, html, difflib, glob, os
def strip(t):
    t = re.sub(r'<a[^>]*(?:epub:type="noteref"|type="note")[^>]*>.*?</a>', '', t, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t))).strip()

tot_old = tot_new = 0; diffs = []
for f in sorted(glob.glob("ep/index-*.html")):
    o = strip(open(f, encoding="utf-8").read())
    n = strip(open(os.path.join("out_epub", os.path.basename(f)), encoding="utf-8").read())
    tot_old += len(o); tot_new += len(n)
    if o == n: continue
    ow, nw = o.split(), n.split()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ow, nw, autojunk=False).get_opcodes():
        if tag == "equal": continue
        diffs.append((os.path.basename(f), tag, " ".join(ow[i1:i2]), " ".join(nw[j1:j2])))
print(f"символов: было {tot_old}, стало {tot_new} (разница {tot_new-tot_old})")
print(f"изменённых мест: {len(diffs)}\n")
for f, tag, a, b in diffs:
    print(f'[{tag}] {f}\n   было : {a[:170]!r}\n   стало: {b[:170]!r}')

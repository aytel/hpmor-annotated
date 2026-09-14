# -*- coding: utf-8 -*-
"""Склеивает основной текст каждого тома в непрерывную строку с картой страниц,
находит позиции звёздочек-якорей и начала глав."""
import json, re
HYPH = set(json.load(open("hyphenated.json")))
P = json.load(open("pages_clean.json"))
NOTES_START = {"1": 589, "2": 577, "3": 665}
FOLIO = re.compile(r'^\s*\d{1,3}\s*$')
SEP   = re.compile(r'^[\s*]*$')
CONV  = re.compile(r'^\s*\*\s*Здесь и далее звёздочкой')
W = r'[А-Яа-яЁёA-Za-z]'

def join(lines):
    out = ""
    for ln in lines:
        ln = ln.replace('­', '').rstrip()
        if not ln: continue
        if out.endswith('-') and re.match(W, ln):
            t = re.search(r'([А-Яа-яЁёA-Za-z]+)-$', out); h = re.match(r'([А-Яа-яЁёA-Za-z]+)', ln)
            keep = bool(t and h and (t.group(1)+'-'+h.group(1)).lower().replace('ё','е') in HYPH)
            out = out + ln if keep or ln[:1].isupper() else out[:-1] + ln
        elif out.endswith(('–', '—')) and ln[:1].isdigit():
            out = out + ln
        else:
            out = (out + ' ' + ln) if out else ln
    return out

FIRST_CH = {"1": 1, "2": 38, "3": 78}
books = {}
for vol in "123":
    text, page_at, chapters = "", [], []   # page_at: (offset, page)
    for pno in range(1, NOTES_START[vol]):
        raw = P[vol][pno-1].split("\n")
        if any(CONV.match(l) for l in raw):
            raw = [l for l in raw if not CONV.match(l)]
        lines = [l for l in raw if not FOLIO.match(l) and not (SEP.match(l) and l.strip())]
        ptext = join(lines)
        exp = chapters[-1]["num"] + 1 if chapters else FIRST_CH[vol]
        m = re.search(r'Глава %d\b' % exp, ptext[:600])
        if m: chapters.append({"num": exp, "page": pno,
                               "offset": len(text) + 1 + m.start()})
        page_at.append((len(text)+1, pno))
        text += " " + ptext
    anchors = [{"pos": m.start(), "page": max(p for o,p in page_at if o <= m.start())}
               for m in re.finditer(r'\*', text)]
    for a in anchors:
        a["before"] = text[max(0,a["pos"]-250):a["pos"]]
        a["after"]  = text[a["pos"]+1:a["pos"]+60]
    books[vol] = {"text": text, "page_at": page_at, "chapters": chapters, "anchors": anchors}
    print(f"vol{vol}: {len(text)} chars, {len(chapters)} chapter starts "
          f"({chapters[0]['num']}..{chapters[-1]['num']}), {len(anchors)} anchors")
json.dump(books, open("books.json","w"), ensure_ascii=False)

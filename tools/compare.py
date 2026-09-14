# -*- coding: utf-8 -*-
"""Пословная сверка печатного текста с электронным по главам.
Ищем не опечатки, а выпавшие куски: эпиграфы, реплики, абзацы."""
import json, re, difflib, bisect
from norm import norm
import ebooks

WORD = re.compile(r'[0-9A-Za-zА-Яа-яЁё]+(?:-[0-9A-Za-zА-Яа-яЁё]+)*')

def tokens(text):
    out = []
    for m in WORD.finditer(text):
        w = norm(m.group(0))
        if w: out.append((w, m.start(), m.end()))
    return out

B = json.load(open("books.json"))
CH = ebooks.epub_chapters()
# печатный текст по главам
pr = {}
for vol in "123":
    b = B[vol]; ch = b["chapters"]
    for i, c in enumerate(ch):
        end = ch[i+1]["offset"] if i+1 < len(ch) else len(b["text"])
        pr[c["num"]] = (vol, b["text"][c["offset"]:end])

MIN = 6
findings = []
for num in sorted(pr):
    vol, ptext = pr[num]
    etext = CH[num]["plain"]
    P, E = tokens(ptext), tokens(etext)
    sm = difflib.SequenceMatcher(None, [w for w,_,_ in P], [w for w,_,_ in E], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        np_, ne = i2-i1, j2-j1
        if tag == "delete" or (tag == "replace" and np_ >= MIN and ne < np_/2):
            if np_ < MIN: continue
            findings.append({"chapter": num, "vol": int(vol), "kind": "нет в электронке",
                             "nwords": np_, "print": ptext[P[i1][1]:P[i2-1][2]],
                             "ebook_at": etext[max(0,E[j1][1]-70):E[j1][1]] if j1 < len(E) else ""})
        elif tag == "insert" or (tag == "replace" and ne >= MIN and np_ < ne/2):
            if ne < MIN: continue
            findings.append({"chapter": num, "vol": int(vol), "kind": "нет в печати",
                             "nwords": ne, "ebook": etext[E[j1][1]:E[j2-1][2]],
                             "print_at": ptext[max(0,P[i1][1]-70):P[i1][1]] if i1 < len(P) else ""})
json.dump(findings, open("diff_findings.json","w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(f["kind"] for f in findings))
print("суммарно слов:", {k: sum(f["nwords"] for f in findings if f["kind"]==k) for k in {f["kind"] for f in findings}})
print("\nсамые крупные пропажи в электронке:")
for f in sorted([f for f in findings if f["kind"]=="нет в электронке"], key=lambda f:-f["nwords"])[:12]:
    print(f'  гл.{f["chapter"]} ({f["nwords"]} слов): {f["print"][:180]!r}')

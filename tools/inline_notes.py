# -*- coding: utf-8 -*-
"""Переводческие примечания, которые уже есть в электронке прямо в тексте.
Два вида: врезка [ ... ] посреди фразы и пара «маркер [N] в тексте + блок [N] ... в конце главы»."""
import re, json, sys
import ebooks

BRACKET = re.compile(r'\s*\[([^\[\]]{20,600})\]')
MARKER  = re.compile(r'\[(\d+)\]')
ATTRIB  = re.compile(r'Прим\.\s*(перев|ред|авт)', re.I)

def collect(CH):
    notes = []
    for num in sorted(CH):
        ch = CH[num]; p = ch["plain"]
        blocks = [m for m in BRACKET.finditer(p)]
        numbered = {}
        for m in blocks:
            inner = m.group(1).strip()
            mm = re.match(r'^(\d+)\s+(.{15,})$', inner, re.S)
            if mm:                                   # блок «[N] текст» в конце главы
                numbered[mm.group(1)] = (m, mm.group(2).strip())
        for m in blocks:
            inner = m.group(1).strip()
            if re.match(r'^\d+\s', inner): continue
            if not ATTRIB.search(inner): continue
            notes.append({"chapter": num, "kind": "врезка", "text": inner,
                          "cut": [m.start(), m.end()], "anchor": m.start()})
        # блок примечания в конце главы не обёрнут в скобки: «[N] текст» последним абзацем
        ms = list(MARKER.finditer(p))
        if len(ms) >= 2 and ms[0].group(1) == ms[-1].group(1) and not numbered:
            first, last = ms[0], ms[-1]
            end = p.find("\n", last.end())
            end = len(p) if end < 0 else end
            text = p[last.end():end].strip()
            if len(text) >= 20:
                notes.append({"chapter": num, "kind": "концевая", "text": text,
                              "cut": [last.start(), end], "anchor": first.start(),
                              "cut2": [first.start(), first.end()]})
    return notes

if __name__ == "__main__":
    for tgt, CH in (("epub", ebooks.epub_chapters()), ("fb2", ebooks.fb2_chapters()[1])):
        ns = collect(CH)
        json.dump(ns, open(f"inline_{tgt}.json", "w"), ensure_ascii=False, indent=1)
        print(f'{tgt}: {len(ns)} примечаний '
              f'(врезок {sum(1 for n in ns if n["kind"]=="врезка")}, '
              f'концевых {sum(1 for n in ns if n["kind"]=="концевая")})')
        if tgt == "epub":
            for n in ns:
                p = CH[n["chapter"]]["plain"]; a = n["anchor"]
                print(f'  гл.{n["chapter"]:3d} [{n["kind"]}] ...{p[max(0,a-45):a]}⟦N⟧{p[n["cut"][1]:n["cut"][1]+25]}'.replace("\n"," "))
                print(f'        {n["text"][:110]}')

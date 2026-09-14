# -*- coding: utf-8 -*-
import json, re, sys

P = json.load(open("pages.json"))
NOTES_START = {"1": 589, "2": 577, "3": 665}
NOTES_END   = {"1": 610, "2": 586, "3": 677}

FOLIO = re.compile(r'^\s*\d{1,3}\s*$')
ENTRY = re.compile(r'^\s*Стр\.\s*(\d+)\.\s*(.*)$')

def lines_of(vol):
    out = []
    for pno in range(NOTES_START[vol], NOTES_END[vol] + 1):
        for ln in P[vol][pno - 1].split("\n"):
            if FOLIO.match(ln):        # running head / folio
                continue
            out.append(ln.rstrip())
    return out

entries = []
for vol in "123":
    cur = None
    started = False
    for ln in lines_of(vol):
        m = ENTRY.match(ln)
        if m:
            started = True
            if cur: entries.append(cur)
            cur = {"vol": int(vol), "page": int(m.group(1)), "lines": [m.group(2)]}
        elif started and ln.strip():
            if cur: cur["lines"].append(ln.strip())
    if cur: entries.append(cur)

print("entries parsed:", len(entries))
from collections import Counter
print(Counter(e["vol"] for e in entries))
json.dump(entries, open("entries_raw.json","w"), ensure_ascii=False, indent=1)
# sanity: pages monotonic within volume?
for vol in (1,2,3):
    pp = [e["page"] for e in entries if e["vol"]==vol]
    bad = [(a,b) for a,b in zip(pp, pp[1:]) if b < a]
    print(f"vol{vol}: pages {pp[0]}..{pp[-1]}, non-monotonic: {bad}")

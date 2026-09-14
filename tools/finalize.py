# -*- coding: utf-8 -*-
"""Окончательная точка привязки в тексте печатного издания.
Правило: если звёздочка лежит внутри цитаты (или вплотную к её концу) — берём её,
она указывает на конкретное слово. Иначе берём конец цитаты: это точнее,
чем звёздочка, отнесённая вёрсткой в конец предложения."""
import json, bisect
from norm import norm_map
B = json.load(open("books.json")); E = json.load(open("entries.json"))
L = {r["n"]: r for r in json.load(open("located.json"))}
for vol in "123":
    b = B[vol]; b["ntext"], b["nidx"] = norm_map(b["text"])
    for a in b["anchors"]: a["npos"] = bisect.bisect_left(b["nidx"], a["pos"])
    b["apos"] = [a["npos"] for a in b["anchors"]]
    b["chn"] = [(bisect.bisect_left(b["nidx"], c["offset"]), c["num"]) for c in b["chapters"]]

taken = {}
out = []
# первый проход — записи с цитатой; второй — без цитаты (иначе они хватают чужие звёздочки)
for e in sorted(E, key=lambda e: (e["quote"] is None, e["n"])):
    vol = str(e["vol"]); b = B[vol]; r = L[e["n"]]
    rec = {"n": e["n"], "vol": e["vol"], "page": e["page"],
           "quote": e["quote"], "comment": e["comment"]}
    pos = src = None
    if r.get("qstart") is not None:
        lo, hi = r["qstart"] - 10, r["qend"] + 25
        cands = [k for k in range(bisect.bisect_left(b["apos"], lo), bisect.bisect_right(b["apos"], hi))
                 if (e["vol"], k) not in taken]
        if cands:
            k = cands[0]; taken[(e["vol"], k)] = e["n"]
            pos, src = b["apos"][k], "звёздочка"
        else:
            pos, src = r["qend"], "конец цитаты"
    else:                                     # запись без цитаты — только звёздочка
        cands = [k for k, a in enumerate(b["anchors"])
                 if e["page"] <= a["page"] <= e["page"] + 1 and (e["vol"], k) not in taken]
        if len(cands) == 1:
            k = cands[0]; taken[(e["vol"], k)] = e["n"]
            pos, src = b["apos"][k], "звёздочка (без цитаты)"
    rec["src"] = src
    if pos is not None:
        rec["chapter"] = max((n for o, n in b["chn"] if o < pos), default=b["chn"][0][1])
        starts = [o for o, n in b["chn"]]
        k = starts.index(max((o for o, n in b["chn"] if o < pos), default=b["chn"][0][0]))
        lo = starts[k]; hi = starts[k+1] if k+1 < len(starts) else len(b["ntext"])
        rec["rel"] = round((pos - lo) / max(1, hi - lo), 4)
        rec["ctx"] = b["ntext"][max(0, pos - 90):pos]
        o = b["nidx"][pos - 1] + 1 if pos > 0 else 0
        rec["ctx_human"] = b["text"][max(0, o - 70):o] + "⟦*⟧" + b["text"][o:o + 40]
    else:
        rec["chapter"] = None; rec["rel"] = None
    out.append(rec)

out.sort(key=lambda r: r["n"])
json.dump(out, open("anchored.json", "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(Counter(r["src"] for r in out))
print("глав задействовано:", len({r["chapter"] for r in out if r["chapter"]}))
print("\nзаписи, где точка привязки — конец цитаты (звёздочки рядом не нашлось):")
for r in out:
    if r["src"] == "конец цитаты":
        print(f'  #{r["n"]} т.{r["vol"]} стр.{r["page"]} гл.{r["chapter"]}: {r["ctx_human"]}')

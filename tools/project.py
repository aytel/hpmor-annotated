# -*- coding: utf-8 -*-
"""Переносим точку привязки из печатного текста в электронный.
Контекст — 90 нормализованных символов, кончающихся ровно в точке привязки;
ищем его в нужной главе, точка привязки = конец найденного вхождения."""
import json, sys, bisect
from rapidfuzz import fuzz
import ebooks, place

TARGET = sys.argv[1] if len(sys.argv) > 1 else "epub"

def refine(nt, ctx, e0):
    """Уточняем правый край: скользим концом по окрестности и берём максимум сходства."""
    tail = ctx[-45:]
    best, bp = -1, e0
    for e in range(max(len(tail), e0 - 45), min(len(nt), e0 + 45) + 1):
        s = fuzz.ratio(tail, nt[e - len(tail):e])
        if s > best: best, bp = s, e
    return bp, best

def locate(ch, ctx, rel_hint):
    nt = ch["ntext"]
    for L in (90, 70, 50, 35, 25, 18):
        c = ctx[-L:]
        if len(c) < 12: break
        hits, i = [], nt.find(c)
        while i >= 0:
            hits.append(i + len(c)); i = nt.find(c, i + 1)
        if len(hits) == 1: return hits[0], f"точно ({L})", 100.0
        if len(hits) > 1:
            # несколько одинаковых мест — выбираем ближайшее по относительной позиции в главе
            pick = min(hits, key=lambda h: abs(h / len(nt) - rel_hint))
            return pick, f"точно ({L}, выбор из {len(hits)})", 100.0
    r = fuzz.partial_ratio_alignment(ctx, nt, score_cutoff=75)
    if not r: return None, "не найдено", 0.0
    e, s = refine(nt, ctx, r.dest_end)
    return e, f"нечётко ({s:.0f}%)", s

def run(target):
    A = json.load(open("anchored.json"))
    if target == "epub":
        CH = ebooks.epub_chapters(); raw = None
    else:
        raw, CH = ebooks.fb2_chapters()
    out = []
    for r in A:
        ch = CH.get(r["chapter"])
        if ch is None:
            pos, how, sc = None, "нет главы", 0.0
        else:
            pos, how, sc = locate(ch, r["ctx"], r.get("rel") or 0.5)
        rec = {**{k: r[k] for k in ("n","vol","page","chapter","src","quote","comment","ctx","ctx_human")},
               "npos": pos, "how": how, "score": round(sc, 1), "ins": None, "view": None}
        if ch is not None and pos is not None:
            i = place.insert_at(ch, pos)
            if how.startswith("нечётко"):
                i = place.nudge_to_last_word(ch["plain"], i, r["ctx_human"])
            p = ch["plain"]
            rec["ins"] = i
            rec["view"] = f'...{p[max(0,i-58):i]}⟦N⟧{p[i:i+28]}'.replace("\n", " ")
        out.append(rec)
    json.dump(out, open(f"projected_{target}.json","w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(target, Counter(o["how"].split(" (")[0] for o in out))
    for o in out:
        if o["npos"] is None or not o["how"].startswith("точно ("):
            print(f'  #{o["n"]} гл.{o["chapter"]} [{o["how"]}] «{(o["quote"] or "—")[:55]}»')
        elif "выбор" in o["how"]:
            print(f'  #{o["n"]} гл.{o["chapter"]} [{o["how"]}] «{(o["quote"] or "—")[:55]}»')
    return out, CH

if __name__ == "__main__":
    run(TARGET)

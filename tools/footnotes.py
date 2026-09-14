# -*- coding: utf-8 -*-
"""Собираем подстрочные сноски печатного издания и их маркеры в тексте."""
import json, re
P3 = json.load(open("pages3.json"))
NOTES_START = {"1": 589, "2": 577, "3": 665}
FRONT = 12          # титул, выходные данные, предисловие — не трогаем

pages_clean, foots = {}, []
for vol in "123":
    pc = []
    for pno, pg in enumerate(P3[vol], 1):
        bottom = pg["h"] * 0.72
        cand = [l for l in pg["lines"]
                if (7.9 <= l["sz"] <= 8.9 or 4.5 <= l["sz"] <= 5.6) and l["y"] > bottom]
        # из текста выносим только нумерованный подстрочник; авторские примечания
        # набраны тем же кеглем, но это часть книги — в них даже сидят якори комментариев
        isfoot = any("\x02" in l["t"] for l in cand)
        foot = cand if isfoot else []
        body = [l["t"] for l in pg["lines"] if l not in foot]
        foot = [l["t"] for l in foot]
        pc.append("\n".join(body).replace("\x01", "").replace("\x02", ""))
        blk = "\n".join(foot)
        if blk.strip() and FRONT < pno < NOTES_START[vol]:
            foots.append({"vol": int(vol), "page": pno, "raw": blk,
                          "numbered": "\x02" in blk,
                          "markers": sum(l["t"].count("\x01") for l in pg["lines"])})
    pages_clean[vol] = pc
json.dump(pages_clean, open("pages_clean.json", "w"), ensure_ascii=False)
json.dump(foots, open("footnotes_raw.json", "w"), ensure_ascii=False, indent=1)
print(f"блоков подстрочника в основном корпусе: {len(foots)} "
      f"(с номером: {sum(1 for f in foots if f['numbered'])})")
for f in foots:
    t = re.sub(r'\s+', ' ', f["raw"].replace("\x02", "№")).strip()
    print(f'  т.{f["vol"]} стр.{f["page"]:3d} маркеров={f["markers"]}: {t[:120]}')

# -*- coding: utf-8 -*-
"""Текст страниц с выделенными надстрочными маркерами.
\x01 — маркер подстрочной сноски в основном тексте (надстрочная цифра, кегль 6.6)
\x02 — номер в самой сноске (кегль 4.9)
Звёздочки комментариев остаются как есть."""
import pymupdf, json, os
from paths import SRC
out = {}
for vol, name in enumerate(["Книга 1.pdf", "Книга 2.pdf", "Книга 3.pdf"], 1):
    doc = pymupdf.open(os.path.join(SRC, name))
    pages = []
    for p in doc:
        lines = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                buf = ""
                for s in l["spans"]:
                    t, sz = s["text"], s["size"]
                    if t.strip().isdigit() and sz < 7.6:
                        buf += "\x02" if sz < 5.7 else "\x01"
                    else:
                        buf += t
                lines.append({"t": buf, "y": round(l["bbox"][1], 1),
                              "sz": round(max([s["size"] for s in l["spans"] if s["text"].strip()] or [0]), 1)})
        pages.append({"lines": lines, "h": round(p.rect.height, 1)})
    out[vol] = pages
    print(f"vol{vol}: {len(pages)} страниц, маркеров \\x01: "
          f"{sum(l['t'].count(chr(1)) for pg in pages for l in pg['lines'])}, "
          f"номеров \\x02: {sum(l['t'].count(chr(2)) for pg in pages for l in pg['lines'])}")
    doc.close()
json.dump(out, open("pages3.json", "w"), ensure_ascii=False)

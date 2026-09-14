# -*- coding: utf-8 -*-
"""Финальная сверка: чего из печати действительно нет в электронке.
Атрибуцию («— Прим. перев.», «От автора:») отбрасываем — она оформлена по-разному."""
import json, glob, html, re
from norm import norm
ATTR = re.compile(r'\s*[—–-]?\s*Прим\.\s*(перев|ред|авт)\w*\.?\s*$', re.I)
LEAD = re.compile(r'^\s*(От автора:|Примечани[ея] автора:)\s*', re.I)

whole = "".join(html.unescape(re.sub(r'<[^>]+>', ' ', open(f, encoding="utf-8").read()))
                for f in sorted(glob.glob("ep/index-*.html")))
W = norm(whole)

def present(text):
    t = LEAD.sub('', ATTR.sub('', re.sub(r'\s+', ' ', text).strip()))
    k = norm(t)
    if len(k) < 20: return None                       # слишком коротко для приговора
    return k[:min(90, len(k))] in W

res = {"fragments": [], "footnotes": []}
for f in json.load(open("diff_findings.json")):
    if f["kind"] != "нет в электронке": continue
    if present(f["print"]) is False:
        res["fragments"].append(f)
for f in json.load(open("footnotes_raw.json")):
    t = re.sub(r'\s+', ' ', f["raw"].replace("\x02", " ")).strip()
    t = re.sub(r'^\s*\d+\s*', '', t)
    if present(t) is False:
        res["footnotes"].append({**f, "text": t})
json.dump(res, open("missing_final.json", "w"), ensure_ascii=False, indent=1)
print(f'фрагментов основного текста нет в электронке: {len(res["fragments"])}')
for f in res["fragments"]: print(f'   гл.{f["chapter"]:3d} ({f["nwords"]:3d} сл.) {f["print"][:130]!r}')
print(f'\nподстрочных сносок печати нет в электронке: {len(res["footnotes"])}')
for f in res["footnotes"]: print(f'   т.{f["vol"]} стр.{f["page"]}: {f["text"][:130]!r}')

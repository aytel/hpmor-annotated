# -*- coding: utf-8 -*-
"""Находим саму цитату в теле тома (а не звёздочку) и смотрим, где рядом звёздочка."""
import json, re, bisect
from norm import norm, norm_map
from rapidfuzz import fuzz
B=json.load(open("books.json")); E=json.load(open("entries.json"))
ELL=re.compile(r'\(\s*\.\.\.\s*\)|\.{3}|…')
for vol in "123":
    b=B[vol]; b["ntext"],b["nidx"]=norm_map(b["text"])
    for a in b["anchors"]: a["npos"]=bisect.bisect_left(b["nidx"],a["pos"])
    b["apos"]=[a["npos"] for a in b["anchors"]]
    b["pn"]={p:bisect.bisect_left(b["nidx"],o) for o,p in b["page_at"]}

def window(b,page):
    lo=b["pn"].get(max(1,page-3),0); hi=b["pn"].get(page+8,len(b["ntext"]))
    return lo,hi

res=[]
for e in E:
    vol=str(e["vol"]); b=B[vol]; lo,hi=window(b,e["page"])
    q=e["quote"] or ""
    fr=[norm(x) for x in ELL.split(q) if len(norm(x))>=6] or ([norm(q)] if norm(q) else [])
    rec={"n":e["n"],"vol":e["vol"],"page":e["page"]}
    if not fr:
        rec.update(qstart=None,qend=None,found=None); res.append(rec); continue
    # первый фрагмент
    s=b["ntext"].find(fr[0],lo,hi); sc=100.0
    if s<0:
        r=fuzz.partial_ratio_alignment(fr[0],b["ntext"][lo:hi],score_cutoff=75)
        s,sc=(lo+r.dest_start,r.score) if r else (-1,0)
    if s<0: rec.update(qstart=None,qend=None,found=0); res.append(rec); continue
    # последний фрагмент — ищем от начала первого
    last=fr[-1]; e2=b["ntext"].find(last,s,min(hi,s+len(norm(q))+400))
    if e2<0:
        r=fuzz.partial_ratio_alignment(last,b["ntext"][s:min(hi,s+len(norm(q))+400)],score_cutoff=75)
        e2=s+r.dest_start if r else s
        sc=min(sc,r.score if r else 0)
    qend=e2+len(last)
    j=bisect.bisect_left(b["apos"],s)
    near=[(b["apos"][k]-qend,k) for k in range(max(0,j-1),min(len(b["apos"]),j+3))]
    best=min(near,key=lambda t:abs(t[0])) if near else (None,None)
    rec.update(qstart=s,qend=qend,found=round(sc,1),gap=best[0],anchor=best[1])
    res.append(rec)
json.dump(res,open("located.json","w"),ensure_ascii=False,indent=1)
ok=[r for r in res if r.get("found")==100]
print(f"цитата найдена точно: {len(ok)}/323; неточно: {sum(1 for r in res if r.get('found') not in (100,None))}; нет цитаты: {sum(1 for r in res if r.get('found') is None)}")
gaps=[r["gap"] for r in res if r.get("gap") is not None]
import collections
print("распределение gap (позиция звёздочки минус конец цитаты):")
for lo,hi in [(-10**9,-40),(-40,-5),(-5,0),(0,1),(1,5),(5,40),(40,200),(200,10**9)]:
    print(f"   [{lo},{hi}): {sum(1 for g in gaps if lo<=g<hi)}")

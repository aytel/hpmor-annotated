import pymupdf, json, os, re
from paths import SRC
out = {}
for vol, name in enumerate(["Книга 1.pdf", "Книга 2.pdf", "Книга 3.pdf"], 1):
    doc = pymupdf.open(os.path.join(SRC, name))
    pages = [p.get_text("text") for p in doc]
    out[vol] = pages
    # check folio alignment: find running head number on a few pages
    ok = 0
    for i in range(50, 300):
        nums = re.findall(r'^\s*(\d{1,3})\s*$', pages[i], re.M)
        if str(i+1) in nums: ok += 1
    print(f"vol{vol}: {len(pages)} pages, folio==index on {ok}/250 sampled")
    doc.close()
json.dump(out, open("pages.json","w"), ensure_ascii=False)

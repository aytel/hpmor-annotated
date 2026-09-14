# -*- coding: utf-8 -*-
"""Распаковывает исходный epub в ./ep и достаёт из fb2 «общую» обложку."""
import base64, os, re, shutil, zipfile
from paths import EPUB_IN, FB2_IN

if os.path.exists("ep"): shutil.rmtree("ep")
os.makedirs("ep")
with zipfile.ZipFile(EPUB_IN) as z: z.extractall("ep")
print(f"распакован {EPUB_IN}: {len(os.listdir('ep'))} объектов")

raw = open(FB2_IN, encoding="utf-8").read()
m = re.search(r'<binary id="([^"]+)" content-type="image/[^"]+">(.*?)</binary>', raw, re.S)
open("fb2__0.jpg", "wb").write(base64.b64decode(m.group(2)))
print(f"обложка из fb2 ({m.group(1)}): {os.path.getsize('fb2__0.jpg')} байт")

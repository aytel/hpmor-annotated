# -*- coding: utf-8 -*-
"""Проверка собранного fb2 по официальной схеме FictionBook 2.0.
Исходник с гпмрм.рф схеме не соответствует (аннотация не на своём месте и без
абзаца), поэтому сборка эти два места заодно чинит — результат должен быть чистым."""
import os, re, sys
from lxml import etree
from paths import FB2_OUT

HERE = os.path.dirname(os.path.abspath(__file__))
xsd = etree.XMLSchema(etree.parse(os.path.join(HERE, "schema", "FictionBook.xsd")))
ok = xsd.validate(etree.parse(FB2_OUT))
print("FB2 по схеме FictionBook 2.0:", "✔ валиден" if ok else "✘ невалиден")
for e in xsd.error_log:
    print(f"   строка {e.line}: {re.sub(r'\{[^}]*\}', '', e.message)[:160]}")
sys.exit(0 if ok else 1)

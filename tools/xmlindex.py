# -*- coding: utf-8 -*-
"""Плоский текст XML/HTML-файла вместе с картой «символ текста -> смещение в файле».
Нужен, чтобы вставлять разметку по позиции, найденной в тексте, и гарантированно
не попасть внутрь тега или сущности."""
import re, html
TAG = re.compile(r'<[^>]*>')
ENT = re.compile(r'&(#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);')

def build(raw, start=0):
    """-> (plain, offs, ends): offs[i]/ends[i] — границы i-го символа в исходном файле."""
    plain, offs, ends, i = [], [], [], start
    for m in TAG.finditer(raw, start):
        seg_start, seg_end = i, m.start()
        j = seg_start
        while j < seg_end:
            e = ENT.match(raw, j)
            if e and e.end() <= seg_end:
                plain.append(html.unescape(e.group(0))); offs.append(j); ends.append(e.end()); j = e.end()
            else:
                plain.append(raw[j]); offs.append(j); ends.append(j + 1); j += 1
        i = m.end()
    return ''.join(plain), offs, ends

# -*- coding: utf-8 -*-
import re, unicodedata
KEEP = re.compile(r'[0-9a-zа-я]')

def _fold(s):
    # NFKD + выброс диакритики: ѝ -> и, ё -> е, й -> и. Применяется к обеим сторонам,
    # поэтому различающая способность почти не страдает, зато уходят «эмѝ» vs «эми».
    s = unicodedata.normalize('NFKD', s.lower())
    return ''.join(ch for ch in s if not unicodedata.combining(ch))

def norm(s):
    """Только буквы/цифры в нижнем регистре: убивает кавычки, тире, переносы,
    пробелы и многоточия — всё, чем печатное издание отличается от электронного."""
    return ''.join(ch for ch in _fold(s) if KEEP.match(ch))

def norm_map(s):
    """То же, плюс карта: индекс в нормализованной строке -> индекс в исходной."""
    out, idx = [], []
    for i, ch in enumerate(s):
        for c in _fold(ch):
            if KEEP.match(c):
                out.append(c); idx.append(i)
    return ''.join(out), idx

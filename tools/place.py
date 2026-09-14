# -*- coding: utf-8 -*-
"""Доводим точку вставки до типографски правильного места:
не внутрь слова (в том числе дефисного), после закрывающей кавычки,
восклицательного/вопросительного знака и многоточия — но перед точкой,
запятой и скобкой, как принято в вёрстке сносок."""
import re
LETTER = re.compile(r'[0-9A-Za-zА-Яа-яЁё]')
CLOSERS = '»”"\'’!?…'

def snap(plain, i):
    n = len(plain)
    if 0 < i < n and LETTER.match(plain[i]) and LETTER.match(plain[i-1]):
        while i < n and LETTER.match(plain[i]): i += 1
    # дефисное слово — единое целое: куда-нибудь, Мальчик-Который-Выжил
    while (i + 1 < n and plain[i] == '-' and LETTER.match(plain[i+1])
           and i > 0 and LETTER.match(plain[i-1])):
        i += 1
        while i < n and LETTER.match(plain[i]): i += 1
    while i < n and plain[i] in CLOSERS: i += 1
    if plain[i:i+2] == '..':                      # многоточие тремя точками
        while i < n and plain[i] == '.': i += 1
    return i

def nudge_to_last_word(plain, i, print_ctx_human):
    """Для нечётких совпадений: если последнее слово печатного контекста стоит
    в электронном тексте чуть дальше — дотягиваем маркер до него."""
    left = print_ctx_human.split("\u27e6*\u27e7")[0]
    m = re.search(r'[0-9A-Za-zА-Яа-яЁё]+$', left)
    if not m: return i
    w = m.group(0)
    j = plain.find(w, i, i + 25)
    return snap(plain, j + len(w)) if j >= 0 else i


def insert_at(ch, npos):
    """npos — индекс в нормализованном тексте главы; возвращаем индекс в plain."""
    if npos is None or npos == 0: return None
    return snap(ch["plain"], ch["nidx"][npos-1] + 1)

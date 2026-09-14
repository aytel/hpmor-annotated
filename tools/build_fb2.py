# -*- coding: utf-8 -*-
"""Собирает fb2 со сносками: маркеры type="note" и отдельное тело <body name="notes">,
которое читалки показывают всплывающим окном."""
from paths import FB2_OUT
import re, html, json, os
import ebooks, corpus
from build_epub import ops_apply, whole_element, TAGS, render

DEST = FB2_OUT
MARK = '<a xlink:href="#n{n}" type="note">[{n}]</a>'

def main():
    raw, CH = ebooks.fb2_chapters()
    notes, cuts = corpus.gather("fb2", CH)
    ops = []
    marker_at = {}
    for n in notes:
        if n["pos"] >= 0: marker_at.setdefault(n["chapter"], {})[n["pos"]] = n["num"]
    for ch, a, b, kind in cuts:
        c = CH[ch]; offs, ends = c["offs"], c["ends"]
        rep = MARK.format(n=marker_at[ch].pop(a)) if kind == "MARKER" else ""
        rs, re_ = offs[a], ends[b-1]
        el = whole_element(raw, rs, re_)
        if el:
            rs, re_ = el
            if rep and a > 0:
                ops.append((ends[a-1], ends[a-1], rep)); rep = ""
        else:
            rep += "".join(TAGS.findall(raw[rs:re_]))
        ops.append((rs, re_, rep))
    for ch, m in marker_at.items():
        offs, ends = CH[ch]["offs"], CH[ch]["ends"]
        for pos, num in m.items():
            at = ends[pos-1] if pos > 0 else offs[pos]
            ops.append((at, at, MARK.format(n=num)))
    # восстановления текста
    n108 = next(x for x in notes if x["chapter"] == 23 and x["pos"] == -1)
    i = raw.index("</title>", CH[23]["offs"][0] - 300) + len("</title>")
    ops.append((i, i, '<p>' + html.escape(corpus.EPIGRAPH_23) + MARK.format(n=n108["num"]) + '</p>\n'))
    c7 = CH[7]; p7 = c7["plain"]
    k = p7.index("Мне нужно подумать над этим.") + len("Мне нужно подумать над этим.")
    ops.append((c7["ends"][k-1], c7["ends"][k-1], html.escape(corpus.CH7_ADD)))
    j = p7.index(corpus.CH7_OLD)
    ops.append((c7["offs"][j], c7["ends"][j + len(corpus.CH7_OLD) - 1], html.escape(corpus.CH7_NEW)))

    raw = ops_apply(raw, ops)
    raw = re.sub(r'(type="note">\[\d+\]</a>)\s*</p>\s*<p>\s*(?=[.,;:!?])', r'\1', raw)

    nb = ['<body name="notes">']
    for n in notes:
        nb.append(f'<section id="n{n["num"]}"><title><p>{n["num"]}</p></title>'
                  f'<p>{render(n["text"], "fb2")}</p></section>')
    nb.append('</body>')
    raw = re.sub(r'<book-title>.*?</book-title>',
                 '<book-title>Гарри Поттер и методы рационального мышления '
                 '(с комментариями)</book-title>', raw, count=1)
    raw = raw.replace('</FictionBook>', "\n".join(nb) + '\n</FictionBook>')
    open(DEST, "w", encoding="utf-8").write(raw)
    print(f'{DEST}  {os.path.getsize(DEST)/1e6:.2f} МБ, сносок {len(notes)}')

if __name__ == "__main__":
    main()

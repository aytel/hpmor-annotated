# -*- coding: utf-8 -*-
"""Собирает epub со сносками: разметка EPUB 3 (noteref/aside) плюс отдельная
страница примечаний как запасной вариант для старых читалок."""
import os, re, shutil, json, html, datetime, subprocess
import ebooks, corpus

SRC, OUT = "ep", "out_epub"
MARK = ('<a epub:type="noteref" href="notes.xhtml#n{n}" id="r{n}" '
        'class="noteref"><sup>{n}</sup></a>')

TAGS = re.compile(r'<[^>]*>')
SEP_P = re.compile(r'<p\b[^>]*>[\s_\u2014\u2013-]*</p>\s*$')

def whole_element(raw, s, e):
    """Если вырезаемое занимает весь абзац (пусть и обёрнутое в <em>), расширяем
    вырезку до <p>…</p> — иначе останется пустой абзац. Заодно убираем абзац-разделитель
    из подчёркиваний, если он стоял перед сноской."""
    ts = s                       # перематываем пробелы и открывающие теги до самого текста
    while ts < e:
        if raw[ts] in " \n\t\r": ts += 1
        elif raw[ts] == "<": ts = raw.index(">", ts) + 1
        else: break
    a = raw.rfind("<p", 0, ts)
    z = raw.find("</p>", e)
    if a < 0 or z < 0: return None
    head = raw.index(">", a) + 1
    if TAGS.sub("", raw[head:ts]).strip() or TAGS.sub("", raw[e:z]).strip():
        return None
    z += len("</p>")
    while z < len(raw) and raw[z] in " \n\t": z += 1
    m = SEP_P.search(raw[:a])
    if m: a = m.start()
    return a, z


def render(text, fmt):
    """Экранируем текст и разворачиваем перекрёстные ссылки {{ref:N}}."""
    t = html.escape(text)
    if fmt == "epub":
        return re.sub(r'\{\{ref:(\d+)\}\}', r'<a href="#n\1">\1</a>', t)
    return re.sub(r'\{\{ref:(\d+)\}\}', r'<a xlink:href="#n\1" type="note">\1</a>', t)


def ops_apply(raw, ops):
    """ops: (start, end, replacement) в координатах файла. Проверяем пересечения."""
    ops = sorted(ops, key=lambda o: (o[0], o[1]))
    for a, b in zip(ops, ops[1:]):
        if a[1] > b[0]:
            raise SystemExit(f"пересекающиеся правки: {a[:2]} и {b[:2]}")
    for s, e, t in reversed(ops):
        raw = raw[:s] + t + raw[e:]
    return raw

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    CH = ebooks.epub_chapters()
    notes, cuts = corpus.gather("epub", CH)
    by_ch = {}
    for n in notes: by_ch.setdefault(n["chapter"], []).append(n)
    cut_by_ch = {}
    for ch, a, b, kind in cuts: cut_by_ch.setdefault(ch, []).append((a, b, kind))

    fname = {ch: os.path.basename(CH[ch]["path"]) for ch in CH}
    for ch in sorted(CH):
        c = CH[ch]; raw, offs, ends, plain = c["raw"], c["offs"], c["ends"], c["plain"]
        ops = []
        marker_at = {}                       # позиция в plain -> номер сноски
        for n in by_ch.get(ch, []):
            if n["pos"] >= 0: marker_at[n["pos"]] = n["num"]
        cut_positions = {a for a, b, k in cut_by_ch.get(ch, [])}
        for a, b, kind in cut_by_ch.get(ch, []):
            rep = MARK.format(n=marker_at.pop(a)) if kind == "MARKER" else ""
            rs, re_ = offs[a], ends[b-1]
            el = whole_element(raw, rs, re_)
            if el:                       # примечание занимало отдельный абзац
                rs, re_ = el
                if rep and a > 0:        # маркер — к концу предыдущего абзаца
                    ops.append((ends[a-1], ends[a-1], rep)); rep = ""
            else:
                # вырезаем только текст: теги внутри диапазона оставляем на месте,
                # иначе можно снести открывающий <em> и осиротить его закрывающий
                rep += "".join(TAGS.findall(raw[rs:re_]))
            ops.append((rs, re_, rep))
        for pos, num in marker_at.items():
            # ставим маркер сразу за последним символом текста, а не перед следующим:
            # иначе между ними может оказаться <br/> или закрывающий тег, и маркер
            # уедет на другую строку
            at = ends[pos-1] if pos > 0 else offs[pos]
            ops.append((at, at, MARK.format(n=num)))
        # восстановления текста
        if ch == 23:
            n108 = next(x for x in by_ch[23] if x["pos"] == -1)
            i = raw.index("</h2>") + len("</h2>")
            ops.append((i, i, '\n<p class="calibre2">' + html.escape(corpus.EPIGRAPH_23)
                        + MARK.format(n=n108["num"]) + '</p>'))
        if ch == 7:
            i = plain.index("Мне нужно подумать над этим.") + len("Мне нужно подумать над этим.")
            ops.append((offs[i], offs[i], html.escape(corpus.CH7_ADD)))
            j = plain.index(corpus.CH7_OLD)
            ops.append((offs[j], ends[j + len(corpus.CH7_OLD) - 1], html.escape(corpus.CH7_NEW)))
        raw = ops_apply(raw, ops)
        # врезка иногда разрывала абзац, и следующий начинался со знака препинания —
        # после переноса примечания в сноску абзацы можно снова склеить
        raw = re.sub(r'(class="noteref"><sup>\d+</sup></a>)\s*</p>\s*<p[^>]*>\s*(?=[.,;:!?])',
                     r'\1', raw)
        raw = raw.replace('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n  '
                          '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">', '<!DOCTYPE html>')
        raw = raw.replace('<html xmlns="http://www.w3.org/1999/xhtml">',
                          '<html xmlns="http://www.w3.org/1999/xhtml" '
                          'xmlns:epub="http://www.idpf.org/2007/ops">')
        open(os.path.join(OUT, fname[ch]), "w", encoding="utf-8").write(raw)

    # страница примечаний
    body = []
    for n in notes:
        body.append(f'<aside epub:type="footnote" id="n{n["num"]}" class="fn">'
                    f'<p class="fnp"><a class="fnback" href="{fname[n["chapter"]]}#r{n["num"]}">'
                    f'{n["num"]}</a> {render(n["text"], "epub")}</p></aside>')
    open(os.path.join(OUT, "notes.xhtml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
        '<head><title>Комментарии и примечания</title><meta charset="utf-8"/>'
        '<link href="stylesheet.css" rel="stylesheet" type="text/css"/></head>\n'
        '<body class="calibre"><h2 class="calibre5">Комментарии и примечания</h2>\n'
        + "\n".join(body) + '\n</body>\n</html>\n')

    with open(os.path.join(OUT, "stylesheet.css"), "a", encoding="utf-8") as f:
        f.write("\n.noteref{text-decoration:none}\n"
                ".noteref sup{font-size:.72em;line-height:0;vertical-align:super}\n"
                "aside.fn{margin:0 0 .7em 0}\n.fnp{text-indent:0;margin:0}\n"
                ".fnback{text-decoration:none;font-weight:bold}\n")
    json.dump(notes, open("notes_final.json", "w"), ensure_ascii=False, indent=1)
    print(f"главы обработаны, сносок: {len(notes)}")

if __name__ == "__main__":
    main()

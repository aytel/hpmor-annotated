# -*- coding: utf-8 -*-
import json, re
HYPH = set(json.load(open("hyphenated.json")))
WORD = r'[А-Яа-яЁёA-Za-z]'

def join_lines(lines):
    lines = [l.replace('­', '') for l in lines]
    out = lines[0]
    for nxt in lines[1:]:
        if not nxt: continue
        if out.endswith('-') and re.match(WORD, nxt):
            tail = re.search(r'([А-Яа-яЁёA-Za-z]+)-$', out)
            head = re.match(r'([А-Яа-яЁёA-Za-z]+)', nxt)
            keep = False
            if tail and head:
                cand = (tail.group(1) + '-' + head.group(1)).lower().replace('ё','е')
                keep = cand in HYPH
            out = out + nxt if keep or nxt[:1].isupper() else out[:-1] + nxt
        elif out.endswith(('–', '—')) and nxt[:1].isdigit():
            out = out + nxt
        else:
            out = out + ' ' + nxt
    return re.sub(r'\s+', ' ', out).strip()

entries = json.load(open("entries_raw.json"))
for e in entries:
    e["text"] = join_lines(e["lines"])
    del e["lines"]
json.dump(entries, open("entries_joined.json","w"), ensure_ascii=False, indent=1)
for e in entries[:3] + entries[165:168]:
    print(f'--- v{e["vol"]} p{e["page"]}\n{e["text"][:400]}\n')

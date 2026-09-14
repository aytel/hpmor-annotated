# -*- coding: utf-8 -*-
import json, re
E = json.load(open("entries_joined.json"))
# quote = leading «...» (non-greedy, nested quotes are „ ”); then optional punct, then dash
RX = re.compile(r'^«(.+?)»\s*([.,!?…]*)\s*[—–-]\s*(.*)$', re.S)
bad = []
for i, e in enumerate(E):
    m = RX.match(e["text"])
    if m:
        e["quote"] = m.group(1).strip()
        e["tail_punct"] = m.group(2)
        e["comment"] = m.group(3).strip()
    else:
        e["quote"] = None; e["comment"] = e["text"]; bad.append(e)
    e["n"] = i + 1
print("не удалось разделить цитату/комментарий:", len(bad))
for e in bad: print(f'  #{e["n"]} v{e["vol"]} p{e["page"]}: {e["text"][:150]}')
nested = [e for e in E if e["quote"] and '«' in e["quote"]]
print("\nцитат с вложенными «»:", len(nested))
for e in nested[:8]: print(f'  #{e["n"]} v{e["vol"]} p{e["page"]}: {e["quote"][:130]}')
json.dump(E, open("entries.json","w"), ensure_ascii=False, indent=1)

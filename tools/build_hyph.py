from paths import FB2_IN
import re, html, json
txt = open(FB2_IN, encoding="utf-8").read()
txt = re.sub(r'<binary.*?</binary>', ' ', txt, flags=re.S)
txt = html.unescape(re.sub(r'<[^>]+>', ' ', txt))
words = set(w.lower().replace('ё','е') for w in re.findall(r'[А-Яа-яЁёA-Za-z]+-[А-Яа-яЁёA-Za-z-]+', txt))
json.dump(sorted(words), open("hyphenated.json","w"), ensure_ascii=False)
print(len(words), "hyphenated word forms")
print(list(sorted(words))[:15])

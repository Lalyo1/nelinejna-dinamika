#!/usr/bin/env python3
"""Прави инвентар на учебника: раздели, примери, теореми и определения.
Употреба: python3 -I scripts/make_inventory.py книга.pdf
Пише inventory/book-sections.md и inventory/NN.md за всяка тема.
PDF страница = печатна + 15."""
import re, subprocess, sys, os
def OFFSET(p): return 15 if p <= 289 else 19
# тема -> печатни диапазони (както в konspekt.md)
T = {1:[(1,14)],2:[(15,24)],3:[(24,32)],4:[(45,54)],5:[(56,62),(70,74)],6:[(74,80)],
 7:[(95,105)],8:[(125,139)],9:[(146,156)],10:[(160,174)],11:[(198,212)],12:[(217,230)],
 13:[(251,257)],14:[(319,325)],15:[(327,329),(373,376)],16:[(355,360)],17:[(405,416)],18:[(416,423)]}
S = {1:['1.0','1.1','1.2','1.3'],2:['2.0','2.1','2.2','2.3'],3:['2.4','2.5','2.6','2.7'],
 4:['3.0','3.1','3.2'],5:['3.4','3.6'],6:['3.7'],7:['4.0','4.1','4.2','4.3','4.4'],
 8:['5.0','5.1','5.2'],9:['6.0','6.1','6.2','6.3'],10:['6.5','6.6','6.7'],
 11:['7.0','7.1','7.2','7.3'],12:['7.6'],13:['8.2'],14:['9.2'],15:['9.3','10.5'],
 16:['10.0','10.1'],17:['11.0','11.1','11.2','11.3'],18:['11.4','11.5']}
def sec_topics(k): return [t for t,v in S.items() if k in v]
pdf = sys.argv[1]
n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
def page(p):
    return subprocess.run(['pdftotext','-f',str(p),'-l',str(p),'-layout',pdf,'-'],capture_output=True,text=True).stdout
H = re.compile(r'^\s{0,8}(\d{1,2}\.\d{1,2})\s{1,8}([A-Z][^\n]{3,90}?)\s*$')
EX = re.compile(r'EXAMPLE\s+(\d+\.\d+\.\d+)')
TH = re.compile(r'((?:Theorem|Lemma|Corollary)\s+\d+\.\d+\.\d+|[A-Z][\w–—\- ]{3,50}\sTheorem:|Existence and Uniqueness Theorem)')
DF = re.compile(r'\b(Definition|DEFINITION)\b')
secs, items = {}, []
for p in range(16, n+1):
    pr = p-OFFSET(p)
    for line in page(p).splitlines():
        m = H.match(line)
        if m and not line.strip().isupper() and not re.search(r'\d\s*$', line) and '. ' not in m.group(2) and not m.group(2).endswith('.'):
            secs.setdefault(m.group(1), (m.group(2).strip(), pr))
        for rx,kind in ((EX,'Пример'),(TH,'Теорема'),(DF,'Определение')):
            m = rx.search(line)
            if m and not (kind=='Теорема' and line.strip().isupper()):
                items.append((pr,kind,(m.group(1) if kind!='Определение' else line.strip()[:70]).strip()))
def topic_of(pr):
    return [t for t,rs in T.items() if any(a<=pr<=b for a,b in rs)]
os.makedirs('inventory',exist_ok=True)
keys = sorted(secs, key=lambda k:[int(x) for x in k.split('.')])
with open('inventory/book-sections.md','w') as f:
    f.write('# Всички раздели на книгата и къде са в конспекта\n\nПечатни страници. Статус: вътре = страницата на раздела е в диапазон на тема; извън = НЕ е в конспекта.\n\n| Раздел | Заглавие | Стр. | Теми от конспекта |\n|---|---|---|---|\n')
    for k in keys:
        t,pr = secs[k]; tt = sec_topics(k)
        f.write(f'| {k} | {t} | {pr} | {", ".join(map(str,tt)) if tt else "**извън**"} |\n')
for t,rs in T.items():
    lo = [(a,b) for a,b in rs]
    with open(f'inventory/{t:02d}.md','w') as f:
        f.write(f'# Тема {t}: инвентар на откъса (печатни стр. {", ".join(f"{a}-{b}" for a,b in rs)})\n\n## Раздели, които започват в откъса\n')
        for k in keys:
            if t in sec_topics(k): f.write(f'- {k} {secs[k][0]} (стр. {secs[k][1]})\n')
        f.write('\n## Примери, теореми, определения (стр. -> вид -> име)\n')
        seen=set()
        for pr,kind,name in items:
            if t in topic_of(pr) and (kind,name) not in seen:
                seen.add((kind,name)); f.write(f'- [ ] стр. {pr}: {kind} {name}\n')
        f.write('\n## Съседни раздели извън откъса (кандидати за изпуснати предпоставки)\n')
        for k in keys:
            pr = secs[k][1]
            if not sec_topics(k) and any(a-12<=pr<=b+12 for a,b in lo): f.write(f'- {k} {secs[k][0]} (стр. {pr})\n')
print('готово', len(keys), 'раздела,', len(items), 'елемента')

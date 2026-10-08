#!/usr/bin/env python3
"""Реже учебника по теми. Употреба: python3 -I scripts/slice_book.py книга.pdf
Правило за страниците: PDF = печатна + 15 до печатна стр. 274,
а след нея PDF = печатна + 19 (в PDF има 4 страници-фигури без текст на PDF стр. 290-293)."""
import subprocess, sys, os, glob
from pypdf import PdfReader, PdfWriter
def pdfpage(pr): return pr + 15 if pr <= 274 else pr + 19
def printed(p): return p - 15 if p <= 289 else p - 19
T = {1:[(1,14)],2:[(15,24)],3:[(24,32)],4:[(45,54)],5:[(56,62),(70,74)],6:[(74,80)],
 7:[(95,105)],8:[(125,139)],9:[(146,156)],10:[(160,174)],11:[(198,212)],12:[(217,230)],
 13:[(251,257)],14:[(319,325)],15:[(327,329),(373,376)],16:[(355,360)],17:[(405,416)],18:[(416,423)]}
src = sys.argv[1]; r = PdfReader(src)
names = {int(os.path.basename(f)[:2]): os.path.splitext(os.path.basename(f))[0] for f in glob.glob('book-slices/pdf/*.pdf')}
for n, rngs in T.items():
    base = names[n]; w = PdfWriter(); txt = []
    for a, b in rngs:
        pa, pb = pdfpage(a), pdfpage(b)
        for p in range(pa-1, pb): w.add_page(r.pages[p])
        t = subprocess.run(['pdftotext','-f',str(pa),'-l',str(pb),'-layout',src,'-'],capture_output=True,text=True).stdout
        txt.append(f'=== PDF pages {pa}-{pb} (printed {a}-{b}) ===\n{t}\n')
    with open(f'book-slices/pdf/{base}.pdf','wb') as f: w.write(f)
    open(f'book-slices/txt/{base}.txt','w').write(''.join(txt))
    print(n, base, [(pdfpage(a), pdfpage(b)) for a,b in rngs])

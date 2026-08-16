# -*- coding: utf-8 -*-
import re, io
src = io.open(r"C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder\Nova Consulting\06 - Lean Six Sigma Initiative\07 - 6S Materials\6S Environment\Master\6S Success Home Edition\6s-home-reset-app-v2.jsx", encoding="utf-8").read()

def grab(name):
    m = re.search(r"const %s\s*=\s*" % name, src)
    i = src.index("[", m.end())
    depth = 0; instr = False; esc = False; q = None
    for j in range(i, len(src)):
        ch = src[j]
        if instr:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == q: instr = False
        else:
            if ch in "\"'": instr = True; q = ch
            elif ch == "[": depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return src[i:j+1]
    return None

for nm in ["ROOMS", "PRODUCTS", "BRIEFS"]:
    lit = grab(nm)
    io.open(nm + ".lit", "w", encoding="utf-8").write(lit)
    print(nm, "len", len(lit))

# -*- coding: utf-8 -*-
import re, io, zlib

PDF = (r"C:\Users\philk\Desktop\Process Kaizen\Process Kaizen\Work Folder\Nova Consulting"
       r"\06 - Lean Six Sigma Initiative\07 - 6S Materials\6S Environment\Master"
       r"\6S Success Home Edition\6S Home Reset Product Specification.pdf")
d = io.open(PDF, "rb").read()

def unesc(b):
    b = b.replace(b"\\(", b"(").replace(b"\\)", b")")
    b = b.replace(b"\\\\", b"\\")
    return b

out = []
for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", d, re.S):
    raw = m.group(1)
    try:
        s = zlib.decompress(raw)
    except Exception:
        continue
    for mm in re.finditer(rb"\[(.*?)\]\s*TJ|\((.*?)\)\s*Tj", s, re.S):
        if mm.group(1) is not None:
            parts = re.findall(rb"\((.*?)\)", mm.group(1))
            out.append(b"".join(unesc(p) for p in parts))
        else:
            out.append(unesc(mm.group(2)))
    out.append(b"\n")

text = b" ".join(out).decode("latin-1", "replace")
text = re.sub(r"[ ]{2,}", " ", text)
io.open("spec_pdf_text.txt", "w", encoding="utf-8").write(text)
print("chars:", len(text))
print(text[:3000])

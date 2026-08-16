# -*- coding: utf-8 -*-
"""Best-effort cleanup of the mojibake from the PDF text extraction."""
import io, re

t = io.open("spec_pdf_text.txt", encoding="utf-8").read()
# only the SAFE, unambiguous substitutions; ambiguous glyphs (!, %, $, #, the
# lost U+FFFD separators) are left for the writer agents to decode via a legend.
sub = {
    "Þ": "fi",
    "ß": "fl",
    "¥": "•",
    "¤": "§",
    "Ð": "-",
}
for k, v in sub.items():
    t = t.replace(k, v)
t = re.sub(r"[ ]{2,}", " ", t)
# strip the long run of trailing blank page numbers
t = re.sub(r"(\n\s*)+$", "\n", t)
io.open("spec_source.txt", "w", encoding="utf-8").write(t)
print("cleaned chars:", len(t))
print(t[:1200])

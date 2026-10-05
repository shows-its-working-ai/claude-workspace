"""Early Rising, Erased (cycle 269): an erasure poem. Every word of poem.txt must be found in source.txt (two
paragraphs of Mrs Beeton's Book of Household Management, 1861, public domain, from Project Gutenberg ebook 10136)
IN ORDER, each source word used at most once. Words are compared without case or punctuation. The build finds the
earliest matching word each time (greedy), which succeeds exactly when the poem is an in-order subsequence; if any
word can't be found the build FAILS and writes nothing. Writes index.html: the poem, and a 'show the page' view with
the kept words dark and the rest faded."""
import html, json, re, sys
from pathlib import Path
D = Path(__file__).resolve().parent
source = (D / "source.txt").read_text(encoding="utf-8")
poem = (D / "poem.txt").read_text(encoding="utf-8").strip("\n")
norm = lambda w: re.sub(r"[^a-z]", "", w.lower())
# split on whitespace AND on the em-dash "--" (Gutenberg's 'subject:--"I would' is one whitespace token, and hid the
# 'I'), keeping the separators so the page shows her text exactly as printed
parts = re.split(r"(\s+|--)", source.strip())
src = [p for k, p in enumerate(parts) if k % 2 == 0]   # words, punctuation attached; parts[odd] are the separators
want = [w for w in re.findall(r"\S+", poem)]
kept, i = [], 0
for w in want:
    while i < len(src) and norm(src[i]) != norm(w): i += 1
    if i == len(src): sys.exit(f"NOT AN ERASURE: '{w}' isn't in the source after word {kept[-1] if kept else 0}")
    kept.append(i); i += 1
print(f"erasure ok: {len(want)} poem words found in order among the source's {len(src)}; {len(src) - len(want)} erased")
page, keep = [], set(kept)
for k, tok in enumerate(src):
    page.append(f'<span class="k">{html.escape(tok)}</span>' if k in keep else html.escape(tok))
    if 2 * k + 1 < len(parts): page.append(" " if parts[2 * k + 1].isspace() else html.escape(parts[2 * k + 1]))
stanzas = "".join(f'<p class="verse">{html.escape(s)}</p>' for s in poem.split("\n\n"))
tpl = (D / "page_template.txt").read_text(encoding="utf-8")
out = tpl.replace("@@POEM@@", stanzas).replace("@@PAGE@@", "".join(page)).replace("@@KEPT@@", str(len(want))).replace("@@TOTAL@@", str(len(src)))
(D / "index.html").write_text(out, encoding="utf-8")
json.dump({"kept": kept, "n_source": len(src), "n_poem": len(want)}, open(D / "erasure.json", "w"))
print("built index.html")

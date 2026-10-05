"""Fact-check for writing/47-six-words.md. The history is checked against Wikipedia by tools/check_links.py (CITES);
this checks what the essay says about the form and about my own poem (writing/46): the 6-1-5-2-4-3 shuffle puts
every end-word in every one of the six positions over six stanzas; each word ends a line six times and appears again
in the envoi; the kettle is brought out in stanza 3, rinsed and hidden in stanza 5, found warm in stanza 6; the
quoted rain line is in the poem; the link to the poem works. Control: a shuffle that only swaps pairs (2,1,4,3,6,5)
does NOT visit every position, so the 'every position' check can fail."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
essay = " ".join((ROOT / "writing" / "47-six-words.md").read_text(encoding="utf-8").split())
poem = (ROOT / "writing" / "46-the-night-porter.md").read_text(encoding="utf-8").split("\n---\n", 1)[1]
stanzas = [b.strip() for b in poem.strip().split("\n\n")]
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
def visits(perm):   # does each word visit every position over six stanzas?
    order = list(range(6)); seen = {w: {i} for i, w in enumerate(order)}
    for _ in range(5):
        order = [order[j - 1] for j in perm]
        for i, w in enumerate(order): seen[w].add(i)
    return all(len(s) == 6 for s in seen.values())
check("essay describes the shuffle (last word first, then first, then fifth)", "The last word of one stanza becomes the first of the next, then the first comes second, the fifth third" in essay)
check("6-1-5-2-4-3 puts every word in every position", visits((6, 1, 5, 2, 4, 3)) and "every word has ended a line in every position" in essay)
pairs = visits((2, 1, 4, 3, 6, 5))
check("control: a pair-swapping shuffle does NOT", not pairs, "NOT SEEN" if pairs else "SEEN")
words = ["door", "light", "kettle", "hours", "rain", "home"]
ends = [re.findall(r"[a-z']+", l.lower())[-1] for st in stanzas[:6] for l in st.splitlines()]
envoi = stanzas[6].lower()
check("each word ends a line six times and is in the envoi ('seven times')", all(ends.count(w) == 6 and w in envoi for w in words) and "said seven times" in essay)
check("the kettle: out in stanza 3, rinsed and hidden in 5, found warm in 6",
      "out it comes" in stanzas[2] and "kettle" in stanzas[2] and "rinses the kettle" in stanzas[4] and "warm kettle" in stanzas[5])
check("the quoted rain line is in the poem", "It's only, after all, rain." in poem and "It's only, after all, rain." in essay)
check("the link to the poem points at a real page", "(46-the-night-porter.html)" in essay and (ROOT / "writing" / "46-the-night-porter.md").exists())
print("FACTCHECK OK" if ok else "FACTCHECK FAILED"); raise SystemExit(0 if ok else 1)

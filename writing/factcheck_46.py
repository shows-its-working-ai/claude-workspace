"""Form check for writing/46-the-night-porter.md, a sestina: six stanzas of six lines; the first stanza's end-words,
in order, are the six words; each later stanza's end-words are the previous stanza's taken in the order 6,1,5,2,4,3;
the three-line envoi contains all six words, each line ending on one and holding another inside it. Words are
compared without case or punctuation. Control: the same check on the poem with two lines of one stanza swapped
must FAIL, so it really reads the order."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "writing" / "46-the-night-porter.md").read_text(encoding="utf-8").split("\n---\n", 1)[1]
blocks = [[l.strip() for l in b.strip().split("\n") if l.strip()] for b in text.strip().split("\n\n")]
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
last = lambda line: re.findall(r"[a-z']+", line.lower())[-1]
def sestina(blocks):
    stanzas, envoi = blocks[:6], blocks[6] if len(blocks) > 6 else []
    if len(blocks) != 7 or any(len(s) != 6 for s in stanzas) or len(envoi) != 3: return False, "shape"
    order = [last(l) for l in stanzas[0]]
    if len(set(order)) != 6: return False, "first stanza repeats an end-word"
    for i in range(1, 6):
        order = [order[j - 1] for j in (6, 1, 5, 2, 4, 3)]
        got = [last(l) for l in stanzas[i]]
        if got != order: return False, f"stanza {i + 1}: {got} != {order}"
    words = set(order); ends = [last(l) for l in envoi]
    inner = [set(re.findall(r"[a-z']+", l.lower())[:-1]) & (words - {e}) for l, e in zip(envoi, ends)]
    if set(ends) - words or any(not w for w in inner): return False, "envoi"
    if words - set(ends) - set().union(*inner): return False, "envoi misses a word"
    return True, f"end-words {sorted(words)}"
good, why = sestina(blocks)
check("six stanzas turn 6-1-5-2-4-3, and the envoi holds all six words", good, why)
swapped = [b[:] for b in blocks]; swapped[3][0], swapped[3][1] = swapped[3][1], swapped[3][0]
bad, why2 = sestina(swapped)
check("control: two lines of stanza 4 swapped FAILS the check", not bad, f"{why2}  {'SEEN' if not bad else 'NOT SEEN'}")
print("FACTCHECK OK" if ok else "FACTCHECK FAILED"); raise SystemExit(0 if ok else 1)

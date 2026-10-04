"""Fact-check for writing/24-three-against-two.md: "long, short, short, long" is the gap pattern of 3 against 2 as
computed by art/16-against/against.py (sixths 0,2,3,4 -> gaps 2,1,1,2), and the order of hands the teacher gives
(both, right, left, right) matches which voice owns each beat, with the right hand playing three."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "24-three-against-two.md").read_text(encoding="utf-8").split())
on = json.loads((ROOT / "art" / "16-against" / "against.json").read_text(encoding="utf-8"))["3,2"]
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
L = 6; gaps = [b - a for a, b in zip(on, on[1:] + [L])]
words = ["long" if g == max(gaps) else "short" for g in gaps]
check(f"gaps {gaps} read as '{', '.join(words)}'", "long, short, short, long" in s and words == ["long", "short", "short", "long"])
owner = ["both" if t % 2 == 0 and t % 3 == 0 else "right" if t % 2 == 0 else "left" for t in on]   # right = 3 beats (every 2 sixths)
check(f"hands in order {owner}", owner == ["both", "right", "left", "right"]
      and "Both hands on the first one. Then the right. Then the left. Then the right." in s)
# cycle 164: the first draft tapped "Tap. Tap-tap. Tap." and this check didn't exist to catch it. Group beats by gap:
# a long gap ends a group, short gaps join taps with hyphens.
groups, g = [], ["Tap"]
for gap in gaps:
    if gap == max(gaps): groups.append("-".join(g)); g = ["tap"]
    else: g.append("tap")
taps = " ".join(x[0].upper() + x[1:] + "." for x in groups)
check(f"the taps written as {taps!r}", f"She tapped the lid of the piano with one finger. {taps}" in s)
check("right hand plays three, left two", "The right hand played three notes" in s and "the left hand played two" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

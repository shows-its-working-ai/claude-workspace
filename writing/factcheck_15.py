"""Fact-check for writing/15-the-extent.md: every ringing claim is recomputed from the place notation (ringing_15.py)."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D))
from ringing_15 import ring, BOB, HUNT
s = (D / "15-the-extent.md").read_text(encoding="utf-8")
body = " ".join(s.split("### The numbers, checked")[0].split())        # one line, so wrapped phrases still match
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
bob = ring(BOB, 3); rows = ["1234"] + bob
pos = lambda bell, rs: [r.index(bell) + 1 for r in rs]
check("24 orders; extent rings each once, round at the 24th", "can come in twenty-four orders" in body
      and len(bob) == 24 and len(set(bob)) == 24 and bob[-1] == "1234" and "1234" not in bob[:-1]
      and "it was the twenty-fourth change, and nothing had been rung twice" in body)
check("never more than one place per change", "Never more than one" in body
      and all(abs(a.index(b) - c.index(b)) <= 1 for a, c in zip(rows, rows[1:]) for b in "1234"))
check("treble: lead, 2, 3, 4, 4, 3, 2, lead, lead; eight changes a lead; three leads",
      pos("1", rows[:9]) == [1, 2, 3, 4, 4, 3, 2, 1, 1] and "lead, second, third, fourth, fourth again, back down, lead, lead" in body
      and "Eight changes and she's home" in body and "Three leads is the extent" in body and len(BOB) == 8)
check("lead ends 1342, 1423, rounds", (bob[7], bob[15], bob[23]) == ("1342", "1423", "1234")
      and "one-three-four-two, then one-four-two-three, then rounds" in body)
check("the third makes seconds at the first lead end (row 7 has 3 in 2nd; 12 keeps it there)",
      rows[7][1] == "3" and bob[7][1] == "3" and "the third was the bell in seconds place" in body)
check("without the kink, it hunts UP (into thirds) and the second comes down into seconds",
      ring(BOB[:7] + ["14"], 1)[-1] == "1234" and rows[7].index("3") == 1 and "1234".index("3") == 2
      and "the third went on up into thirds" in body and "The second came down into the place she'd left" in body
      and "makes seconds instead of hunting up" in body)
check("plain hunt: round after 8 changes", ring(HUNT, 1)[-1] == "1234" and len(set(ring(HUNT, 1))) == 8
      and "eight changes and back to rounds" in body and "Rounds. Eight changes in." in body and "Plain hunt, 8 changes" in body)
check("third's first lead: up to the back, two blows there, down to lead, led twice, up again",
      pos("3", rows[:9]) == [3, 4, 4, 3, 2, 1, 1, 2, 2] and "lay there for two blows" in body)
check("second lead end dodge: second and tenor at the back swap (1324 -> 1342)", rows[7][2:] == "24" and bob[7][2:] == "42"
      and "the second and the tenor dodged" in body)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

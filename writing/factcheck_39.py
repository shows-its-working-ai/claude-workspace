"""Fact-check for writing/39-notes-on-the-fridge.md: the yoghurt count goes four -> (one eaten by Monday's note) ->
two -> one -> none, one a night, so four pots in total, and the four pots Dee finds == the four that went missing."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "39-notes-on-the-fridge.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
W = {"no": 0, "one": 1, "two": 2, "three": 3, "four": 4}
days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
start = W[re.search(r"There were (\w+)\.", s)[1].lower()]
left = [W[re.search(p, s.split(f"**{d}**")[1])[1].lower()] for d, p in zip(days[1:], [r"(\w+) yoghurts left", r"(\w+) yoghurt\.", r"(\w+) yoghurts\."])]
check("Monday: there were four; one already gone (someone 'keeps eating' them)", start == 4 and "who keeps eating my yoghurts" in s)
seq = [start - 1] + left
check("one a night: 3, 2, 1, 0 left by Mon..Thu", seq == [3, 2, 1, 0], str(seq))
found = W[re.search(r"(\w+) of them, and a spoon", s)[1].lower()]
check("Dee finds as many pots as went missing (and the lids line up)", found == start - seq[-1] == 4 and "You opened four lids" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

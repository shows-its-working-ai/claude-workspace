"""Fact-check for writing/25-folds.md: every number and crease claim recomputed from art/17-dragon/dragon.json (the
creases the Paper Dragon page is tested against): one fold one crease, two folds three; 65,535 creases and 65,536
lengths at sixteen; corners touched twice at sixteen == 28,555 and none three times."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "25-folds.md").read_text(encoding="utf-8").split())
cr = json.loads((ROOT / "art" / "17-dragon" / "dragon.json").read_text(encoding="utf-8"))
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
check("one fold, one crease; two folds, three", len(cr["1"]) == 1 and len(cr["2"]) == 3 and "One fold, one crease. Two folds, three." in s)
check("sixteen folds: 65,535 creases", len(cr["16"]) == 65535 and "65,535 of them" in s)
check("...and 65,536 short lengths", len(cr["16"]) + 1 == 65536 and "65,536 short lengths" in s)
x = y = 0; dx, dy = 1, 0; v = {(0, 0): 1}
for c in cr["16"] + "E":
    x += dx; y += dy; v[(x, y)] = v.get((x, y), 0) + 1
    if c == "L": dx, dy = -dy, dx
    elif c == "R": dx, dy = dy, -dx
twice, more = sum(n == 2 for n in v.values()), sum(n > 2 for n in v.values())
check(f"corners touched twice at sixteen == {twice:,}", f"{twice:,} times, at sixteen folds" in s)
check("never three times", more == 0 and "Never three times." in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

"""Fact-check for writing/40-eight-of-thirteen.md: the eight named games are real folders among the last thirteen
in projects/ (16-28 when written: checked at the essay's commit); the cycle-213 note and its correction (The Lock
happens on summer evenings, never 'night'); the rule (231) and Folded Poem as the first thing after it; three issues
in twenty minutes and 'more than a hundred' checks (essay 33 says about a hundred and thirty)."""
import re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "40-eight-of-thirteen.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
TITLE = {"Nim": "16-nim", "Corner the Queen": "17-queen", "Small Hex": "20-hex", "Nobody Wins Noughts": "23-notakto",
         "Four Boxes": "24-boxes", "Poisoned Chocolate": "25-chomp", "No Triangles": "26-sim", "Skittles": "28-kayles"}
added = (subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", "writing/40-eight-of-thirteen.md"], cwd=ROOT,
         capture_output=True, text=True).stdout.split() or ["HEAD"])[-1]
tree = subprocess.run(["git", "ls-tree", "--name-only", f"{added}:projects"], cwd=ROOT, capture_output=True, text=True).stdout.split() if added != "HEAD" else sorted(p.name for p in (ROOT / "projects").iterdir() if p.is_dir())
last13 = sorted(tree, key=lambda d: int(d.split("-")[0]))[-14:-1] if added != "HEAD" else sorted(tree, key=lambda d: int(d.split("-")[0]))[-14:-1]
# at the essay's commit the newest folder is 29-folded (made after the rule); the thirteen BEFORE it are 16..28
check("the eight named games are folders among the thirteen before the rule", all(v in last13 for v in TITLE.values()) and len(last13) == 13
      and all(t in s for t in TITLE), str(last13[:2]) + "...")
for name, d in TITLE.items():
    t = (ROOT / "projects" / d / "index.html").read_text(encoding="utf-8")
    check(f"  {name} is that page's title", f"<title>{name}</title>" in t)
check("'eight' and 'thirteen'", "Of the last thirteen things in my games-and-puzzles folder, eight were the same thing" in s)
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
sec = lambda n: " ".join(j.split(f"## Cycle {n} - ")[1].split("\n## ")[0].split()) if f"## Cycle {n} - " in j else ""
check("cycle 213 noted the stories pattern (galley, bakery, lock, bridge)", all(w in sec(213) for w in ("night shifts", "galley", "bakery", "lock", "bridge")) and "At cycle 213" in s)
lock = (ROOT / "writing" / "23-the-lock.md").read_text(encoding="utf-8").lower()
check("The Lock: summer evenings, no 'night' anywhere (the correction)", "summer" in lock and "evening" in lock and "night" not in lock and "happens on summer evenings" in s)
check("rule (231) is written; Folded Poem (232) came first after it", "(231) Before choosing the next thing, list the last ten" in j and "Folded Poem" in sec(232)
      and "first non-solved-game after rule 231" in sec(232) and "folded-paper poem" in s)
e33 = " ".join((ROOT / "writing" / "33-twenty-minutes.md").read_text(encoding="utf-8").split())
check("three issues in twenty minutes; more than a hundred checks", "three issues in twenty minutes" in e33 and "about a hundred and thirty run" in e33
      and "three bug reports in twenty minutes" in s and "more than a hundred of my checks" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

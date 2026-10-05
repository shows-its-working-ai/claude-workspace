"""Fact-check for writing/35-the-bug-that-changed-nothing.md: the survivor and its replacement are in cycle 210's
journal section (equivalent, 4% at desktop width, half size at phone width); the page's pick() comment no longer says
'smallest'; mutate.py no longer carries the equivalent mutant and does carry the unscaled-click one; apollo.py still
says no two circles overlap; the test really does a mouse click at phone width."""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "35-the-bug-that-changed-nothing.md").read_text(encoding="utf-8").split())
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8"); sec = " ".join(j.split("## Cycle 210 - ")[1].split("\n## ")[0].split()) if "## Cycle 210 - " in j else ""
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
check("cycle 210: the biggest/smallest mutant survived and was EQUIVALENT", "SURVIVED" in sec and "EQUIVALENT mutant" in sec
      and "At cycle 210, one survived." in s and "equivalent mutant" in s)
check("cycle 210: the replacement survived at desktop width, 4% smaller", "ALSO survived at desktop width" in sec and "only 4% smaller" in sec
      and "only 4% smaller" in s)
check("cycle 210: caught at phone width, half size", "half size" in sec and "about half size" in s)
page = (ROOT / "art/24-apollonian/index.html").read_text(encoding="utf-8")
check("the page's pick comment now says the circles never overlap", "inner circles never overlap" in page and "the smallest circle containing" not in page)
m = (ROOT / "tools/mutate.py").read_text(encoding="utf-8")
check("mutate.py: equivalent mutant gone, unscaled-click mutant present", "picks the biggest circle" not in m and "forgets the canvas is scaled on screen" in m)
t = (ROOT / "art/24-apollonian/test.py").read_text(encoding="utf-8")
check("test.py: a real mouse click, after the phone-width resize", "pg.mouse.click" in t and t.index('"width": 390') < t.index("pg.mouse.click"))
out = subprocess.run([sys.executable, str(ROOT / "art/24-apollonian/apollo.py")], capture_output=True, text=True).stdout
check("apollo.py: no two circles overlap", "(c) no two circles overlap, all inside the outer one: True" in out and "never overlap" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

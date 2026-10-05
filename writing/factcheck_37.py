"""Fact-check for writing/37-a-year-off.md: the three quoted page sentences really were on the pages before cycle 217
(checked in git at the commit before 217's), the two corrected dates are on the pages now, 'seven' and 'five right, two
a year off' are in cycle 217's journal, the cited phrase is in check_links' CITES, and the two side-claims
(181,440 layouts; twenty-two minutes) are on their pages."""
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "37-a-year-off.md").read_text(encoding="utf-8").split())
git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
fix = (git("log", "--format=%H", "-S", "noticed in 2004 (and", "--", "art/15-rhythm/index.html").split() or [""])[-1]
before = lambda f: " ".join(git("show", f"{fix}~1:{f}").split())
check("the three quotes were on the pages before the fix", fix and "The rule is Descartes' (1643)." in before("art/24-apollonian/index.html")
      and "Euler described it in 1736" in before("projects/21-stroke/index.html") and "Donald Knuth's 1977 rule" in before("projects/18-mastermind/index.html")
      and all(q in s for q in ['"The rule is Descartes\' (1643)."', '"Euler described it in 1736."', '"Donald Knuth\'s 1977 rule."']))
now = lambda f: " ".join((ROOT / f).read_text(encoding="utf-8").split())
check("the pages now say 2004 (Toussaint) and 1976 (Knuth)", "noticed in 2004" in now("art/15-rhythm/index.html") and "from 1976" in now("projects/18-mastermind/index.html")
      and "He found it in 2004 and published in 2005" in s and "a paper dated 1976" in s)
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8"); sec = " ".join(j.split("## Cycle 217 - ")[1].split("\n## ")[0].split()) if "## Cycle 217 - " in j else ""
check("journal 217: seven claims, two a year off, five right", "seven historical claims" in sec and "Two were a year off" in sec and "The other five were right" in sec
      and "turned up seven of these" in s and "Five were right. Two were a year off." in s)
check("the quoted phrase is one check_links checks", '"in 2004 and is described in a 2005 paper"' in (ROOT / "tools/check_links.py").read_text(encoding="utf-8")
      and 'says "in 2004 and is described in a 2005 paper"' in s)
check("side claims: 181,440 layouts; twenty-two minutes", "181,440" in now("projects/19-eight/index.html") and "181,440" in s
      and "twenty-two minutes" in now("writing/34-the-night-bridge.md") and "twenty-two minutes" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

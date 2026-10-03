"""Fact-check for writing/10-what-the-summary-hid.md: every quoted phrase in its fact-check list must appear verbatim
in JOURNAL.md, and the essay's numbers must agree with the journal's."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "writing" / "10-what-the-summary-hid.md").read_text(encoding="utf-8")
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name}")
fc = s.split("### Fact-check")[1]
quotes = [q.replace('\\"', '"') for q in re.findall(r'"((?:[^"\\]|\\")+)"', fc)]
missing = [q for q in quotes if q not in j]
check(f"{len(quotes)} quoted phrases all in the journal {missing or ''}", not missing)
check("1,735 vs 9 seeds; 8 per 30 vs 4 per 15", "1,735 seeds" in s and "9 seeds" in s and "(30,-8) 1,735 seeds" in j and "(15,-4) 9 seeds" in j)
check("B-bar: 6 cells every 12 steps, one seed", "6 cells every 12 steps" in s and "(12,-6) ONE seed" in j)
check("pair fifteen cells apart (295 - 280)", "fifteen cells apart" in s and "offsets 295 and 280" in j and 295 - 280 == 15)
check("2,000 then 20,000 samples; 0.1%", "2,000 random grids" in s and "20,000 per setting" in s and "0.1% good at 16%" in j and "Reran at 20,000 per density" in j)
check("'about forty cycles' (cycle 31 -> 75)", "about forty cycles" in s and 40 <= 75 - 31 <= 45)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

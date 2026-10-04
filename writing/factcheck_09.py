"""Fact-check for writing/09-three-corrections.md: each factual claim in the poems is checked against the journal,
the published catalogue numbers and the earlier story. The poem text must still contain each claim."""
from fractions import Fraction as Fr
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = (ROOT / "writing" / "09-three-corrections.md").read_text(encoding="utf-8")
j = (ROOT / "JOURNAL.md").read_text(encoding="utf-8")
story = (ROOT / "writing" / "08-the-rating-nut.md").read_text(encoding="utf-8")
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name}")
check("E-bar: 8 left every 30; E: 4 every 15; same speed",
      "Every thirty steps it moved eight cells left" in s and "E moves four every fifteen" in s and Fr(-8, 30) == Fr(-4, 15)
      and "period 30, shift -8" in j and "move -4 per **15** steps" in j)
check("'half as often' = period 30 vs 15", "half as often" in s and 15 * 2 == 30)
first = j.index("## Cycle 22 "); fix = j.index("## Cycle 64 ")
check("named E from cycle 22 to 64 ('forty cycles' ~ 42)", "For forty cycles" in s and first < fix and 38 <= 64 - 22 <= 45)
check("C pair ~15 cells apart (offsets 295 and 280)", "fifteen cells apart" in s and "offsets 295 and 280" in j and 295 - 280 == 15)
check("lone C3 in 9 seeds; lone C1 in none", "One I found nine times." in s and "The other, not once." in s
      and "lone C3 9" in j and "**No lone C1.**" in j)
check("rating nut: rate not time; a minute and a half", "a minute and a half" in s and "minute and a half" in story
      and "changes the RATE, not the time already lost" in j)
# cycle 178: the published "what the poems claim, checked" paragraph was itself unchecked (a planted 30 -> 31 survived)
summ = " ".join(s.split("### What the poems claim, checked")[1].split())
check("the checked paragraph states the same numbers",
      "moves 8 cells left every 30 steps, E moves 4 every 15" in summ and Fr(-8, 30) == Fr(-4, 15)
      and f"cycle 22 to cycle 64, a span of {64 - 22} cycles" in summ and "about 15 cells apart" in summ and 295 - 280 == 15
      and "a lone C3 turned up in 9 seeds and a lone C1 in none" in summ)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

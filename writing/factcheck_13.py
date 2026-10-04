"""Fact-check for writing/13-the-log.md: the story's numbers must agree with each other and still be stated.
Mutation-tested in the same cycle (change a time or the flash count -> FACTCHECK FAILED)."""
from pathlib import Path
s = (Path(__file__).resolve().parent / "13-the-log.md").read_text(encoding="utf-8")
body = s.split("### The numbers, checked")[0]
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name}")
mins = lambda hhmm: int(hhmm[:2]) * 60 + int(hhmm[3:])
per_min = 2 * 60 // 10                                               # Fl(2) 10s: two flashes per ten seconds
check("Fl(2) 10s stated, and = two flashes every ten seconds", "*Fl(2) 10s*" in body and "two white flashes every ten seconds" in body)
check("outage >= 03:14..03:20 = 6 min x 12 = 72 'seventy-two flashes'", "seventy-two flashes" in body and "forty-eight" not in body
      and (mins("03:20") - mins("03:14")) * per_min == 72)
check("silence 03:14 -> top 03:16 = 'Two minutes on the stairs'", "at 03:14" in body and "03:16" in body and "Two minutes on the stairs" in body and mins("03:16") - mins("03:14") == 2)
check("03:16 -> 03:20 = 'four on the belt' = 'in four minutes'", "four on the belt" in body and "in four minutes" in body and mins("03:20") - mins("03:16") == 4)
check("log line starts at 03:14 (heard), not 03:16 (repair start)", "*03:14 (when heard; may have stopped earlier) to 03:20" in body
      and "rotation restored 03:20" in body and "*03:16 to" not in body)
check("1953 outage 21:40-21:52 stated", "21:40 to 21:52" in body and mins("21:52") - mins("21:40") == 12)
check("ninety-six steps; eleven keepers (consistent wherever repeated)", body.count("ninety-six steps") == 1 and "eleven keepers" in body)
# cycle 178: the published "numbers, checked" paragraph was itself unchecked (a planted 12 -> 10 survived)
summ = " ".join(s.split("### The numbers, checked")[1].split())
check("the checked paragraph states the same numbers",
      f"so {per_min} flashes a minute and 4 minutes is {4 * per_min} flashes but 6 minutes is {6 * per_min}" in summ
      and "two minutes for ninety-six steps" in summ and mins("21:52") - mins("21:40") == 12 and "is twelve minutes" in summ)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

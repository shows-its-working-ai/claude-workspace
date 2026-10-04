"""Fact-check for writing/11-the-count.md: the story's numbers must agree with each other, and the story must still
state each one (so an edit can't silently break the arithmetic)."""
from pathlib import Path
s = (Path(__file__).resolve().parent / "11-the-count.md").read_text(encoding="utf-8")
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name}")
system, sold, counted, behind = 40, 12, 32, 4
check("system says forty; Mrs Okafor bought twelve", "The system said forty" in s and "Mrs Okafor bought twelve" in s)
check("expected on shelf = 40 - 12 = 28", "Should\nbe twenty-eight on the shelf" in s and system - sold == 28)
check("counted thirty-two -> four too many", "got thirty-two" in s and "four tubs too many" in s and counted - (system - sold) == 4)
check("four returned tubs, shelved: they ARE the four extra", "four tubs of white" in s and "Four of them had a dent" in s
      and system - sold + behind == counted)
check("Ruth's note: 32 = 40 - 12 + 4; Sami says thirty-two; no stale thirty-six",
      "32 on floor = 40 in system - 12 sold on account + 4 returned" in s and '"Thirty-two," said Sami.' in s and '"Thirty-six," said Sami' not in s)
check("'eight missing' was Sami's first, wrong reading (40 - 32)", "Eight missing" in s and system - counted == 8)
check("hinges: twelve in the bin + two on the floor = fourteen", '"Twelve," she said.' in s and "I put fourteen" in s and 12 + 2 == 14)
check("delivery Thursday of twenty tubs is consistent (does not change the sums)", "Thursday. Twenty tubs." in s)
order = [s.index(t) for t in ("At half eleven", "at ten to one", "at half past two")]
check("times appear in order", order == sorted(order))
# cycle 178: the published "arithmetic, checked" paragraph was itself unchecked (a planted 32 -> 33 survived)
summ = " ".join(s.split("### The arithmetic, checked")[1].split())
want = (f"{system} in the system, {sold} sold on account and not yet reported, so {system} − {sold} = {system - sold} expected; "
        f"{counted} counted, so {counted} − {system - sold} = {counted - (system - sold)} extra, which are the {behind} returned tubs")
check("the checked paragraph states the same arithmetic", want in summ and f"{system} − {sold} + {behind} = {counted}" in summ)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

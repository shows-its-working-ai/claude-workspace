"""Fact-check for writing/41-the-marrow.md: both marrows weigh 12 kg; the slices (200 g and 100 g) leave 11.8 and
11.9, so the SECOND is now the heaviest and wins first prize; the third marrow (4 kg) is lighter than both; my first
draft's 'denser' was backwards (the lighter equal slice means the LESS dense end), so the word mustn't come back."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "41-the-marrow.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
W = {"Eleven point eight": 11.8, "Eleven point nine": 11.9, "Two hundred grams": 0.2, "One hundred grams": 0.1}
check("both marrows 12 kg", s.count('"Twelve kilos,"') == 4)
check("12 - 0.2 = 11.8 and 12 - 0.1 = 11.9, as Hen reads them", all(k in s for k in W) and abs(12 - 0.2 - 11.8) < 1e-9 and abs(12 - 0.1 - 11.9) < 1e-9
      and s.index("Two hundred grams") < s.index("One hundred grams") and s.index('"Eleven point eight," she said, of the first') > 0)
check("the second is heaviest after slicing, and wins first prize", 11.9 > 11.8 and "first prize went to the second marrow" in s and "Second prize went to the first" in s)
check("the third marrow (4 kg) is lighter than both", "marrow of four kilos" in s and 4 < 11.8)
check("no 'denser' (it was backwards: the lighter slice means the less dense end)", "denser" not in s)
judges = [j for j in ("Mrs Adeyemi", "Mr Pask", "Bernard", "Lorna", "Hen") if j in s]
check("five judges, and five are named", "had five judges" in s and len(judges) == 5, str(judges))
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")

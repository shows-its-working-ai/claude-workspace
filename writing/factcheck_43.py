"""Fact-check for writing/43-the-coat.md: the section years run strictly BACKWARDS and the coat is bought in the last
(earliest) one; the funeral ("three years" before 2019) falls after Walter is last seen alive (2011); the daughter is
born after the coat was bought, and old enough to have a school-age child by 2011 (born >= 20 years before her
child, the child >= 5 in 2011); the three things in the pockets at the end are the three put there in the story,
and the button is NOT in the pocket."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
s = " ".join((ROOT / "writing" / "43-the-coat.md").read_text(encoding="utf-8").split())
ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")
years = [int(y) for y in re.findall(r"\*\*(\d{4})\.\*\*", s)]
check("section years run strictly backwards", years == sorted(years, reverse=True) and len(set(years)) == len(years), str(years))
check("the coat is bought in the earliest section", "buys the coat" in s.split(f"**{min(years)}.**")[1])
funeral = 2019 - 3
check("funeral (2019 - three years = 2016) comes after Walter's last scene (2011)", "for three years now, since the funeral" in s and 2011 < funeral < 2019)
born = int(re.search(r"\*\*(\d{4})\.\*\* A pencil", s)[1])
check("daughter born after the coat (1979), and a school-age grandchild by 2011 is possible", "their daughter was born" in s and 1979 < born and born + 20 + 5 <= 2011, str(born))
end = s.split("In the pockets, when the girl tried it on:")[1]
check("the pockets at the end hold exactly receipt, pencil, stone (all put there earlier)", all(w in end for w in ("receipt for bread", "half a pencil", "a stone with a white line"))
      and "receipt for bread" in s.split("**2019.**")[1] and "half-used" in s and "white line round it and drops it into the pocket" in s)
check("and the button is not in the pocket (it's in the caretaker's jar)", "The button was somewhere else, in a jam jar" in end and "keeps it in a jam jar" in s)
print("FACTCHECK OK" if ok else "FACTCHECK FAILED")
